# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TyreMaster(Document):
	def validate(self):
		# Legacy tyres created before the item remodel have no serial; keep them editable.
		if self.is_new() or self.serial_no:
			self.validate_item_and_serial()

		if self.status == "Scrapped":
			self.clear_fitment()

		self.validate_non_negative()
		self.cost_per_km = self.calculate_cost_per_km()

	def validate_item_and_serial(self):
		if not self.tyre_item or not self.serial_no:
			frappe.throw(_("Tyre Item and Serial No are required"))

		item = frappe.get_cached_value("Item", self.tyre_item, ["is_tyre", "has_serial_no"], as_dict=True)
		if not item or not item.is_tyre or not item.has_serial_no:
			frappe.throw(_("Item {0} must have Is Tyre and Has Serial No enabled").format(self.tyre_item))

		serial_item = frappe.db.get_value("Serial No", self.serial_no, "item_code")
		if serial_item != self.tyre_item:
			frappe.throw(
				_("Serial No {0} belongs to item {1}, not {2}").format(
					self.serial_no, serial_item, self.tyre_item
				)
			)

	def validate_non_negative(self):
		for field in ("cumulative_usage", "retread_count", "purchase_cost", "total_repair_cost"):
			if flt(self.get(field)) < 0:
				frappe.throw(_("{0} cannot be negative").format(_(self.meta.get_label(field))))

	def calculate_cost_per_km(self):
		km = flt(self.cumulative_usage)
		if not km:
			return 0
		return (flt(self.purchase_cost) + flt(self.total_repair_cost)) / km

	def clear_fitment(self):
		self.current_vehicle_type = ""
		self.current_vehicle = ""
		self.position = ""
		self.install_odometer_km = 0

	def is_fitted(self):
		return self.status == "In Service" and bool(self.current_vehicle_type and self.current_vehicle)
