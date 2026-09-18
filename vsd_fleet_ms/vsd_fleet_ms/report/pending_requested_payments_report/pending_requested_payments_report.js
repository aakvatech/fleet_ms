// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Pending Requested Payments Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.now_date()
		},
		{
			"fieldname": "truck_no",
			"label": __("Truck"),
			"fieldtype": "Link",
			"options": "Truck"
		},
		{
			"fieldname": "approval_status",
			"label": __("Approval Status"),
			"fieldtype": "Select",
			"options": "\nWaiting Approval\nProcessed"
		},
		{
			"fieldname": "payment_status",
			"label": __("Payment Status"),
			"fieldtype": "Select",
			"options": "\nWaiting Approval\nWaiting Payment\nPaid"
		}
	]
};
