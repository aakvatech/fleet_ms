# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from vsd_fleet_ms.tyre_management.tyre_test_fixtures import TyreFixtures


class TestTyreInspection(TyreFixtures, FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.setup_tyre_fixtures()

	def inspect(self, tyre, **values):
		inspection = frappe.get_doc({"doctype": "Tyre Inspection", "tyre": tyre, **values})
		inspection.insert(ignore_permissions=True)
		inspection.submit()
		return inspection

	def test_low_tread_recommends_replace(self):
		(tyre,) = self.receive_tyres()
		inspection = self.inspect(tyre, tread_depth=2.5, recommended_action="Observe")
		self.assertEqual(inspection.recommended_action, "Replace")
		self.assertEqual(frappe.db.get_value("Tyre Master", tyre, "current_tread_depth_mm"), 2.5)

	def test_inspector_choice_is_kept(self):
		(tyre,) = self.receive_tyres()
		inspection = self.inspect(tyre, tread_depth=2.5, recommended_action="Repair")
		self.assertEqual(inspection.recommended_action, "Repair")

	def test_cancel_restores_previous_reading(self):
		(tyre,) = self.receive_tyres()
		self.inspect(tyre, tread_depth=14, inspection_date="2026-01-01")
		wrong = self.inspect(tyre, tread_depth=2, inspection_date="2026-02-01")
		wrong.cancel()
		doc = frappe.get_doc("Tyre Master", tyre)
		self.assertEqual(doc.current_tread_depth_mm, 14)
		self.assertEqual(str(doc.last_inspection_date), "2026-01-01")

	def test_inspection_does_not_add_km(self):
		(tyre,) = self.receive_tyres()
		self.install(tyre, self.truck_2, self.make_position("Insp Steer"), odometer=1_000)
		inspection = self.inspect(tyre, odometer_km=9_000, tread_depth=12)
		self.assertEqual(inspection.vehicle, self.truck_2)

		doc = frappe.get_doc("Tyre Master", tyre)
		self.assertEqual(doc.cumulative_usage, 0)
		self.assertEqual(doc.last_odometer_km, 9_000)

		self.move(tyre, "Removal", odometer_km=11_000)
		self.assertEqual(frappe.db.get_value("Tyre Master", tyre, "cumulative_usage"), 10_000)

	def test_scrapped_tyre_cannot_be_inspected(self):
		(tyre,) = self.receive_tyres()
		self.move(tyre, "Scrap")
		self.assertRaises(frappe.ValidationError, self.inspect, tyre, tread_depth=5)
