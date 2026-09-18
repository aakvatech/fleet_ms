# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}

	if filters.get("from_date") and filters.get("to_date") and filters.get("from_date") > filters.get("to_date"):
		frappe.throw(_("From Date must be before To Date {0}").format(filters.get("to_date")))

	columns = get_columns()
	data = get_data(filters)
	return columns, data, None, None


def get_columns():
	return [
		{"fieldname": "reference", "label": _("Trip"), "fieldtype": "Link", "options": "Trips", "width": 130},
		{"fieldname": "posting_date", "label": _("Trip Date"), "fieldtype": "Date", "width": 100},
		{"fieldname": "transporter_name", "label": _("Transporter"), "fieldtype": "Data", "width": 160},
		{"fieldname": "vehicle_plate_number", "label": _("Vehicle"), "fieldtype": "Data", "width": 110},
		{"fieldname": "driver_name", "label": _("Driver"), "fieldtype": "Data", "width": 150},
		{"fieldname": "route", "label": _("Route"), "fieldtype": "Data", "width": 150},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 110},
		{"fieldname": "revenue_usd", "label": _("Revenue (USD)"), "fieldtype": "Currency", "options": "USD", "width": 120},
		{"fieldname": "expenses_usd", "label": _("Expenses (USD)"), "fieldtype": "Currency", "options": "USD", "width": 120},
		{"fieldname": "profit_usd", "label": _("Profit (USD)"), "fieldtype": "Currency", "options": "USD", "width": 120},
		{"fieldname": "revenue_tzs", "label": _("Revenue (TZS)"), "fieldtype": "Currency", "options": "TZS", "width": 130},
		{"fieldname": "expenses_tzs", "label": _("Expenses (TZS)"), "fieldtype": "Currency", "options": "TZS", "width": 130},
		{"fieldname": "profit_tzs", "label": _("Profit (TZS)"), "fieldtype": "Currency", "options": "TZS", "width": 130},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)

	rows = frappe.db.sql(
		"""
		SELECT
			`tabTrips`.name AS reference,
			`tabTrips`.date AS posting_date,
			`tabTrips`.trip_status AS status,
			IF(`tabTrips`.transporter_type = 'In House', '', `tabTrips`.sub_contractor_name) AS transporter_name,
			IF(`tabTrips`.transporter_type = 'In House', `tabTrips`.truck_licence_plate, `tabTrips`.sub_contactor_truck_license_plate_no) AS vehicle_plate_number,
			IF(`tabTrips`.transporter_type = 'In House', `tabTrips`.driver_name, `tabTrips`.sub_contactor_driver_name) AS driver_name,
			`tabTrips`.route AS route,
			(
				SELECT SUM(cd.rate)
				FROM `tabCargo Detail` cd
				INNER JOIN `tabCargo Registration` cr ON cd.parent = cr.name
				WHERE cr.trip = `tabTrips`.name AND cd.currency = 'USD'
			) AS revenue_usd,
			(
				SELECT SUM(cd.rate)
				FROM `tabCargo Detail` cd
				INNER JOIN `tabCargo Registration` cr ON cd.parent = cr.name
				WHERE cr.trip = `tabTrips`.name AND cd.currency = 'TZS'
			) AS revenue_tzs,
			(
				SELECT SUM(request_amount)
				FROM `tabRequested Fund Details`
				WHERE parenttype = 'Trips' AND parent = `tabTrips`.name AND request_currency = 'USD' AND request_status = 'Approved'
			) AS fund_expenses_usd,
			(
				SELECT SUM(request_amount)
				FROM `tabRequested Fund Details`
				WHERE parenttype = 'Trips' AND parent = `tabTrips`.name AND request_currency = 'TZS' AND request_status = 'Approved'
			) AS fund_expenses_tzs,
			(
				SELECT SUM(total_cost)
				FROM `tabFuel Requests Table`
				WHERE parenttype = 'Trips' AND parentfield = 'fuel_request_history' AND parent = `tabTrips`.name AND currency = 'USD'
			) AS fuel_expenses_usd,
			(
				SELECT SUM(total_cost)
				FROM `tabFuel Requests Table`
				WHERE parenttype = 'Trips' AND parentfield = 'fuel_request_history' AND parent = `tabTrips`.name AND currency = 'TZS'
			) AS fuel_expenses_tzs
		FROM `tabTrips`
		WHERE 1 = 1 """ + conditions + """
		""",
		values,
		as_dict=1,
	)

	data = []
	for row in rows:
		revenue_usd = row.revenue_usd or 0
		revenue_tzs = row.revenue_tzs or 0
		expenses_usd = (row.fund_expenses_usd or 0) + (row.fuel_expenses_usd or 0)
		expenses_tzs = (row.fund_expenses_tzs or 0) + (row.fuel_expenses_tzs or 0)

		data.append({
			"reference": row.reference,
			"posting_date": row.posting_date,
			"transporter_name": row.transporter_name,
			"vehicle_plate_number": row.vehicle_plate_number,
			"driver_name": row.driver_name,
			"route": row.route,
			"status": row.status,
			"revenue_usd": revenue_usd,
			"expenses_usd": expenses_usd,
			"profit_usd": revenue_usd - expenses_usd,
			"revenue_tzs": revenue_tzs,
			"expenses_tzs": expenses_tzs,
			"profit_tzs": revenue_tzs - expenses_tzs,
		})

	return data


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("status"):
		conditions += " AND `tabTrips`.trip_status = %(status)s"
		values["status"] = filters.get("status")

	if filters.get("from_date"):
		conditions += " AND `tabTrips`.date >= %(from_date)s"
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions += " AND `tabTrips`.date <= %(to_date)s"
		values["to_date"] = filters.get("to_date")

	return conditions, values
