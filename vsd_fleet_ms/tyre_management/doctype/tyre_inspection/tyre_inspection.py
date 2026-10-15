# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate


class TyreInspection(Document):
	def validate(self):
		if not self.inspection_date:
			self.inspection_date = nowdate()

		tyre = frappe.get_doc("Tyre Master", self.tyre)
		if tyre.status == "Scrapped":
			frappe.throw(_("Tyre {0} is scrapped").format(tyre.name))

		self.vehicle_type = tyre.current_vehicle_type
		self.vehicle = tyre.current_vehicle
		self.position = tyre.position
		self.apply_tread_limit()

	def apply_tread_limit(self):
		min_depth = flt(frappe.db.get_single_value("Tyre Management Settings", "min_tread_depth_mm"))
		if self.tread_depth and min_depth and flt(self.tread_depth) < min_depth:
			# Keep an inspector's Repair/Replace call; only escalate softer actions.
			if self.recommended_action in ("Observe", "Rotate", None, ""):
				self.recommended_action = "Replace"
			frappe.msgprint(
				_("Tread depth {0} mm is below the minimum of {1} mm").format(self.tread_depth, min_depth),
				indicator="red",
				alert=True,
			)

	def on_submit(self):
		tyre = frappe.get_doc("Tyre Master", self.tyre)
		# Inspections record condition only; KM run is counted by movements.
		if self.tread_depth:
			tyre.current_tread_depth_mm = self.tread_depth
		if self.odometer_km:
			tyre.last_odometer_km = self.odometer_km
		tyre.last_inspection_date = self.inspection_date
		tyre.save(ignore_permissions=True)
		self.create_ledger_entry()

	def on_cancel(self):
		self.restore_tyre_condition()
		for name in frappe.get_all(
			"Tyre Ledger",
			filters={"reference_doctype": self.doctype, "reference_name": self.name},
			pluck="name",
		):
			frappe.delete_doc("Tyre Ledger", name, ignore_permissions=True)

	def restore_tyre_condition(self):
		"""Put back the readings of the latest inspection that is still submitted."""
		previous = frappe.get_all(
			"Tyre Inspection",
			filters={"tyre": self.tyre, "docstatus": 1, "name": ["!=", self.name]},
			fields=["tread_depth", "inspection_date"],
			order_by="inspection_date desc, creation desc",
			limit=1,
		)
		tyre = frappe.get_doc("Tyre Master", self.tyre)
		tyre.current_tread_depth_mm = previous[0].tread_depth if previous else 0
		tyre.last_inspection_date = previous[0].inspection_date if previous else None
		tyre.save(ignore_permissions=True)

	def create_ledger_entry(self):
		ledger = frappe.new_doc("Tyre Ledger")
		ledger.update(
			{
				"tyre": self.tyre,
				"posting_date": self.inspection_date,
				"transaction_type": "Inspection",
				"reference_doctype": self.doctype,
				"reference_name": self.name,
				"air_pressure": self.air_pressure,
				"tread_depth": self.tread_depth,
				"recommended_action": self.recommended_action,
				"odometer_km": self.odometer_km,
				"remarks": self.damage_notes,
			}
		)
		ledger.insert(ignore_permissions=True)
