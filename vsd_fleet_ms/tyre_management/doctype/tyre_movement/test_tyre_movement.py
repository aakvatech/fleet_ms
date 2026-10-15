# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from vsd_fleet_ms.tyre_management.tyre_test_fixtures import TYRE_RATE, TyreFixtures

# Service Job Card comes from servicems, which CI does not install.
test_ignore = ["Service Job Card"]


class TestTyreMovement(TyreFixtures, FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.setup_tyre_fixtures()

	def setUp(self):
		self.set_settings(enable_stock_integration=1)

	def test_full_lifecycle_moves_serial_between_warehouses(self):
		(tyre,) = self.receive_tyres()

		install = self.install(tyre, odometer=10_000)
		self.assertEqual(self.serial_warehouse(tyre), self.in_service)
		self.assertTrue(install.stock_entry)

		rotate = self.move(tyre, "Positional Change", to_position=self.pos_steer_right, odometer_km=25_000)
		self.assertEqual(rotate.usage_km, 15_000)
		self.assertFalse(rotate.stock_entry, "rotation on the same vehicle is not a stock move")

		self.move(
			tyre,
			"Vehicle Transfer",
			to_vehicle_type="Trailers",
			to_vehicle=self.trailer,
			to_position=self.pos_axle_1,
			odometer_km=40_000,
			to_odometer_km=500,
		)
		doc = frappe.get_doc("Tyre Master", tyre)
		self.assertEqual((doc.current_vehicle_type, doc.current_vehicle), ("Trailers", self.trailer))
		self.assertEqual(doc.install_odometer_km, 500)

		self.move(tyre, "Send for Repair", odometer_km=20_500)
		self.assertEqual(self.serial_warehouse(tyre), self.repair)

		self.move(tyre, "Return from Repair", is_retreaded=1, repair_cost=300_000)
		doc.reload()
		self.assertEqual(doc.status, "In Store")
		self.assertEqual(self.serial_warehouse(tyre), self.store)
		self.assertEqual(doc.retread_count, 1)
		# 15,000 + 15,000 on the truck, 20,000 on the trailer.
		self.assertEqual(doc.cumulative_usage, 50_000)
		self.assertAlmostEqual(doc.cost_per_km, (TYRE_RATE + 300_000) / 50_000)

		self.move(tyre, "Scrap")
		doc.reload()
		self.assertEqual(doc.status, "Scrapped")
		self.assertFalse(self.serial_warehouse(tyre), "scrapped tyre is issued out of stock")

	def test_installation_requires_tyre_in_store(self):
		(tyre,) = self.receive_tyres()
		self.install(tyre)
		self.assertRaises(frappe.ValidationError, self.install, tyre, self.truck_2, self.pos_steer_left)

	def test_removal_requires_fitted_tyre(self):
		(tyre,) = self.receive_tyres()
		self.assertRaises(frappe.ValidationError, self.move, tyre, "Removal")

	def test_position_cannot_hold_two_tyres(self):
		first, second = self.receive_tyres(2)
		self.install(first, self.truck_2, self.pos_steer_right)
		self.assertRaises(frappe.ValidationError, self.install, second, self.truck_2, self.pos_steer_right)

	def test_odometer_cannot_go_below_fitment_reading(self):
		(tyre,) = self.receive_tyres()
		self.install(tyre, self.truck_2, self.pos_axle_1, odometer=50_000)
		self.assertRaises(frappe.ValidationError, self.move, tyre, "Removal", odometer_km=40_000)

	def test_source_vehicle_must_match_fitment(self):
		(tyre,) = self.receive_tyres()
		self.install(tyre, self.truck, self.pos_axle_1)
		self.assertRaises(
			frappe.ValidationError,
			self.move,
			tyre,
			"Removal",
			from_vehicle_type="Truck",
			from_vehicle=self.truck_2,
		)

	def test_source_is_filled_from_current_fitment(self):
		(tyre,) = self.receive_tyres()
		self.install(tyre, self.truck_2, self.pos_steer_left)
		removal = self.move(tyre, "Removal", submit=False, odometer_km=20_000)
		self.assertEqual((removal.from_vehicle, removal.from_position), (self.truck_2, self.pos_steer_left))

	def test_return_from_repair_can_fit_directly_on_vehicle(self):
		(tyre,) = self.receive_tyres()
		self.move(tyre, "Send for Repair")
		self.move(
			tyre,
			"Return from Repair",
			to_vehicle_type="Truck",
			to_vehicle=self.truck,
			to_position=self.make_position("Drive 2 Right Inner"),
			odometer_km=1_000,
		)
		self.assertEqual(frappe.db.get_value("Tyre Master", tyre, "status"), "In Service")
		self.assertEqual(self.serial_warehouse(tyre), self.in_service)

	def test_cancel_reverts_tyre_and_stock(self):
		(tyre,) = self.receive_tyres()
		install = self.install(tyre, self.truck, self.make_position("Drive 1 Left Outer"), odometer=1_000)
		removal = self.move(tyre, "Removal", odometer_km=6_000)
		self.assertEqual(frappe.db.get_value("Tyre Master", tyre, "cumulative_usage"), 5_000)

		self.assertRaises(frappe.ValidationError, install.cancel)

		removal.cancel()
		doc = frappe.get_doc("Tyre Master", tyre)
		self.assertEqual(
			(doc.status, doc.current_vehicle, doc.cumulative_usage), ("In Service", self.truck, 0)
		)
		self.assertEqual(self.serial_warehouse(tyre), self.in_service)
		self.assertEqual(frappe.db.get_value("Stock Entry", removal.stock_entry, "docstatus"), 2)

		install.reload()
		install.cancel()
		doc.reload()
		self.assertEqual(doc.status, "In Store")
		self.assertFalse(doc.current_vehicle)
		self.assertEqual(self.serial_warehouse(tyre), self.store)

	def test_without_stock_integration_no_stock_entry(self):
		self.set_settings(enable_stock_integration=0)
		(tyre,) = self.receive_tyres()
		install = self.install(tyre, self.truck_2, self.make_position("Drive 1 Right Outer"))
		self.assertFalse(install.stock_entry)
		self.assertEqual(self.serial_warehouse(tyre), self.store)

	def test_truck_fitment_requires_odometer(self):
		(tyre,) = self.receive_tyres()
		self.assertRaises(
			frappe.ValidationError, self.install, tyre, self.truck_2, self.pos_axle_1, odometer=0
		)

	def test_trailer_fitment_without_odometer(self):
		(tyre,) = self.receive_tyres()
		self.install(
			tyre, self.trailer, self.make_position("Trailer Axle 3"), odometer=0, vehicle_type="Trailers"
		)
		removal = self.move(tyre, "Removal")
		self.assertEqual(removal.usage_km, 0)

	def test_scrapped_tyre_cannot_move(self):
		(tyre,) = self.receive_tyres()
		self.move(tyre, "Scrap")
		self.assertRaises(frappe.ValidationError, self.install, tyre)
