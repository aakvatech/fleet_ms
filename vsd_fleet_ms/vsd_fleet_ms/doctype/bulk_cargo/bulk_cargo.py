# Copyright (c) 2024, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
import traceback
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt

class BulkCargo(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_billing_volume()
    
    def before_save(self):
        self.calculate_totals()
    
    def calculate_totals(self):
        """Calculate all totals from cargo trips"""
        total_capacity = 0
        total_loaded_volume = 0
        total_offloaded_volume = 0
        total_loss = 0
        
        for trip in self.cargo_trips:
            total_capacity += flt(trip.truck_capacity)
            total_loaded_volume += flt(trip.loaded_volume)
            total_offloaded_volume += flt(trip.offloaded_volume)
            total_loss += flt(trip.loss)
        
        self.total_capacity = total_capacity
        self.total_loaded_volume = total_loaded_volume
        self.total_offloaded_volume = total_offloaded_volume
        self.total_loss = total_loss
        
        # Calculate remained capacity
        if self.fuel_capacity:
            self.remained_capacity = flt(self.fuel_capacity) - total_capacity
    
    def validate_billing_volume(self):
        """Validate billing volume selection"""
        if self.billing_on and self.billing_on not in ["Loaded Volume", "Offloaded Volume"]:
            frappe.throw(_("Invalid billing option selected"))

@frappe.whitelist()
def create_cargo_registration(**kwargs):
    """Create Cargo Registration from Bulk Cargo trip data"""
    try:
        # Get arguments from kwargs
        customer = kwargs.get('customer')
        trip_route = kwargs.get('trip_route')
        posting_date = kwargs.get('posting_date')
        rate = kwargs.get('rate')
        cargo_type = kwargs.get('cargo_type')
        truck_capacity = kwargs.get('truck_capacity')
        
        # Validate required fields
        if not all([customer, trip_route, rate, cargo_type]):
            frappe.throw(_("Missing required fields for Cargo Registration"))
        
        # Create Cargo Registration
        cargo_registration = frappe.new_doc("Cargo Registration")
        cargo_registration.customer = customer
        cargo_registration.posting_date = posting_date or nowdate()
        cargo_registration.transport_type = "Bulk Cargo"
        
        # Add cargo details
        cargo_detail = {
            "cargo_type": cargo_type,
            "cargo_route": trip_route,
            "net_weight": flt(truck_capacity),
            "rate": flt(rate),
            "service_item": kwargs.get('service_item'),
            "cargo_destination_country": kwargs.get('cargo_destination_country'),
            "cargo_destination_city": kwargs.get('cargo_destination_city'),
            "expected_offloading_date": kwargs.get('expected_offloading_date'),
            "cargo_location_country": kwargs.get('cargo_location_country'),
            "cargo_location_city": kwargs.get('cargo_location_city'),
            "loading_date": kwargs.get('loading_date')
        }
        
        cargo_registration.append("cargo_details", cargo_detail)
        cargo_registration.insert(ignore_permissions=True)
        
        return {
            "status": "success",
            "name": cargo_registration.name,
            "message": f"Cargo Registration {cargo_registration.name} created successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating Cargo Registration: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def create_sales_invoice(name):
    """Create Sales Invoice from Bulk Cargo"""
    try:
        # Fetch Bulk Cargo document
        bulk_cargo = frappe.get_doc("Bulk Cargo", name)
        
        # Check if Sales Invoice already exists
        if bulk_cargo.sales_invoice_id:
            return {
                "status": "error",
                "message": f"Sales Invoice already exists: {bulk_cargo.sales_invoice_id}"
            }
        
        # Validate billing requirements
        if not bulk_cargo.billing_on:
            frappe.throw(_("Please select a Billing Option (Loaded Volume or Offloaded Volume)"))
        
        if not bulk_cargo.service_item:
            frappe.throw(_("Service Item is required"))
        
        if not bulk_cargo.customer_name:
            frappe.throw(_("Customer is required"))
        
        # Determine billing volume
        if bulk_cargo.billing_on == "Loaded Volume":
            billing_volume = flt(bulk_cargo.total_loaded_volume)
        else:
            billing_volume = flt(bulk_cargo.total_offloaded_volume)
        
        if billing_volume <= 0:
            frappe.throw(_("The selected billing volume must be greater than zero"))
        
        # Validate rate
        rate = flt(bulk_cargo.rate)
        if rate <= 0:
            frappe.throw(_("Rate must be greater than zero"))
        
        # Calculate amounts
        invoice_amount = billing_volume * rate
        
        # Prepare invoice items
        items = [{
            'item_code': bulk_cargo.service_item,
            'qty': billing_volume,
            'rate': rate,
            'amount': invoice_amount,
            'description': f"Billing based on {bulk_cargo.billing_on}: {billing_volume} units at {rate} per unit"
        }]
        
        # Create Sales Invoice
        sales_invoice = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'customer': bulk_cargo.customer_name,
            'currency': bulk_cargo.currency or frappe.defaults.get_global_default('currency'),
            'posting_date': nowdate(),
            'company': bulk_cargo.company or frappe.defaults.get_global_default('company'),
            'items': items
        })
        
        # Insert and save
        sales_invoice.insert(ignore_permissions=True)
        sales_invoice.save()
        
        # Update Bulk Cargo with Sales Invoice ID
        frappe.db.set_value("Bulk Cargo", name, "sales_invoice_id", sales_invoice.name)
        frappe.db.commit()
        
        return {
            "status": "success",
            "invoice_name": sales_invoice.name,
            "rate": rate,
            "message": f"Sales Invoice {sales_invoice.name} created successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating Sales Invoice: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_truck_capacity(truck_name, cargo_type):
    """Get truck capacity for specific cargo type"""
    try:
        truck = frappe.get_doc("Truck", truck_name)
        
        if not truck.compartment_details:
            return {"status": "error", "message": "No compartments found"}
        
        for compartment in truck.compartment_details:
            if compartment.cargo == cargo_type:
                return {
                    "status": "success",
                    "capacity": flt(compartment.capacity)
                }
        
        return {
            "status": "error", 
            "message": f"No compartment found for cargo type: {cargo_type}"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def calculate_loss(cargo_type, loaded_volume, offloaded_volume):
    """Calculate loss based on cargo type allowable loss percentage"""
    try:
        # Get allowable loss percentage from Cargo Types
        cargo_type_doc = frappe.get_doc("Cargo Types", cargo_type)
        allowable_loss_percentage = flt(cargo_type_doc.allowable_loss)
        
        loaded_volume = flt(loaded_volume)
        offloaded_volume = flt(offloaded_volume)
        
        actual_loss = loaded_volume - offloaded_volume
        allowable_loss = (allowable_loss_percentage / 100) * loaded_volume
        
        # Calculate exceeded loss
        exceeded_loss = max(0, actual_loss - allowable_loss)
        
        return {
            "status": "success",
            "actual_loss": actual_loss,
            "allowable_loss": allowable_loss,
            "exceeded_loss": exceeded_loss
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_bulk_cargo_summary(name):
    """Get summary data for Bulk Cargo"""
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