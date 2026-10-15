import frappe


def execute():
	"""Clear the vehicle type that new tyres got by default although they are not fitted.

	The Select field had no blank option, so every new tyre was stored as "Truck".
	"""
	tyre = frappe.qb.DocType("Tyre Master")
	(
		frappe.qb.update(tyre)
		.set(tyre.current_vehicle_type, "")
		.where(tyre.status != "In Service")
		.where(tyre.current_vehicle.isnull() | (tyre.current_vehicle == ""))
	).run()
