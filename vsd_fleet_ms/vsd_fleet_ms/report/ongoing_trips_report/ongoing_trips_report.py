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
		{"fieldname": "date", "label": _("Trip Date"), "fieldtype": "Date", "width": 100},
		{"fieldname": "truck_number", "label": _("Truck"), "fieldtype": "Link", "options": "Truck", "width": 110},
		{"fieldname": "truck_licence_plate", "label": _("Plate Number"), "fieldtype": "Data", "width": 110},
		{"fieldname": "driver_name", "label": _("Driver"), "fieldtype": "Data", "width": 150},
		{"fieldname": "route", "label": _("Route"), "fieldtype": "Link", "options": "Trip Routes", "width": 150},
		{"fieldname": "transporter_type", "label": _("Transporter"), "fieldtype": "Data", "width": 110},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)

	return frappe.db.sql(
		"""
		SELECT name, date, truck_number, truck_licence_plate, driver_name, route, transporter_type
		FROM `tabTrips`
		WHERE trip_status = 'Pending' """ + conditions + """
		ORDER BY date DESC
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
