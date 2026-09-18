// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Pending Fuel Requests Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "truck",
			"label": __("Truck"),
			"fieldtype": "Link",
			"options": "Truck"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nWaiting Approval\nPartially Processed"
		}
	]
};
