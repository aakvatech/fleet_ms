import frappe

STATUS_BY_LOWER = {s.lower(): s for s in ("In Store", "In Service", "Under Repair", "Scrapped")}


def execute():
	"""Link tyres created before the item remodel to their Serial No where one exists.

	Tyres with no matching Serial No stay as legacy records: movements and
	inspections still work, but they are not moved in stock.
	"""
	for tyre in frappe.get_all(
		"Tyre Master",
		filters={"serial_no": ["is", "not set"]},
		fields=["name", "status", "last_odometer_km"],
	):
		values = {}
		# Some old records hold free-typed statuses such as "In service".
		status = STATUS_BY_LOWER.get((tyre.status or "").lower(), "In Store")
		if status != tyre.status:
			values["status"] = status
			tyre.status = status

		item_code = frappe.db.get_value("Serial No", tyre.name, "item_code")
		if item_code:
			values.update({"serial_no": tyre.name, "tyre_item": item_code})
			# The item already holds tyre serials, so it is a tyre item.
			frappe.db.set_value("Item", item_code, "is_tyre", 1, update_modified=False)

		# Usage now runs from the fitment reading; the last reading is the best estimate.
		if tyre.status == "In Service":
			values["install_odometer_km"] = tyre.last_odometer_km

		if values:
			frappe.db.set_value("Tyre Master", tyre.name, values, update_modified=False)
