# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors

import frappe


def before_tests():
	"""Run ERPNext's test setup on a fresh site (as in CI), where no company exists yet.

	ERPNext's hook also deletes all Item Prices, so it must never run on a site with data.
	"""
	if frappe.db.a_row_exists("Company"):
		return

	from erpnext.setup.utils import before_tests as erpnext_before_tests

	erpnext_before_tests()
