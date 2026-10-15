# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# See license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import random_string

from vsd_fleet_ms.tyre_management.tyre_test_fixtures import TyreFixtures
from vsd_fleet_ms.utils.tyre_service_integration import create_tyre_movement_from_service_job_card

# Service Job Card comes from servicems, which CI does not install.
test_ignore = ["Service Job Card"]


class TestTyreServiceIntegration(TyreFixtures, FrappeTestCase):
	"""Service Job Card submit creates the matching Tyre Movement."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("DocType", "Service Job Card"):
			raise unittest.SkipTest("servicems is not installed")
		cls.setup_tyre_fixtures()
		settings = frappe.get_single("Transport Settings")
		settings.enable_service_ms = 1
		settings.create_tyre_movement_from_service_job_card = 1
		settings.flags.ignore_mandatory = True
		settings.save(ignore_permissions=True)

	def test_installation_from_job_card(self):
		(tyre,) = self.receive_tyres()
		job_card = self.make_job_card(
			self.truck, "Installation", tyre, "Truck", odometer=5_000, tyre_position=self.pos_steer_left
		)
		create_tyre_movement_from_service_job_card(job_card)

		doc = frappe.get_doc("Tyre Master", tyre)
		self.assertEqual((doc.status, doc.current_vehicle), ("In Service", self.truck))
		self.assertEqual(doc.install_odometer_km, 5_000)
		self.assertTrue(
			frappe.db.exists("Tyre Movement", {"service_job_card": job_card.name, "docstatus": 1})
		)

	def test_truck_found_by_plate(self):
		truck = frappe.get_doc("Truck", self.truck_2)
		truck.db_set("license_plate", f"_PL{random_string(5)}")
		(tyre,) = self.receive_tyres()
		job_card = self.make_job_card(
			truck.license_plate, "Installation", tyre, "Truck", odometer=100, tyre_position=self.pos_axle_1
		)
		create_tyre_movement_from_service_job_card(job_card)
		self.assertEqual(frappe.db.get_value("Tyre Master", tyre, "current_vehicle"), self.truck_2)

	def test_transfer_from_trailer_to_job_card_truck(self):
		(tyre,) = self.receive_tyres()
		position = self.make_position("SJC Trailer Axle")
		self.install(tyre, self.trailer, position, odometer=0, vehicle_type="Trailers")
		job_card = self.make_job_card(
			self.truck,
			"Vehicle Transfer",
			tyre,
			"Trailers",
			odometer=8_000,
			tyre_position=self.make_position("SJC Drive"),
			trailer=self.trailer,
		)
		create_tyre_movement_from_service_job_card(job_card)

		doc = frappe.get_doc("Tyre Master", tyre)
		self.assertEqual((doc.current_vehicle_type, doc.current_vehicle), ("Truck", self.truck))
		self.assertEqual(doc.install_odometer_km, 8_000)

	def test_invalid_tyre_does_not_block_job_card(self):
		(tyre,) = self.receive_tyres()
		self.install(tyre, self.truck, self.make_position("SJC Fitted"))
		job_card = self.make_job_card(
			self.truck, "Installation", tyre, "Truck", odometer=9_000, tyre_position=self.pos_steer_right
		)
		create_tyre_movement_from_service_job_card(job_card)
		self.assertFalse(frappe.db.exists("Tyre Movement", {"service_job_card": job_card.name}))

	def test_job_card_without_tyre_is_ignored(self):
		job_card = self.make_job_card(self.truck, None, None, None)
		create_tyre_movement_from_service_job_card(job_card)
		self.assertFalse(frappe.db.exists("Tyre Movement", {"service_job_card": job_card.name}))

	def make_job_card(self, vehicle, movement_type, tyre, install_on, odometer=None, **values):
		self.make_service_vehicle(vehicle)
		job_card = frappe.get_doc(
			{
				"doctype": "Service Job Card",
				"service_item_name": vehicle,
				"tyre_movement_type": movement_type,
				"tyre_serial": tyre,
				"tyre_install_on": install_on,
				"odometer_reading": odometer,
				**values,
			}
		)
		job_card.flags.ignore_mandatory = True
		job_card.insert(ignore_permissions=True, ignore_links=True)
		return job_card

	def make_service_vehicle(self, registration_number):
		if not frappe.db.exists("Service Vehicle", registration_number):
			frappe.get_doc({"doctype": "Service Vehicle", "registration_number": registration_number}).insert(
				ignore_permissions=True, ignore_mandatory=True
			)
