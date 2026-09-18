import glob
import os

import frappe
from frappe.modules.import_file import import_file_by_path


def execute():
	"""Bring any site's Fleet MS workspace in line with the new Fleet Management layout.

	Runs in pre_model_sync so the rename happens before the standard fixture sync
	tries to import the "Fleet Management" workspace file - otherwise a site that
	still has the old "Fleet MS" doc would end up with both, side by side.
	"""
	if frappe.db.exists("Workspace", "Fleet MS") and not frappe.db.exists("Workspace", "Fleet Management"):
		frappe.rename_doc("Workspace", "Fleet MS", "Fleet Management", ignore_permissions=True)
		frappe.db.set_value("Workspace", "Fleet Management", "label", "Fleet Management")

	frappe.flags.in_migrate = True
	for old_report in ("Fuel Expense By Trip", "Truck Status Report"):
		if frappe.db.exists("Report", old_report):
			frappe.delete_doc("Report", old_report, force=True, ignore_permissions=True)

	# Number Card fixtures for this app are not picked up by the generic module sync
	# (frappe.model.sync only scans a fixed doctype list that excludes "number_card"
	# for non-core apps), so import them explicitly here - before the workspace
	# fixture syncs and tries to link to them.
	app_path = frappe.get_app_path("vsd_fleet_ms", "vsd_fleet_ms")
	for path in sorted(glob.glob(os.path.join(app_path, "number_card", "*", "*.json"))):
		import_file_by_path(path, force=True)

	frappe.db.commit()
