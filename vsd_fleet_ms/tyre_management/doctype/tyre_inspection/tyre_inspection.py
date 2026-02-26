# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class TyreInspection(Document):
    def validate(self):
        if not self.inspection_date:
            self.inspection_date = nowdate()

    def on_submit(self):
        tyre = frappe.get_doc("Tyre Master", self.tyre)
        self.update_usage(tyre)
        tyre.save(ignore_permissions=True)
        self.create_ledger_entry()

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
        ledger.tyre = self.tyre
        ledger.posting_date = self.inspection_date
        ledger.transaction_type = "Inspection"
        ledger.reference_doctype = self.doctype
        ledger.reference_name = self.name
        ledger.air_pressure = self.air_pressure
        ledger.tread_depth = self.tread_depth
        ledger.recommended_action = self.recommended_action
        ledger.odometer_km = self.odometer_km
        ledger.remarks = self.damage_notes
        ledger.insert(ignore_permissions=True)

