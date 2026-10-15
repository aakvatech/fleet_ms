import frappe


def execute():
	"""Move Service Job Card `custom_trailer` values into `trailer`, then drop the old field.

	Runs after the patch that creates `trailer`. Sites without ServiceMS have neither field.
	"""
	old_field = frappe.db.get_value("Custom Field", {"dt": "Service Job Card", "fieldname": "custom_trailer"})
	if not old_field or not frappe.db.has_column("Service Job Card", "trailer"):
		return

	job_card = frappe.qb.DocType("Service Job Card")
	(
		frappe.qb.update(job_card)
		.set(job_card.trailer, job_card.custom_trailer)
		.where(job_card.custom_trailer.isnotnull() & (job_card.custom_trailer != ""))
		.where(job_card.trailer.isnull() | (job_card.trailer == ""))
	).run()

	frappe.delete_doc("Custom Field", old_field, ignore_permissions=True)
