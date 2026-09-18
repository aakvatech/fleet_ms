# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data, None, None


def get_columns():
	return [
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Select", "width": 150},
		{"fieldname": "truck_count", "label": _("Number of Trucks"), "fieldtype": "Int", "width": 150},
	]


def get_data():
	return frappe.db.sql(
		"""
		SELECT status, COUNT(*) AS truck_count
		FROM `tabTruck`
		GROUP BY status
		ORDER BY truck_count DESC
		""",
		as_dict=1,
	)
