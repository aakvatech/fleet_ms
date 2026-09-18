# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data, None, None


def get_columns():
	return [
		{"fieldname": "truck", "label": _("Truck"), "fieldtype": "Link", "options": "Truck", "width": 120},
		{"fieldname": "truck_number", "label": _("Truck Number"), "fieldtype": "Data", "width": 110},
		{"fieldname": "status", "label": _("Current Status"), "fieldtype": "Select", "width": 120},
		{"fieldname": "total_trips", "label": _("Total Trips"), "fieldtype": "Int", "width": 100},
		{"fieldname": "completed_trips", "label": _("Completed Trips"), "fieldtype": "Int", "width": 130},
		{"fieldname": "breakdown_trips", "label": _("Breakdown Trips"), "fieldtype": "Int", "width": 130},
		{"fieldname": "last_trip_date", "label": _("Last Trip Date"), "fieldtype": "Date", "width": 120},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)

	return frappe.db.sql(
		"""
		SELECT
			t.name AS truck,
			t.truck_number,
			t.status,
			(SELECT COUNT(*) FROM `tabTrips` WHERE truck_number = t.name) AS total_trips,
			(SELECT COUNT(*) FROM `tabTrips` WHERE truck_number = t.name AND trip_status = 'Completed') AS completed_trips,
			(SELECT COUNT(*) FROM `tabTrips` WHERE truck_number = t.name AND trip_status = 'Breakdown') AS breakdown_trips,
			(SELECT MAX(date) FROM `tabTrips` WHERE truck_number = t.name) AS last_trip_date
		FROM `tabTruck` t
		WHERE 1 = 1 """ + conditions + """
		ORDER BY total_trips DESC
		""",
		values,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("status"):
		conditions += " AND t.status = %(status)s"
		values["status"] = filters.get("status")

	return conditions, values
