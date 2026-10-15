# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import random_string

from vsd_fleet_ms.tyre_management.tyre_test_fixtures import TYRE_RATE, TyreFixtures
from vsd_fleet_ms.utils.tyre_receipt import get_tyre_store_warehouse


class TestTyreMaster(TyreFixtures, FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.setup_tyre_fixtures()

	def test_receipt_creates_tyre_per_serial(self):
		serials = self.receive_tyres(3)
		for serial in serials:
			tyre = frappe.get_doc("Tyre Master", serial)
			self.assertEqual(tyre.tyre_item, self.item)
			self.assertEqual(tyre.status, "In Store")
			self.assertEqual(tyre.warehouse, self.store)
			self.assertEqual(tyre.purchase_cost, TYRE_RATE)
			self.assertEqual(tyre.tyre_size, "315/80R22.5")
			# Not fitted yet, so no vehicle side; a Select must not default to "Truck".
			self.assertFalse(tyre.current_vehicle_type)

	def test_receipt_creates_tyres_before_settings_are_saved(self):
		frappe.db.delete("Singles", {"doctype": "Tyre Management Settings", "field": "auto_create_tyres"})
		try:
			(serial,) = self.receive_tyres()
			self.assertTrue(frappe.db.exists("Tyre Master", serial))
		finally:
			self.set_settings(auto_create_tyres=1)

	def test_receipt_skips_tyres_when_auto_create_is_off(self):
		self.set_settings(auto_create_tyres=0)
		try:
			(serial,) = self.receive_tyres()
			self.assertFalse(frappe.db.exists("Tyre Master", serial))
		finally:
			self.set_settings(auto_create_tyres=1)

	def test_tyres_must_be_received_into_tyre_store(self):
		with self.assertRaisesRegex(frappe.ValidationError, "Tyre Store"):
			self.receive_tyres(warehouse=self.in_service)

	def test_any_warehouse_allowed_without_stock_integration(self):
		self.set_settings(enable_stock_integration=0)
		try:
			(serial,) = self.receive_tyres(warehouse=self.repair)
			self.assertEqual(frappe.db.get_value("Tyre Master", serial, "warehouse"), self.repair)
		finally:
			self.set_settings(enable_stock_integration=1)

	def test_receipt_form_default_warehouse(self):
		self.assertEqual(get_tyre_store_warehouse(self.item, self.company), self.store)
		self.assertIsNone(get_tyre_store_warehouse(self.make_other_serial_item(), self.company))

	def test_serial_must_belong_to_tyre_item(self):
		other_item = self.make_other_serial_item()
		(serial,) = self.receive_tyres(item_code=other_item)
		tyre = frappe.get_doc({"doctype": "Tyre Master", "tyre_item": self.item, "serial_no": serial})
		self.assertRaises(frappe.ValidationError, tyre.insert)

	def test_new_tyre_requires_item_and_serial(self):
		tyre = frappe.get_doc({"doctype": "Tyre Master", "tyre_item": self.item})
		self.assertRaises(frappe.ValidationError, tyre.insert)

	def test_tyre_item_must_be_serialised(self):
		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": f"_Test Tyre No Serial {random_string(4)}",
				"item_group": frappe.db.get_value("Item Group", {"is_group": 0}),
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"is_tyre": 1,
			}
		)
		self.assertRaises(frappe.ValidationError, item.insert)

	def make_other_serial_item(self):
		item_code = "_Test Serial Battery"
		if not frappe.db.exists("Item", item_code):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_group": frappe.db.get_value("Item Group", {"is_group": 0}),
					"stock_uom": "Nos",
					"is_stock_item": 1,
					"has_serial_no": 1,
				}
			).insert(ignore_permissions=True)
		return item_code
