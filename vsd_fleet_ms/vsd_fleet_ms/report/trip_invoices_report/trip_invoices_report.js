// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Trip Invoices Report"] = {
	filters: [
		{
			fieldname: "invoice_status",
			label: __("Invoice Status"),
			fieldtype: "Select",
			options: "All\nPending\nOverdue\nPaid",
			default: "All"
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer"
		},
		{
			fieldname: "trip",
			label: __("Trip"),
			fieldtype: "Link",
			options: "Trips"
		},
		{
			fieldname: "cargo_registration",
			label: __("Cargo Registration"),
			fieldtype: "Link",
			options: "Cargo Registration"
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start()
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.now_date()
		}
	]
};
