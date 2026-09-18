import frappe
from frappe.modules.import_file import import_file_by_path


def execute():
	path = frappe.get_app_path("vsd_fleet_ms", "vsd_fleet_ms", "workspace", "fleet_management", "fleet_management.json")
	import_file_by_path(path, force=True)
