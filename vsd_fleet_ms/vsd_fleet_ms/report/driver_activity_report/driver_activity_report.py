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
		{"fieldname": "driver", "label": _("Driver"), "fieldtype": "Link", "options": "Truck Driver", "width": 130},
		{"fieldname": "full_name", "label": _("Full Name"), "fieldtype": "Data", "width": 150},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Select", "width": 100},
		{"fieldname": "current_truck", "label": _("Current Truck"), "fieldtype": "Link", "options": "Truck", "width": 120},
		{"fieldname": "total_trips", "label": _("Total Trips"), "fieldtype": "Int", "width": 100},
		{"fieldname": "completed_trips", "label": _("Completed Trips"), "fieldtype": "Int", "width": 130},
		{"fieldname": "pending_trips", "label": _("Pending Trips"), "fieldtype": "Int", "width": 110},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)

	return frappe.db.sql(
		"""
		SELECT
			d.name AS driver,
			d.full_name,
			d.status,
			(SELECT tr.name FROM `tabTruck` tr WHERE tr.trans_ms_driver = d.name LIMIT 1) AS current_truck,
			(SELECT COUNT(*) FROM `tabTrips` WHERE assigned_driver = d.name) AS total_trips,
			(SELECT COUNT(*) FROM `tabTrips` WHERE assigned_driver = d.name AND trip_status = 'Completed') AS completed_trips,
			(SELECT COUNT(*) FROM `tabTrips` WHERE assigned_driver = d.name AND trip_status = 'Pending') AS pending_trips
		FROM `tabTruck Driver` d
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
		conditions += " AND d.status = %(status)s"
		values["status"] = filters.get("status")

	return conditions, values
