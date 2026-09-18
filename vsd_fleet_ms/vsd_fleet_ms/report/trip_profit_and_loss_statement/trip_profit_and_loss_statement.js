// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Trip Profit and Loss Statement"] = {
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
			"fieldname": "status",
			"label": __("Trip Status"),
			"fieldtype": "Select",
			"options": "\nPending\nCompleted\nBreakdown"
		}
	]
};
