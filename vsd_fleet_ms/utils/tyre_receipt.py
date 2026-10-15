# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors

"""Tyres entering stock: receiving warehouse check and Tyre Master creation.

Hooked on Purchase Receipt, Purchase Invoice (with Update Stock) and Stock Entry.
"""

import frappe
from frappe import _


def validate_tyre_receipt_warehouse(doc, method=None):
	"""validate: new tyres must land in the Tyre Store warehouse when stock integration is on."""
	if not brings_stock_in(doc):
		return
	store = get_store_warehouse(doc.company)
	if not store:
		return

	errors = [
		_("Row {0}: {1} is received into {2}").format(row.idx, row.item_code, receipt_warehouse(doc, row))
		for row in received_tyre_rows(doc)
		if receipt_warehouse(doc, row) != store
	]
	if errors:
		frappe.throw(
			"<br>".join(errors)
			+ "<br><br>"
			+ _(
				"New tyres must be received into the Tyre Store warehouse {0} (Tyre Management Settings)."
			).format(frappe.bold(store)),
			title=_("Wrong Tyre Warehouse"),
		)


def create_tyres_from_receipt(doc, method=None):
	"""on_submit: create a Tyre Master per received tyre serial."""
	if not brings_stock_in(doc) or not is_auto_create_enabled():
		return

	for row in received_tyre_rows(doc):
		for serial_no in get_row_serial_nos(row):
			create_tyre(row.item_code, serial_no, row.valuation_rate)


@frappe.whitelist()
def get_tyre_store_warehouse(item_code: str, company: str) -> str | None:
	"""Default receiving warehouse for a tyre item, used by the receipt form scripts."""
	if not item_code or not is_tyre_item(item_code):
		return None
	return get_store_warehouse(company)


def create_tyre(item_code, serial_no, purchase_cost=0):
	# Legacy tyres are named by serial but may have no serial_no link.
	if frappe.db.exists("Tyre Master", serial_no) or frappe.db.exists(
		"Tyre Master", {"serial_no": serial_no}
	):
		return None

	tyre = frappe.new_doc("Tyre Master")
	tyre.tyre_item = item_code
	tyre.serial_no = serial_no
	tyre.status = "In Store"
	tyre.purchase_cost = purchase_cost
	tyre.insert(ignore_permissions=True)
	return tyre


def get_store_warehouse(company):
	"""Tyre Store warehouse, only when stock integration is on for this company."""
	settings = frappe.get_single("Tyre Management Settings")
	if settings.enable_stock_integration and settings.company == company:
		return settings.store_warehouse
	return None


def is_auto_create_enabled():
	# Nothing is stored until the settings page is first saved; the field default is on.
	value = frappe.db.get_single_value("Tyre Management Settings", "auto_create_tyres")
	return value is None or bool(value)


def brings_stock_in(doc):
	# A Purchase Invoice made from a receipt is only the bill; the receipt brought the tyres in.
	return doc.doctype != "Purchase Invoice" or bool(doc.update_stock)


def received_tyre_rows(doc):
	return [row for row in doc.items if is_received_row(doc, row) and is_tyre_item(row.item_code)]


def is_received_row(doc, row):
	if doc.doctype == "Stock Entry":
		# Transfers move existing tyres; only rows without a source bring new serials in.
		return bool(row.t_warehouse) and not row.s_warehouse
	return not doc.get("is_return") and bool(row.get("warehouse"))


def receipt_warehouse(doc, row):
	return row.t_warehouse if doc.doctype == "Stock Entry" else row.warehouse


def is_tyre_item(item_code):
	return bool(frappe.get_cached_value("Item", item_code, "is_tyre"))


def get_row_serial_nos(row):
	from erpnext.stock.serial_batch_bundle import get_serial_nos_from_bundle

	if row.get("serial_and_batch_bundle"):
		return get_serial_nos_from_bundle(row.serial_and_batch_bundle)

	from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

	return get_serial_nos(row.get("serial_no"))
