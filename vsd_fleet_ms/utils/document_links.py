import frappe


def _joined_refs(values):
    refs = sorted({value for value in values if value})
    return ", ".join(refs)


def sync_cargo_registration_links(doc):
    manifests = {row.manifest_number for row in (doc.cargo_details or []) if row.manifest_number}
    trips = {row.created_trip for row in (doc.cargo_details or []) if row.created_trip}
    doc.manifest = next(iter(manifests)) if len(manifests) == 1 else ""
    doc.trip = next(iter(trips)) if len(trips) == 1 else ""
