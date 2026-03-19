import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt
class BulkCargo(Document):
    def validate(self):
        """Called on Save; calculate totals but allow empty child table"""
        self.calculate_totals()
        self.validate_billing_volume()

    def before_save(self):
        """Ensure totals are updated before saving"""
        self.calculate_totals()

    def on_submit(self):
        """Prevent submission if child table is empty or missing required fields"""
        if not self.cargo_trips:
            frappe.throw(_("Cannot submit Bulk Cargo without Cargo Trips."))

        for trip in self.cargo_trips:
            if not trip.truck_number:
                frappe.throw(_("Truck Number is required in all Cargo Trips."))
            if trip.loaded_volume is None:
                frappe.throw(_("Loaded Volume is required in all Cargo Trips."))

    def calculate_totals(self):
        """Calculate totals from cargo trips"""
        if not self.cargo_trips:
            self.total_capacity = 0
            self.total_loaded_volume = 0
            self.total_offloaded_volume = 0
            self.total_loss = 0
            self.remained_capacity = flt(self.fuel_capacity or 0)
            return

        total_capacity = 0
        total_loaded_volume = 0
        total_offloaded_volume = 0
        total_loss = 0

        for trip in self.cargo_trips:
            trip.truck_capacity = flt(trip.truck_capacity or 0)
            trip.loaded_volume = flt(trip.loaded_volume or 0)
            trip.offloaded_volume = flt(trip.offloaded_volume or 0)

            # Calculate loss as simple difference
            trip.loss = max(0, trip.loaded_volume - trip.offloaded_volume)

            total_capacity += trip.truck_capacity
            total_loaded_volume += trip.loaded_volume
            total_offloaded_volume += trip.offloaded_volume
            total_loss += trip.loss

        self.total_capacity = total_capacity
        self.total_loaded_volume = total_loaded_volume
        self.total_offloaded_volume = total_offloaded_volume
        self.total_loss = total_loss
        self.remained_capacity = flt(self.fuel_capacity or 0) - total_capacity

    def validate_billing_volume(self):
        """Ensure billing option is valid"""
        if self.billing_on and self.billing_on not in ["Loaded Volume", "Offloaded Volume"]:
            frappe.throw(_("Invalid billing option selected"))


# ------------------- API Methods -------------------

@frappe.whitelist()
def create_cargo_registration(**kwargs):
    """Create Cargo Registration from Bulk Cargo trip"""
    try:
        required_fields = [
            "customer", "trip_route", "rate", "cargo_type", "truck_capacity",
            "number_of_packages", "cargo_location_country", "cargo_location_city",
            "loading_date", "cargo_destination_country", "cargo_destination_city",
            "expected_offloading_date"
        ]
        for field in required_fields:
            if not kwargs.get(field):
                frappe.throw(_(f"Missing required field: {field}"))

        cargo_registration = frappe.new_doc("Cargo Registration")
        cargo_registration.customer = kwargs.get("customer")
        cargo_registration.posting_date = kwargs.get("posting_date") or nowdate()
        cargo_registration.transport_type = "Internal"  # Set as Internal

        # Child table row
        cargo_detail = {
            "cargo_type": kwargs.get("cargo_type"),
            "cargo_route": kwargs.get("trip_route"),
            "net_weight": flt(kwargs.get("truck_capacity")),
            "rate": flt(kwargs.get("rate")),
            "service_item": kwargs.get("service_item"),
            "number_of_packages": kwargs.get("number_of_packages") or 1,
            "cargo_location_country": kwargs.get("cargo_location_country"),
            "cargo_location_city": kwargs.get("cargo_location_city"),
            "loading_date": kwargs.get("loading_date"),
            "cargo_destination_country": kwargs.get("cargo_destination_country"),
            "cargo_destination_city": kwargs.get("cargo_destination_city"),
            "expected_offloading_date": kwargs.get("expected_offloading_date"),
        }

        cargo_registration.append("cargo_details", cargo_detail)
        cargo_registration.insert(ignore_permissions=True)

        return {"status": "success", "name": cargo_registration.name}

    except Exception as e:
        frappe.log_error(f"Error creating Cargo Registration: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def create_sales_invoice(name):
    """Create Sales Invoice from Bulk Cargo"""
    try:
        bulk_cargo = frappe.get_doc("Bulk Cargo", name)

        if bulk_cargo.sales_invoice_id:
            return {"status": "error", "message": f"Sales Invoice already exists: {bulk_cargo.sales_invoice_id}"}

        if not bulk_cargo.billing_on:
            frappe.throw(_("Please select a Billing Option"))
        if not bulk_cargo.service_item:
            frappe.throw(_("Service Item is required"))
        if not bulk_cargo.customer_name:
            frappe.throw(_("Customer is required"))

        billing_volume = bulk_cargo.total_loaded_volume if bulk_cargo.billing_on == "Loaded Volume" else bulk_cargo.total_offloaded_volume
        if billing_volume <= 0:
            frappe.throw(_("Billing volume must be greater than zero"))

        rate = flt(bulk_cargo.rate)
        if rate <= 0:
            frappe.throw(_("Rate must be greater than zero"))

        invoice_amount = billing_volume * rate
        items = [{
            "item_code": bulk_cargo.service_item,
            "qty": billing_volume,
            "rate": rate,
            "amount": invoice_amount,
            "description": f"Billing based on {bulk_cargo.billing_on}: {billing_volume} units at {rate} per unit"
        }]

        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": bulk_cargo.customer_name,
            "currency": frappe.defaults.get_global_default("currency"),  # <-- fixed here
            "posting_date": nowdate(),
            "company": bulk_cargo.company,
            "items": items
        })

        sales_invoice.insert(ignore_permissions=True)
        sales_invoice.save()

        bulk_cargo = frappe.get_doc("Bulk Cargo", name)
        bulk_cargo.sales_invoice_id = sales_invoice.name
        bulk_cargo.save(ignore_permissions=True)

        return {"status": "success", "invoice_name": sales_invoice.name, "rate": rate}

    except Exception as e:
        frappe.log_error(f"Error creating Sales Invoice: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_truck_capacity(truck_name, cargo_type):
    """Get capacity for a specific truck and cargo type"""
    try:
        truck = frappe.get_doc("Truck", truck_name)
        if not truck.compartment_details:
            return {"status": "error", "message": "No compartments found"}
        for comp in truck.compartment_details:
            if comp.cargo == cargo_type:
                return {"status": "success", "capacity": flt(comp.capacity)}
        return {"status": "error", "message": f"No compartment found for cargo type: {cargo_type}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_bulk_cargo_summary(name):
    """Return summary totals for parent"""
    try:
        bulk_cargo = frappe.get_doc("Bulk Cargo", name)
        return {
            "status": "success",
            "data": {
                "total_capacity": bulk_cargo.total_capacity,
                "total_loaded_volume": bulk_cargo.total_loaded_volume,
                "total_offloaded_volume": bulk_cargo.total_offloaded_volume,
                "total_loss": bulk_cargo.total_loss,
                "remained_capacity": bulk_cargo.remained_capacity,
                "cargo_trips_count": len(bulk_cargo.cargo_trips),
                "sales_invoice_id": bulk_cargo.sales_invoice_id
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
