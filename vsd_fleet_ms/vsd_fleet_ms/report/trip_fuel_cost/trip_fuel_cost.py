# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data, None


def get_columns():
	return [
		{"fieldname": "vehicle_trip", "fieldtype": "Link", "label": _("Vehicle Trip"), "options": "Trips"},
		{"fieldname": "date", "fieldtype": "Date", "label": _("Trip Date")},
		{"fieldname": "driver_name", "fieldtype": "Data", "label": _("Driver Name")},
		{"fieldname": "truck_number", "fieldtype": "Data", "label": _("Truck Number")},
		{"fieldname": "transporter_type", "fieldtype": "Data", "label": _("Transporter Type")},
		{"fieldname": "trip_status", "fieldtype": "Data", "label": _("Trip Status")},
		{"fieldname": "route", "fieldtype": "Link", "label": _("Route"), "options": "Trip Routes"},
		{"fieldname": "item_name", "fieldtype": "Data", "label": _("Item Name")},
		{"fieldname": "uom", "fieldtype": "Data", "label": _("UOM")},
		{"fieldname": "quantity", "fieldtype": "Float", "label": _("Quantity")},
		{"fieldname": "cost_per_litre", "fieldtype": "Float", "label": _("Cost Per Litre")},
		{"fieldname": "currency", "fieldtype": "Link", "label": _("Currency"), "options": "Currency"},
		{"fieldname": "total_cost", "fieldtype": "Currency", "label": _("Total Cost"), "options": "currency"},
		{"fieldname": "disbursement_type", "fieldtype": "Data", "label": _("Disbursement Type")},
		{"fieldname": "supplier", "fieldtype": "Link", "label": _("Supplier"), "options": "Supplier"},
		{"fieldname": "status", "fieldtype": "Data", "label": _("Status")},
		{"fieldname": "approved_by", "fieldtype": "Data", "label": _("Approved By")},
		{"fieldname": "approved_date", "fieldtype": "Date", "label": _("Approved Date")},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)

	rows = frappe.db.sql(
		"""
		SELECT
			T.name AS vehicle_trip, T.date, T.driver_name, T.truck_number, T.transporter_type,
			T.trip_status, T.route,
			FL.item_name, FL.uom, FL.quantity, FL.cost_per_litre, FL.currency, FL.total_cost,
			FL.disbursement_type, FL.supplier, FL.status, FL.approved_by, FL.approved_date
		FROM `tabTrips` T
		INNER JOIN `tabFuel Requests Table` FL ON FL.parent = T.name AND FL.parentfield = 'fuel_request_history'
		WHERE 1 = 1 """ + conditions + """
		ORDER BY T.date DESC
		""",
		values,
		as_dict=True,
	)
	return rows


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("truck_number"):
		conditions += " AND T.truck_number = %(truck_number)s"
		values["truck_number"] = filters.get("truck_number")

	if filters.get("from_date"):
		conditions += " AND T.date >= %(from_date)s"
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions += " AND T.date <= %(to_date)s"
		values["to_date"] = filters.get("to_date")

	return conditions, values
