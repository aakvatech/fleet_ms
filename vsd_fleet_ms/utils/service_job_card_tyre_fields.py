import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def ensure_service_job_card_tyre_fields():
    """Create Fleet-specific tyre fields on Service Job Card.

    Safe to run repeatedly on migrate/install and on sites where either app is absent.
    """
    if "servicems" not in frappe.get_installed_apps():
        return

    if not frappe.db.exists("DocType", "Service Job Card"):
        return

    required_doctypes = ["Tyre Master", "Tyre Position", "Trailers"]
    if not all(frappe.db.exists("DocType", dt) for dt in required_doctypes):
        return

    create_custom_fields(
        {
            "Service Job Card": [
                {
                    "fieldname": "custom_trailer",
                    "label": "Trailer",
                    "fieldtype": "Link",
                    "options": "Trailers",
                    "insert_after": "service_item_name",
                },
                {
                    "fieldname": "tyre_management_section",
                    "label": "Tyre Management",
                    "fieldtype": "Section Break",
                    "insert_after": "odometer_reading",
                },
                {
                    "fieldname": "tyre_serial",
                    "label": "Tyre Serial",
                    "fieldtype": "Link",
                    "options": "Tyre Master",
                    "insert_after": "tyre_management_section",
                },
                {
                    "fieldname": "tyre_movement_type",
                    "label": "Tyre Movement Type",
                    "fieldtype": "Select",
                    "options": "Installation\nRemoval\nPositional Change\nVehicle Transfer\nSend for Repair\nReturn from Repair\nScrap",
                    "default": "Installation",
                    "insert_after": "tyre_serial",
                },
                {
                    "fieldname": "tyre_install_on",
                    "label": "Movement On",
                    "fieldtype": "Select",
                    "options": "Truck\nTrailers",
                    "depends_on": "eval:doc.tyre_movement_type",
                    "insert_after": "tyre_movement_type",
                },
                {
                    "fieldname": "column_break_tyre_1",
                    "fieldtype": "Column Break",
                    "insert_after": "tyre_install_on",
                },
                {
                    "fieldname": "tyre_from_position",
                    "label": "From Position",
                    "fieldtype": "Link",
                    "options": "Tyre Position",
                    "depends_on": "eval:doc.tyre_movement_type == 'Positional Change'",
                    "insert_after": "column_break_tyre_1",
                },
                {
                    "fieldname": "tyre_to_position",
                    "label": "To Position",
                    "fieldtype": "Link",
                    "options": "Tyre Position",
                    "depends_on": "eval:doc.tyre_movement_type == 'Positional Change'",
                    "insert_after": "tyre_from_position",
                },
                {
                    "fieldname": "tyre_position",
                    "label": "Tyre Position",
                    "fieldtype": "Link",
                    "options": "Tyre Position",
                    "depends_on": "eval:doc.tyre_movement_type != 'Positional Change'",
                    "insert_after": "tyre_to_position",
                },
            ]
        },
        update=True,
    )
