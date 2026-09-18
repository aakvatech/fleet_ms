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
		{"fieldname": "reference", "label": _("Trip"), "fieldtype": "Link", "options": "Trips", "width": 130},
		{"fieldname": "date", "label": _("Trip Date"), "fieldtype": "Date", "width": 100},
		{"fieldname": "route", "label": _("Route"), "fieldtype": "Link", "options": "Trip Routes", "width": 150},
		{"fieldname": "invoice_count", "label": _("Invoices"), "fieldtype": "Int", "width": 90},
		{"fieldname": "revenue_usd", "label": _("Revenue (USD)"), "fieldtype": "Currency", "options": "USD", "width": 130},
		{"fieldname": "revenue_tzs", "label": _("Revenue (TZS)"), "fieldtype": "Currency", "options": "TZS", "width": 130},
	]


def get_data(filters):
	# Revenue is booked through Cargo Registration: Trip -> Cargo Registration -> Cargo Detail -> Sales Invoice
	conditions, values = get_conditions(filters)

	return frappe.db.sql(
		"""
		SELECT
			t.name AS reference,
			t.date,
			t.route,
			COUNT(DISTINCT si.name) AS invoice_count,
			SUM(CASE WHEN si.currency = 'USD' THEN si.grand_total ELSE 0 END) AS revenue_usd,
			SUM(CASE WHEN si.currency = 'TZS' THEN si.grand_total ELSE 0 END) AS revenue_tzs
		FROM `tabTrips` t
		INNER JOIN `tabCargo Registration` cr ON cr.trip = t.name
		INNER JOIN `tabCargo Detail` cd ON cd.parent = cr.name AND cd.invoice IS NOT NULL AND cd.invoice != ''
		INNER JOIN `tabSales Invoice` si ON si.name = cd.invoice AND si.docstatus = 1
		WHERE 1 = 1 """ + conditions + """
		GROUP BY t.name
		ORDER BY t.date DESC
		""",
		values,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("from_date"):
		conditions += " AND t.date >= %(from_date)s"
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions += " AND t.date <= %(to_date)s"
		values["to_date"] = filters.get("to_date")

	return conditions, values
