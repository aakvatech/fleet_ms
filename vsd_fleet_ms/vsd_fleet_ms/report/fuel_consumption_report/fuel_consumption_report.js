// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Fuel Consumption Report"] = {
	"filters": [
		{
			"fieldname": "truck_number",
			"label": __("Truck"),
			"fieldtype": "Link",
			"options": "Truck"
		},
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
		}
	]
};
