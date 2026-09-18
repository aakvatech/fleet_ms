// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Vehicle Utilization"] = {
	"filters": [
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nIdle\nUnder Maintenance\nOn Trip\nDisabled"
		}
	]
};
