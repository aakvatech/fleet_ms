import frappe


def get_transport_company(fallback_company=None):
    transport_company = frappe.db.get_single_value("Transport Settings", "company")
    default_company = frappe.defaults.get_global_default("company")
    return transport_company or default_company or fallback_company


def set_company_from_transport_settings(doc, method=None):
    doc.company = get_transport_company(doc.get("company"))
