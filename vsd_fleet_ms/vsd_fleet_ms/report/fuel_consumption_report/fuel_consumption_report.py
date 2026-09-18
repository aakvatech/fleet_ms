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
		{"fieldname": "truck_number", "label": _("Truck"), "fieldtype": "Link", "options": "Truck", "width": 120},
		{"fieldname": "trip_count", "label": _("Trips"), "fieldtype": "Int", "width": 90},
		{"fieldname": "total_quantity", "label": _("Total Fuel (Ltr)"), "fieldtype": "Float", "width": 130},
		{"fieldname": "total_cost_tzs", "label": _("Total Cost (TZS)"), "fieldtype": "Currency", "options": "TZS", "width": 140},
		{"fieldname": "total_cost_usd", "label": _("Total Cost (USD)"), "fieldtype": "Currency", "options": "USD", "width": 140},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)

	return frappe.db.sql(
		"""
		SELECT
			t.truck_number,
			COUNT(DISTINCT t.name) AS trip_count,
			SUM(f.quantity) AS total_quantity,
			SUM(CASE WHEN f.currency = 'TZS' THEN f.total_cost ELSE 0 END) AS total_cost_tzs,
			SUM(CASE WHEN f.currency = 'USD' THEN f.total_cost ELSE 0 END) AS total_cost_usd
		FROM `tabTrips` t
		INNER JOIN `tabFuel Requests Table` f
			ON f.parent = t.name AND f.parentfield = 'fuel_request_history'
		WHERE t.truck_number IS NOT NULL AND t.truck_number != '' """ + conditions + """
		GROUP BY t.truck_number
		ORDER BY total_quantity DESC
		""",
		values,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("truck_number"):
		conditions += " AND t.truck_number = %(truck_number)s"
		values["truck_number"] = filters.get("truck_number")

	if filters.get("from_date"):
		conditions += " AND t.date >= %(from_date)s"
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions += " AND t.date <= %(to_date)s"
		values["to_date"] = filters.get("to_date")

	return conditions, values
