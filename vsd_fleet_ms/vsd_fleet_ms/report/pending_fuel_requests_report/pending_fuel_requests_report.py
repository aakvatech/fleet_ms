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
		{"fieldname": "name", "label": _("Fuel Request"), "fieldtype": "Link", "options": "Fuel Requests", "width": 150},
		{"fieldname": "transaction_date", "label": _("Transaction Date"), "fieldtype": "Date", "width": 110},
		{"fieldname": "truck", "label": _("Truck"), "fieldtype": "Link", "options": "Truck", "width": 110},
		{"fieldname": "driver_name", "label": _("Driver"), "fieldtype": "Data", "width": 150},
		{"fieldname": "main_route", "label": _("Main Route"), "fieldtype": "Link", "options": "Trip Routes", "width": 150},
		{"fieldname": "return_route", "label": _("Return Route"), "fieldtype": "Link", "options": "Trip Routes", "width": 150},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 130},
		{"fieldname": "requested_quantity", "label": _("Requested Quantity (Ltr)"), "fieldtype": "Float", "width": 160},
		{"fieldname": "requested_cost_tzs", "label": _("Requested Cost (TZS)"), "fieldtype": "Currency", "options": "TZS", "width": 150},
		{"fieldname": "requested_cost_usd", "label": _("Requested Cost (USD)"), "fieldtype": "Currency", "options": "USD", "width": 150},
		{"fieldname": "reference_doctype", "label": _("Reference Doctype"), "fieldtype": "Link", "options": "DocType", "width": 130},
		{"fieldname": "reference_docname", "label": _("Reference"), "fieldtype": "Dynamic Link", "options": "reference_doctype", "width": 150},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)

	return frappe.db.sql(
		"""
		SELECT
			fr.name AS name,
			COALESCE(fr.transaction_date, t.date) AS transaction_date,
			COALESCE(fr.truck, t.truck_number) AS truck,
			COALESCE(fr.driver_name, t.driver_name) AS driver_name,
			COALESCE(fr.main_route, t.route) AS main_route,
			fr.return_route,
			fr.status,
			fr.reference_doctype,
			fr.reference_docname,
			COALESCE((
				SELECT SUM(quantity)
				FROM `tabFuel Requests Table`
				WHERE parenttype = 'Fuel Requests' AND parentfield = 'requested_fuel' AND parent = fr.name
			), 0) + COALESCE((
				SELECT SUM(quantity)
				FROM `tabFuel Requests Table`
				WHERE parenttype = 'Trips' AND parentfield = 'fuel_request_history' AND parent = t.name
			), 0) AS requested_quantity,
			COALESCE((
				SELECT SUM(total_cost)
				FROM `tabFuel Requests Table`
				WHERE parenttype = 'Fuel Requests' AND parentfield = 'requested_fuel' AND parent = fr.name AND currency = 'TZS'
			), 0) + COALESCE((
				SELECT SUM(total_cost)
				FROM `tabFuel Requests Table`
				WHERE parenttype = 'Trips' AND parentfield = 'fuel_request_history' AND parent = t.name AND currency = 'TZS'
			), 0) AS requested_cost_tzs,
			COALESCE((
				SELECT SUM(total_cost)
				FROM `tabFuel Requests Table`
				WHERE parenttype = 'Fuel Requests' AND parentfield = 'requested_fuel' AND parent = fr.name AND currency = 'USD'
			), 0) + COALESCE((
				SELECT SUM(total_cost)
				FROM `tabFuel Requests Table`
				WHERE parenttype = 'Trips' AND parentfield = 'fuel_request_history' AND parent = t.name AND currency = 'USD'
			), 0) AS requested_cost_usd
		FROM `tabFuel Requests` fr
		LEFT JOIN `tabTrips` t ON fr.reference_doctype = 'Trips' AND fr.reference_docname = t.name
		WHERE fr.status != 'Fully Processed' """ + conditions + """
		ORDER BY transaction_date DESC
		""",
		values,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("status"):
		conditions += " AND fr.status = %(status)s"
		values["status"] = filters.get("status")

	if filters.get("truck"):
		conditions += " AND fr.truck = %(truck)s"
		values["truck"] = filters.get("truck")

	if filters.get("from_date"):
		conditions += " AND (COALESCE(fr.transaction_date, t.date) >= %(from_date)s OR COALESCE(fr.transaction_date, t.date) IS NULL)"
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions += " AND (COALESCE(fr.transaction_date, t.date) <= %(to_date)s OR COALESCE(fr.transaction_date, t.date) IS NULL)"
		values["to_date"] = filters.get("to_date")

	return conditions, values
