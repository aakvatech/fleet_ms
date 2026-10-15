# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors

"""Tyre items: validation of the Item fields added by this app."""

import frappe
from frappe import _


def validate_tyre_item(doc, method=None):
	"""Item.validate: a tyre must be a serialised stock item."""
	if not doc.get("is_tyre"):
		return
	if not doc.is_stock_item or not doc.has_serial_no:
		frappe.throw(_("Tyre item {0} must have Maintain Stock and Has Serial No enabled").format(doc.name))
