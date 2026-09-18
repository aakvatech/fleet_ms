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
		{"fieldname": "expense_type", "label": _("Expense"), "fieldtype": "Link", "options": "Fixed Expenses", "width": 200},
		{"fieldname": "request_count", "label": _("Number of Requests"), "fieldtype": "Int", "width": 140},
		{"fieldname": "total_tzs", "label": _("Total (TZS)"), "fieldtype": "Currency", "options": "TZS", "width": 130},
		{"fieldname": "total_usd", "label": _("Total (USD)"), "fieldtype": "Currency", "options": "USD", "width": 130},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)

	return frappe.db.sql(
		"""
		SELECT
			expense_type,
			COUNT(*) AS request_count,
			SUM(CASE WHEN request_currency = 'TZS' THEN request_amount ELSE 0 END) AS total_tzs,
			SUM(CASE WHEN request_currency = 'USD' THEN request_amount ELSE 0 END) AS total_usd
		FROM `tabRequested Fund Details`
		WHERE expense_type IS NOT NULL AND expense_type != '' """ + conditions + """
		GROUP BY expense_type
		ORDER BY total_tzs DESC
		""",
		values,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("expense_type"):
		conditions += " AND expense_type = %(expense_type)s"
		values["expense_type"] = filters.get("expense_type")

	if filters.get("from_date"):
		conditions += " AND requested_date >= %(from_date)s"
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions += " AND requested_date <= %(to_date)s"
		values["to_date"] = filters.get("to_date")

	return conditions, values
