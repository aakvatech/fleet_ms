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
		{"fieldname": "name", "label": _("Trip"), "fieldtype": "Link", "options": "Trips", "width": 130},
		{"fieldname": "truck_number", "label": _("Truck"), "fieldtype": "Link", "options": "Truck", "width": 110},
		{"fieldname": "driver_name", "label": _("Driver"), "fieldtype": "Data", "width": 150},
		{"fieldname": "route", "label": _("Route"), "fieldtype": "Link", "options": "Trip Routes", "width": 150},
		{"fieldname": "date", "label": _("Start Date"), "fieldtype": "Date", "width": 100},
		{"fieldname": "trip_completed_date", "label": _("Completed Date"), "fieldtype": "Date", "width": 120},
		{"fieldname": "days_taken", "label": _("Days Taken"), "fieldtype": "Int", "width": 100},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)

	return frappe.db.sql(
		"""
		SELECT
			name, truck_number, driver_name, route, date, trip_completed_date,
			DATEDIFF(trip_completed_date, date) AS days_taken
		FROM `tabTrips`
		WHERE trip_status = 'Completed' AND date IS NOT NULL AND trip_completed_date IS NOT NULL """ + conditions + """
		ORDER BY days_taken DESC
		""",
		values,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("truck_number"):
		conditions += " AND truck_number = %(truck_number)s"
		values["truck_number"] = filters.get("truck_number")

	if filters.get("from_date"):
		conditions += " AND date >= %(from_date)s"
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions += " AND date <= %(to_date)s"
		values["to_date"] = filters.get("to_date")

	return conditions, values
