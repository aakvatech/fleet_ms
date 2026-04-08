# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class TyreMovement(Document):
    def validate(self):
        if not self.transaction_date:
            self.transaction_date = nowdate()

        tyre = frappe.get_doc("Tyre Master", self.tyre_serial)
        if tyre.status == "Scrapped":
            frappe.throw("Scrapped tyre cannot be moved")

        self.validate_tyre_state_for_movement(tyre)
        self.validate_required_fields()
        self.validate_from_matches_current(tyre)

    def validate_tyre_state_for_movement(self, tyre):
        is_installed = bool(tyre.current_vehicle_type and tyre.current_vehicle)

        if self.movement_type == "Installation":
            if tyre.status == "In Service" or is_installed:
                frappe.throw(
                    f"Tyre {tyre.name} is already in service on {tyre.current_vehicle_type} {tyre.current_vehicle}. "
                    "Create a Removal first before Installation."
                )
            return

        if self.movement_type in [
            "Removal",
            "Positional Change",
            "Vehicle Transfer",
            "Send for Repair",
            "Return from Repair",
            "Scrap",
        ] and not is_installed and tyre.status != "Under Repair":
            frappe.throw(f"Tyre {tyre.name} is not currently installed on any vehicle.")

    def validate_required_fields(self):
        if self.movement_type == "Installation":
            self.ensure_to_fields()
            if not self.to_position:
                frappe.throw("Target Position is required for Installation")
            return

        self.ensure_from_fields()
        if not self.from_position:
            frappe.throw("Source Position is required")

        if self.movement_type == "Positional Change":
            if not self.to_position:
                frappe.throw("To Position is required for Positional Change")
            if self.from_position == self.to_position:
                frappe.throw("From Position and To Position cannot be the same")
            self.ensure_to_fields()
            return

        if self.movement_type in ["Vehicle Transfer", "Return from Repair"]:
            self.ensure_to_fields()
            if not self.to_position:
                frappe.throw("Target Position is required")

    def ensure_from_fields(self):
        if not self.from_vehicle_type or not self.from_vehicle:
            frappe.throw("Source Truck/Trailer and Source Truck/Trailer No are required")

    def ensure_to_fields(self):
        if not self.to_vehicle_type or not self.to_vehicle:
            frappe.throw("To Truck/Trailer and To Truck/Trailer No are required")

    def validate_from_matches_current(self, tyre):
        if self.movement_type == "Installation":
            return

        if tyre.current_vehicle and self.from_vehicle and tyre.current_vehicle != self.from_vehicle:
            frappe.throw("Source Truck/Trailer No does not match tyre current vehicle")

    def on_submit(self):
        tyre = frappe.get_doc("Tyre Master", self.tyre_serial)
        self.update_tyre_master(tyre)
        self.create_ledger_entry()

    def on_cancel(self):
        self.delete_ledger_entries()
        tyre = frappe.get_doc("Tyre Master", self.tyre_serial)
        self.restore_tyre_master_from_ledger(tyre)
        tyre.save(ignore_permissions=True)

    def update_tyre_master(self, tyre):
        movement_type = self.movement_type

        if movement_type in ["Installation", "Positional Change", "Vehicle Transfer", "Return from Repair"]:
            tyre.status = "In Service"
            tyre.current_vehicle_type = self.to_vehicle_type or ""
            tyre.current_vehicle = self.to_vehicle or ""
            tyre.position = self.to_position or ""
            if movement_type == "Installation" and not tyre.installation_date:
                tyre.installation_date = self.transaction_date
        elif movement_type == "Removal":
            tyre.status = "In Store"
            tyre.current_vehicle_type = ""
            tyre.current_vehicle = ""
            tyre.position = ""
        elif movement_type == "Send for Repair":
            tyre.status = "Under Repair"
            tyre.current_vehicle_type = ""
            tyre.current_vehicle = ""
            tyre.position = ""
        elif movement_type == "Scrap":
            tyre.status = "Scrapped"
            tyre.current_vehicle_type = ""
            tyre.current_vehicle = ""
            tyre.position = ""

        self.update_usage(tyre)
        tyre.save(ignore_permissions=True)

    def update_usage(self, tyre):
        if not self.odometer_km:
            return

        current_odometer = float(self.odometer_km)
        last_odometer = float(tyre.last_odometer_km or 0)

        if last_odometer and current_odometer >= last_odometer:
            tyre.cumulative_usage = float(tyre.cumulative_usage or 0) + (current_odometer - last_odometer)

        tyre.last_odometer_km = current_odometer

    def create_ledger_entry(self):
        ledger = frappe.new_doc("Tyre Ledger")
        ledger.tyre = self.tyre_serial
        ledger.posting_date = self.transaction_date
        ledger.transaction_type = "Movement"
        ledger.reference_doctype = self.doctype
        ledger.reference_name = self.name
        ledger.movement_type = self.movement_type
        ledger.from_vehicle_type = self.from_vehicle_type
        ledger.from_vehicle = self.from_vehicle
        ledger.from_position = self.from_position
        ledger.to_vehicle_type = self.to_vehicle_type
        ledger.to_vehicle = self.to_vehicle
        ledger.to_position = self.to_position
        ledger.odometer_km = self.odometer_km
        ledger.remarks = self.remarks
        ledger.insert(ignore_permissions=True)

    def delete_ledger_entries(self):
        ledger_names = frappe.get_all(
            "Tyre Ledger",
            filters={
                "reference_doctype": self.doctype,
                "reference_name": self.name,
            },
            pluck="name",
        )

        for ledger_name in ledger_names:
            frappe.delete_doc("Tyre Ledger", ledger_name, ignore_permissions=True)

    def restore_tyre_master_from_ledger(self, tyre):
        last_movement = frappe.get_all(
            "Tyre Ledger",
            filters={
                "tyre": self.tyre_serial,
                "transaction_type": "Movement",
            },
            fields=[
                "movement_type",
                "from_vehicle_type",
                "from_vehicle",
                "from_position",
                "to_vehicle_type",
                "to_vehicle",
                "to_position",
            ],
            order_by="posting_date desc, creation desc",
            limit=1,
        )

        if not last_movement:
            tyre.status = "In Store"
            tyre.current_vehicle_type = ""
            tyre.current_vehicle = ""
            tyre.position = ""
            return

        movement = last_movement[0]
        movement_type = movement.get("movement_type")

        if movement_type in ["Installation", "Positional Change", "Vehicle Transfer", "Return from Repair"]:
            tyre.status = "In Service"
            tyre.current_vehicle_type = movement.get("to_vehicle_type") or ""
            tyre.current_vehicle = movement.get("to_vehicle") or ""
            tyre.position = movement.get("to_position") or ""
        elif movement_type == "Removal":
            tyre.status = "In Store"
            tyre.current_vehicle_type = ""
            tyre.current_vehicle = ""
            tyre.position = ""
        elif movement_type == "Send for Repair":
            tyre.status = "Under Repair"
            tyre.current_vehicle_type = ""
            tyre.current_vehicle = ""
            tyre.position = ""
        elif movement_type == "Scrap":
            tyre.status = "Scrapped"
            tyre.current_vehicle_type = ""
            tyre.current_vehicle = ""
            tyre.position = ""
