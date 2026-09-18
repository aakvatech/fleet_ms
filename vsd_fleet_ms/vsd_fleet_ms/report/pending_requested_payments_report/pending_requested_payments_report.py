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
		{"fieldname": "reference", "label": _("Requested Payment"), "fieldtype": "Link", "options": "Requested Payment", "width": 160},
		{"fieldname": "request_date", "label": _("Request Date"), "fieldtype": "Date", "width": 110},
		{"fieldname": "truck_no", "label": _("Truck"), "fieldtype": "Link", "options": "Truck", "width": 110},
		{"fieldname": "driver_name", "label": _("Driver"), "fieldtype": "Data", "width": 150},
		{"fieldname": "trip_route", "label": _("Route"), "fieldtype": "Link", "options": "Trip Routes", "width": 150},
		{"fieldname": "manifest", "label": _("Manifest"), "fieldtype": "Link", "options": "Manifest", "width": 130},
		{"fieldname": "approval_status", "label": _("Approval Status"), "fieldtype": "Data", "width": 130},
		{"fieldname": "payment_status", "label": _("Payment Status"), "fieldtype": "Data", "width": 130},
		{"fieldname": "requested_usd", "label": _("Requested (USD)"), "fieldtype": "Currency", "options": "USD", "width": 130},
		{"fieldname": "requested_tzs", "label": _("Requested (TZS)"), "fieldtype": "Currency", "options": "TZS", "width": 130},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)

	return frappe.db.sql(
		"""
		SELECT
			rp.name AS reference,
			rp.request_date,
			rp.truck_no,
			rp.driver_name,
			rp.trip_route,
			rp.manifest,
			rp.approval_status,
			rp.payment_status,
			(
				SELECT SUM(request_amount)
				FROM `tabRequested Fund Details`
				WHERE parenttype = rp.reference_doctype AND parent = rp.reference_docname AND request_currency = 'USD'
			) AS requested_usd,
			(
				SELECT SUM(request_amount)
				FROM `tabRequested Fund Details`
				WHERE parenttype = rp.reference_doctype AND parent = rp.reference_docname AND request_currency = 'TZS'
			) AS requested_tzs
		FROM `tabRequested Payment` rp
		WHERE rp.payment_status != 'Paid' """ + conditions + """
		ORDER BY rp.request_date DESC
		""",
		values,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("approval_status"):
		conditions += " AND rp.approval_status = %(approval_status)s"
		values["approval_status"] = filters.get("approval_status")

	if filters.get("payment_status"):
		conditions += " AND rp.payment_status = %(payment_status)s"
		values["payment_status"] = filters.get("payment_status")

	if filters.get("truck_no"):
		conditions += " AND rp.truck_no = %(truck_no)s"
		values["truck_no"] = filters.get("truck_no")

	if filters.get("from_date"):
		conditions += " AND rp.request_date >= %(from_date)s"
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions += " AND rp.request_date <= %(to_date)s"
		values["to_date"] = filters.get("to_date")

	return conditions, values
