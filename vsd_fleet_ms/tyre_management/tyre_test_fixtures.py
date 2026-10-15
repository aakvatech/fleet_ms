# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors

"""Shared fixtures for tyre management tests."""

import unittest

import frappe
from frappe.utils import random_string

from vsd_fleet_ms.utils.custom_fields import import_tyre_item_fields

TYRE_RATE = 1_200_000


class TyreFixtures:
	"""Builds a company stock setup, tyre item, vehicles and positions."""

	@classmethod
	def setup_tyre_fixtures(cls):
		import_tyre_item_fields()
		cls.company = cls.get_company()
		cls.abbr = frappe.get_cached_value("Company", cls.company, "abbr")
		cls.store = cls.make_warehouse("Tyre Store")
		cls.in_service = cls.make_warehouse("Tyres In Service")
		cls.repair = cls.make_warehouse("Tyre Repair")
		cls.item = cls.make_tyre_item()
		cls.truck = cls.make_truck()
		cls.truck_2 = cls.make_truck()
		cls.trailer = cls.make_trailer()
		cls.pos_steer_left = cls.make_position("Steer Left")
		cls.pos_steer_right = cls.make_position("Steer Right")
		cls.pos_axle_1 = cls.make_position("Axle 1 Left Outer")
		cls.set_settings(enable_stock_integration=1)

	@classmethod
	def get_company(cls):
		company = frappe.db.get_value(
			"Company", {"enable_perpetual_inventory": 1, "stock_adjustment_account": ["is", "set"]}
		)
		if not company:
			raise unittest.SkipTest("No company with perpetual inventory on this site")
		return company

	@classmethod
	def set_settings(cls, **values):
		settings = frappe.get_single("Tyre Management Settings")
		settings.update(
			{
				"company": cls.company,
				"store_warehouse": cls.store,
				"in_service_warehouse": cls.in_service,
				"repair_warehouse": cls.repair,
				"auto_create_tyres": 1,
				"min_tread_depth_mm": 3,
				**values,
			}
		)
		settings.save(ignore_permissions=True)

	@classmethod
	def make_warehouse(cls, name):
		warehouse = f"{name} - {cls.abbr}"
		if not frappe.db.exists("Warehouse", warehouse):
			frappe.get_doc({"doctype": "Warehouse", "warehouse_name": name, "company": cls.company}).insert(
				ignore_permissions=True
			)
		return warehouse

	@classmethod
	def make_tyre_item(cls):
		item_code = "_Test Tyre 315/80R22.5"
		if not frappe.db.exists("Item", item_code):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_group": frappe.db.get_value("Item Group", {"is_group": 0}),
					"stock_uom": "Nos",
					"is_stock_item": 1,
					"has_serial_no": 1,
					"is_tyre": 1,
					"tyre_size": "315/80R22.5",
					"tyre_type": "Drive",
					"tyre_new_tread_depth_mm": 18,
				}
			).insert(ignore_permissions=True)
		return item_code

	@classmethod
	def make_truck(cls):
		plate = f"_T{random_string(6).upper()}"
		truck = frappe.get_doc(
			{
				"doctype": "Truck",
				"truck_number": plate,
				"license_plate": plate,
				"chassis_number": plate,
				"model": "Test",
				"make": "Test",
				"manufacturing_year": "2024",
				"acquisition_date": 2024,
				"fuel_type": "Diesel",
			}
		)
		truck.insert(ignore_permissions=True, ignore_mandatory=True)
		return truck.name

	@classmethod
	def make_trailer(cls):
		plate = f"_TR{random_string(6).upper()}"
		trailer = frappe.get_doc(
			{
				"doctype": "Trailers",
				"plate_number": plate,
				"chassis_number": plate,
				"number_of_axels": 3,
				"trailer_type": "Flat Bed",
				"tyre_specification": "Double Tyres",
				"manufacturing_year": 2024,
				"suspension_type": "Air Suspension",
				"status": "Available",
			}
		)
		trailer.insert(ignore_permissions=True, ignore_mandatory=True)
		return trailer.name

	@classmethod
	def make_position(cls, label):
		position = f"_Test {label}"
		if not frappe.db.exists("Tyre Position", position):
			frappe.get_doc({"doctype": "Tyre Position", "position": position}).insert(ignore_permissions=True)
		return position

	def receive_tyres(self, count=1, item_code=None, warehouse=None):
		"""Receive new tyres into the store the way a workshop does: Material Receipt with serials."""
		serials = [f"_TYR{random_string(8).upper()}" for _ in range(count)]
		entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Receipt",
				"company": self.company,
				"items": [
					{
						"item_code": item_code or self.item,
						"qty": count,
						"t_warehouse": warehouse or self.store,
						"basic_rate": TYRE_RATE,
						"conversion_factor": 1,
						"use_serial_batch_fields": 1,
						"serial_no": "\n".join(serials),
					}
				],
			}
		)
		entry.insert(ignore_permissions=True)
		entry.submit()
		return serials

	def move(self, tyre, movement_type, submit=True, **values):
		movement = frappe.get_doc(
			{"doctype": "Tyre Movement", "tyre_serial": tyre, "movement_type": movement_type, **values}
		)
		movement.insert(ignore_permissions=True)
		if submit:
			movement.submit()
		return movement

	def install(self, tyre, vehicle=None, position=None, odometer=10_000, vehicle_type="Truck"):
		return self.move(
			tyre,
			"Installation",
			to_vehicle_type=vehicle_type,
			to_vehicle=vehicle or self.truck,
			to_position=position or self.pos_steer_left,
			odometer_km=odometer,
		)

	def serial_warehouse(self, serial):
		return frappe.db.get_value("Serial No", serial, "warehouse")
