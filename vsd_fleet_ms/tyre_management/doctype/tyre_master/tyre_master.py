# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TyreMaster(Document):
    def validate(self):
        if self.status == "Scrapped":
            self.current_vehicle_type = ""
            self.current_vehicle = ""
            self.position = ""

        if self.cumulative_usage and float(self.cumulative_usage) < 0:
            frappe.throw("Cumulative Usage cannot be negative")

        if self.retread_count and int(self.retread_count) < 0:
            frappe.throw("Retread Count cannot be negative")
