# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TyreMaster(Document):
    def validate(self):
        last_ledger = frappe.get_all(
            "Tyre Ledger",
            filters={"tyre": self.name},
            fields=["transaction_type", "movement_type"],
            order_by="creation desc",
            limit=1,
        )

        if last_ledger:
            ledger_row = last_ledger[0]
            if ledger_row.get("movement_type") == "Scrap" or ledger_row.get("transaction_type") == "Scrap":
                self.status = "Scrapped"

        if self.status == "Scrapped":
            self.current_vehicle_type = ""
            self.current_vehicle = ""
            self.position = ""

        if self.cumulative_usage and float(self.cumulative_usage) < 0:
            frappe.throw("Cumulative Usage cannot be negative")

        if self.retread_count and int(self.retread_count) < 0:
            frappe.throw("Retread Count cannot be negative")
