# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors

"""Custom Fields this app adds to other doctypes, created from JSON batches.

Patches create them on existing sites. `bench install-app` marks patches as done
without running them, so the install hooks create the same batches on new sites.
Only missing fields are created; fields a site has edited are left as they are.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

TYRE_ITEM_FIELDS = "tyre_item_fields_20261015.json"
SERVICE_JOB_CARD_FIELDS = "service_job_card_fleet_fields_20261015.json"
TRIPS_SERVICE_JOB_CARD_FIELDS = "trips_service_job_card_fields_20261015.json"


def after_install():
	import_tyre_item_fields()
	import_servicems_fields()


def after_app_install(app_name):
	# ServiceMS may be installed after this app; its fields then need creating.
	if app_name == "servicems":
		import_servicems_fields()


def import_tyre_item_fields():
	import_custom_fields(TYRE_ITEM_FIELDS)


def import_servicems_fields():
	"""Service Job Card fields, and Trips links to it. Skipped when ServiceMS is absent."""
	# Trips links to Service Job Card, so it also waits for ServiceMS.
	if not frappe.db.exists("DocType", "Service Job Card"):
		return
	import_custom_fields(SERVICE_JOB_CARD_FIELDS)
	import_custom_fields(TRIPS_SERVICE_JOB_CARD_FIELDS)


def import_custom_fields(file_name):
	fields_by_doctype = {}
	for field in load_batch(file_name):
		field = dict(field)
		fields_by_doctype.setdefault(field.pop("dt"), []).append(field)

	# update=False keeps any field that already exists, including site edits.
	create_custom_fields(fields_by_doctype, update=False)


def load_batch(file_name):
	path = frappe.get_app_path("vsd_fleet_ms", "patches", "custom_fields", "custom_field_json", file_name)
	return frappe.get_file_json(path)
