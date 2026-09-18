import frappe


def execute():
	for report in ("Unpaid Invoices Report", "Overdue Invoices Report"):
		if frappe.db.exists("Report", report):
			frappe.delete_doc("Report", report, force=True, ignore_permissions=True)
