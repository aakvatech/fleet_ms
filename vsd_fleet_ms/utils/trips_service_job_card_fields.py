import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def ensure_trips_service_job_card_fields():
    """Create ServiceMS-linked fields on Trips only when ServiceMS exists.

    Safe to run repeatedly on migrate/install and on sites where ServiceMS is absent.
    """
    if "servicems" not in frappe.get_installed_apps():
        return

    if not frappe.db.exists("DocType", "Service Job Card"):
        return

    if not frappe.db.exists("DocType", "Trips"):
        return

    create_custom_fields(
        {
            "Trips": [
                {
                    "fieldname": "service_job_card",
                    "label": "Service Job Card",
                    "fieldtype": "Link",
                    "options": "Service Job Card",
                    "insert_after": "costing_section",
                },
                {
                    "fieldname": "column_break_service_job_card",
                    "fieldtype": "Column Break",
                    "insert_after": "service_job_card",
                },
                {
                    "fieldname": "service_charges",
                    "label": "Service Charges",
                    "fieldtype": "Currency",
                    "fetch_from": "service_job_card.service_charges",
                    "read_only": 1,
                    "insert_after": "column_break_service_job_card",
                },
                {
                    "fieldname": "spares_cost",
                    "label": "Spares Cost",
                    "fieldtype": "Currency",
                    "fetch_from": "service_job_card.spares_cost",
                    "read_only": 1,
                    "insert_after": "service_charges",
                },
            ]
        },
        update=True,
    )
