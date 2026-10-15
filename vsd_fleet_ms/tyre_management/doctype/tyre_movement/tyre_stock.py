# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors

"""Keep the tyre Serial No in the warehouse that matches the tyre status."""

import frappe
from frappe import _


class TyreStockMover:
	def __init__(self, movement, tyre):
		self.movement = movement
		self.tyre = tyre
		self.settings = frappe.get_single("Tyre Management Settings")

	def move(self, new_status):
		"""Create and submit the Stock Entry for this movement. Return its name, or None."""
		# Legacy tyres have no serial, so there is nothing in stock to move.
		if not self.settings.enable_stock_integration or not self.tyre.serial_no:
			return None

		source = self.current_warehouse()
		if new_status == "Scrapped":
			return self.submit_entry("Material Issue", source, None)

		target = self.settings.warehouse_for_status(new_status)
		if target == source:
			return None
		return self.submit_entry("Material Transfer", source, target)

	@staticmethod
	def cancel(stock_entry):
		entry = frappe.get_doc("Stock Entry", stock_entry)
		if entry.docstatus == 1:
			entry.flags.ignore_permissions = True
			entry.cancel()

	def current_warehouse(self):
		warehouse = frappe.db.get_value("Serial No", self.tyre.serial_no, "warehouse")
		if not warehouse:
			frappe.throw(
				_("Serial No {0} is not in stock. Receive the tyre into the tyre store first").format(
					self.tyre.serial_no
				)
			)
		return warehouse

	def submit_entry(self, entry_type, source, target):
		entry = frappe.new_doc("Stock Entry")
		entry.stock_entry_type = entry_type
		entry.purpose = entry_type
		entry.company = self.settings.company
		entry.posting_date = self.movement.transaction_date
		entry.set_posting_time = 1
		entry.remarks = _("Tyre {0}: {1} ({2})").format(
			self.tyre.name, self.movement.movement_type, self.movement.name
		)
		entry.append("items", self.item_row(source, target))
		entry.flags.ignore_permissions = True
		entry.insert()
		entry.submit()
		return entry.name

	def item_row(self, source, target):
		row = {
			"item_code": self.tyre.tyre_item,
			"qty": 1,
			"conversion_factor": 1,
			"s_warehouse": source,
			"t_warehouse": target,
			"use_serial_batch_fields": 1,
			"serial_no": self.tyre.serial_no,
		}
		if not target and self.settings.scrap_expense_account:
			row["expense_account"] = self.settings.scrap_expense_account
		return row
