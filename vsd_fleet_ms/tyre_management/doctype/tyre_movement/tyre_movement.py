# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

from vsd_fleet_ms.tyre_management.doctype.tyre_movement.tyre_stock import TyreStockMover

# Tyre status a movement may start from.
ALLOWED_FROM_STATUS = {
	"Installation": ("In Store",),
	"Removal": ("In Service",),
	"Positional Change": ("In Service",),
	"Vehicle Transfer": ("In Service",),
	"Send for Repair": ("In Service", "In Store"),
	"Return from Repair": ("Under Repair",),
	"Scrap": ("In Service", "In Store", "Under Repair"),
}

RESULT_STATUS = {
	"Installation": "In Service",
	"Removal": "In Store",
	"Positional Change": "In Service",
	"Vehicle Transfer": "In Service",
	"Send for Repair": "Under Repair",
	"Scrap": "Scrapped",
}


class TyreMovement(Document):
	def validate(self):
		if not self.transaction_date:
			self.transaction_date = nowdate()

		tyre = self.get_tyre()
		self.validate_allowed_status(tyre)
		self.set_from_fitment(tyre)
		self.validate_target()
		self.validate_odometer(tyre)
		self.validate_truck_readings(tyre)
		if self.movement_type != "Return from Repair":
			self.is_retreaded = 0
			self.repair_cost = 0

	def before_submit(self):
		tyre = self.get_tyre()
		self.previous_status = tyre.status
		self.previous_install_odometer_km = tyre.install_odometer_km
		self.previous_installation_date = tyre.installation_date
		self.usage_km = self.calculate_usage(tyre)

	def on_submit(self):
		tyre = self.get_tyre()
		self.db_set("stock_entry", TyreStockMover(self, tyre).move(self.result_status()))
		self.apply_to_tyre(tyre)
		self.create_ledger_entry()

	def before_cancel(self):
		self.validate_is_latest_movement()

	def on_cancel(self):
		if self.stock_entry:
			TyreStockMover.cancel(self.stock_entry)
		self.revert_tyre(self.get_tyre())
		self.delete_ledger_entries()

	def get_tyre(self):
		return frappe.get_doc("Tyre Master", self.tyre_serial)

	def result_status(self):
		if self.movement_type == "Return from Repair":
			return "In Service" if self.to_vehicle else "In Store"
		return RESULT_STATUS[self.movement_type]

	def validate_allowed_status(self, tyre):
		allowed = ALLOWED_FROM_STATUS[self.movement_type]
		if tyre.status not in allowed:
			frappe.throw(
				_("{0} is not allowed for tyre {1} with status {2}. Allowed from: {3}").format(
					self.movement_type, tyre.name, tyre.status, ", ".join(allowed)
				)
			)

	def set_from_fitment(self, tyre):
		"""The source is always where the tyre is fitted now."""
		if not tyre.is_fitted():
			self.from_vehicle_type = self.from_vehicle = self.from_position = ""
			return

		if self.from_vehicle and self.from_vehicle != tyre.current_vehicle:
			frappe.throw(
				_("Tyre {0} is fitted on {1}, not {2}").format(
					tyre.name, tyre.current_vehicle, self.from_vehicle
				)
			)
		self.from_vehicle_type = tyre.current_vehicle_type
		self.from_vehicle = tyre.current_vehicle
		self.from_position = tyre.position

	def validate_target(self):
		if self.result_status() != "In Service":
			self.to_vehicle_type = self.to_vehicle = self.to_position = ""
			return

		if self.movement_type == "Positional Change":
			self.to_vehicle_type, self.to_vehicle = self.from_vehicle_type, self.from_vehicle

		if not (self.to_vehicle_type and self.to_vehicle and self.to_position):
			frappe.throw(_("To Truck/Trailer, To Truck/Trailer No and To Position are required"))

		if self.movement_type == "Positional Change" and self.from_position == self.to_position:
			frappe.throw(_("From Position and To Position cannot be the same"))
		if self.movement_type == "Vehicle Transfer" and self.to_vehicle == self.from_vehicle:
			frappe.throw(_("Use Positional Change to move a tyre on the same vehicle"))

		self.validate_position_is_free()

	def validate_position_is_free(self):
		occupant = frappe.db.get_value(
			"Tyre Master",
			{
				"status": "In Service",
				"current_vehicle_type": self.to_vehicle_type,
				"current_vehicle": self.to_vehicle,
				"position": self.to_position,
				"name": ["!=", self.tyre_serial],
			},
		)
		if occupant:
			frappe.throw(
				_("Position {0} on {1} already has tyre {2}. Remove or move it first").format(
					self.to_position, self.to_vehicle, occupant
				)
			)

	def validate_odometer(self, tyre):
		if (
			tyre.is_fitted()
			and flt(self.odometer_km)
			and flt(self.odometer_km) < flt(tyre.install_odometer_km)
		):
			frappe.throw(
				_("Odometer {0} is lower than the reading at fitment ({1})").format(
					self.odometer_km, tyre.install_odometer_km
				)
			)

	def validate_truck_readings(self, tyre):
		"""KM per tyre needs a truck reading at both ends of a fitment. Trailers have no odometer."""
		leaves_truck = tyre.is_fitted() and tyre.current_vehicle_type == "Truck"
		if leaves_truck and not flt(self.odometer_km):
			frappe.throw(_("Odometer/KM of truck {0} is required").format(tyre.current_vehicle))

		if self.result_status() == "In Service" and self.to_vehicle_type == "Truck":
			if not self.new_install_odometer():
				frappe.throw(_("Odometer/KM of receiving truck {0} is required").format(self.to_vehicle))

	def calculate_usage(self, tyre):
		"""KM run since fitment. Both readings come from the same vehicle."""
		if not tyre.is_fitted() or self.movement_type == "Installation":
			return 0
		if not flt(self.odometer_km) or not flt(tyre.install_odometer_km):
			return 0
		return flt(self.odometer_km) - flt(tyre.install_odometer_km)

	def new_install_odometer(self):
		if self.result_status() != "In Service":
			return 0
		if self.movement_type == "Vehicle Transfer":
			return flt(self.to_odometer_km)
		return flt(self.odometer_km)

	def apply_to_tyre(self, tyre):
		tyre.status = self.result_status()
		if tyre.status == "In Service":
			if self.movement_type != "Positional Change":
				tyre.installation_date = self.transaction_date
			tyre.current_vehicle_type = self.to_vehicle_type
			tyre.current_vehicle = self.to_vehicle
			tyre.position = self.to_position
			tyre.install_odometer_km = self.new_install_odometer()
		else:
			tyre.clear_fitment()

		tyre.cumulative_usage = flt(tyre.cumulative_usage) + flt(self.usage_km)
		tyre.last_odometer_km = max(flt(self.odometer_km), flt(self.to_odometer_km)) or tyre.last_odometer_km
		tyre.retread_count = (tyre.retread_count or 0) + (1 if self.is_retreaded else 0)
		tyre.total_repair_cost = flt(tyre.total_repair_cost) + flt(self.repair_cost)
		tyre.save(ignore_permissions=True)

	def revert_tyre(self, tyre):
		tyre.status = self.previous_status or ("In Service" if self.from_vehicle else "In Store")
		if tyre.status == "In Service":
			tyre.current_vehicle_type = self.from_vehicle_type
			tyre.current_vehicle = self.from_vehicle
			tyre.position = self.from_position
			tyre.install_odometer_km = self.previous_install_odometer_km
		else:
			tyre.clear_fitment()
		tyre.installation_date = self.previous_installation_date

		tyre.cumulative_usage = flt(tyre.cumulative_usage) - flt(self.usage_km)
		tyre.retread_count = (tyre.retread_count or 0) - (1 if self.is_retreaded else 0)
		tyre.total_repair_cost = flt(tyre.total_repair_cost) - flt(self.repair_cost)
		tyre.save(ignore_permissions=True)

	def validate_is_latest_movement(self):
		later = frappe.db.get_value(
			"Tyre Movement",
			{"tyre_serial": self.tyre_serial, "docstatus": 1, "creation": [">", self.creation]},
		)
		if later:
			frappe.throw(_("Cancel the later movement {0} of this tyre first").format(later))

	def create_ledger_entry(self):
		ledger = frappe.new_doc("Tyre Ledger")
		ledger.update(
			{
				"tyre": self.tyre_serial,
				"posting_date": self.transaction_date,
				"transaction_type": "Movement",
				"reference_doctype": self.doctype,
				"reference_name": self.name,
				"movement_type": self.movement_type,
				"from_vehicle_type": self.from_vehicle_type,
				"from_vehicle": self.from_vehicle,
				"from_position": self.from_position,
				"to_vehicle_type": self.to_vehicle_type,
				"to_vehicle": self.to_vehicle,
				"to_position": self.to_position,
				"odometer_km": self.odometer_km,
				"remarks": self.remarks,
			}
		)
		ledger.insert(ignore_permissions=True)

	def delete_ledger_entries(self):
		for name in frappe.get_all(
			"Tyre Ledger",
			filters={"reference_doctype": self.doctype, "reference_name": self.name},
			pluck="name",
		):
			frappe.delete_doc("Tyre Ledger", name, ignore_permissions=True)
