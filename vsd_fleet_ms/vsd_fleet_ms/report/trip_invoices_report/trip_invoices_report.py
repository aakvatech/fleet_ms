import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "name", "label": _("Sales Invoice"), "fieldtype": "Link", "options": "Sales Invoice", "width": 130},
		{"fieldname": "invoice_status", "label": _("Status"), "fieldtype": "Data", "width": 100},
		{"fieldname": "trip", "label": _("Trip"), "fieldtype": "Link", "options": "Trips", "width": 120},
		{"fieldname": "cargo_registration", "label": _("Cargo Registration"), "fieldtype": "Link", "options": "Cargo Registration", "width": 150},
		{"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Customer", "width": 160},
		{"fieldname": "posting_date", "label": _("Posting Date"), "fieldtype": "Date", "width": 110},
		{"fieldname": "due_date", "label": _("Due Date"), "fieldtype": "Date", "width": 110},
		{"fieldname": "days_overdue", "label": _("Days Overdue"), "fieldtype": "Int", "width": 110},
		{"fieldname": "grand_total", "label": _("Grand Total"), "fieldtype": "Currency", "options": "currency", "width": 130},
		{"fieldname": "outstanding_amount", "label": _("Outstanding Amount"), "fieldtype": "Currency", "options": "currency", "width": 150},
		{"fieldname": "currency", "label": _("Currency"), "fieldtype": "Link", "options": "Currency", "width": 90},
	]


def get_data(filters):
	conditions, values = get_conditions(filters)
	values["today"] = nowdate()

	return frappe.db.sql(
		"""
		SELECT DISTINCT
			si.name,
			CASE
				WHEN si.outstanding_amount = 0 THEN 'Paid'
				WHEN si.due_date < %(today)s THEN 'Overdue'
				ELSE 'Pending'
			END AS invoice_status,
			cr.trip,
			cr.name AS cargo_registration,
			si.customer, si.posting_date, si.due_date,
			GREATEST(DATEDIFF(%(today)s, si.due_date), 0) AS days_overdue,
			si.grand_total, si.outstanding_amount, si.currency
		FROM `tabSales Invoice` si
		INNER JOIN `tabCargo Detail` cd ON cd.invoice = si.name
		INNER JOIN `tabCargo Registration` cr ON cr.name = cd.parent
		WHERE si.docstatus = 1
		"""
		+ conditions
		+ """
		ORDER BY si.due_date ASC
		""",
		values,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("invoice_status") == "Pending":
		conditions += " AND si.outstanding_amount > 0 AND si.due_date >= %(today)s"
	elif filters.get("invoice_status") == "Overdue":
		conditions += " AND si.outstanding_amount > 0 AND si.due_date < %(today)s"
	elif filters.get("invoice_status") == "Paid":
		conditions += " AND si.outstanding_amount = 0"

	for field, condition in (
		("customer", " AND si.customer = %(customer)s"),
		("trip", " AND cr.trip = %(trip)s"),
		("cargo_registration", " AND cr.name = %(cargo_registration)s"),
	):
		if filters.get(field):
			conditions += condition
			values[field] = filters[field]

	if filters.get("from_date"):
		conditions += " AND si.posting_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions += " AND si.posting_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]

	return conditions, values
