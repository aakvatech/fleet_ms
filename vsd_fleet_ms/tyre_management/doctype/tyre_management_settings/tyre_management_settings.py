# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

WAREHOUSE_FIELDS = ("store_warehouse", "in_service_warehouse", "repair_warehouse")


class TyreManagementSettings(Document):
	def validate(self):
		if self.enable_stock_integration:
			self.validate_warehouses()

	def validate_warehouses(self):
		warehouses = [self.get(field) for field in WAREHOUSE_FIELDS]
		if len(set(warehouses)) != len(warehouses):
			frappe.throw(_("Tyre Store, In-Service and Repair warehouses must be different"))

		for warehouse in warehouses:
			company = frappe.db.get_value("Warehouse", warehouse, "company")
			if company != self.company:
				frappe.throw(
					_("Warehouse {0} does not belong to company {1}").format(warehouse, self.company)
				)

	def warehouse_for_status(self, status):
		"""Return the warehouse where a tyre with this status is kept."""
		return {
			"In Store": self.store_warehouse,
			"In Service": self.in_service_warehouse,
			"Under Repair": self.repair_warehouse,
		}.get(status)
