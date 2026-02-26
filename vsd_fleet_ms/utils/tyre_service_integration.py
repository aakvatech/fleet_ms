# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors

import frappe


def create_tyre_movement_from_service_job_card(doc, method=None):
    def skip(reason):
        frappe.msgprint(
            reason,
            title="Tyre Movement Not Created",
            indicator="orange",
            alert=True,
        )
        return

    try:
        if not frappe.db.exists("DocType", "Transport Settings"):
            return

        settings = frappe.get_single("Transport Settings")
        if not (settings.enable_service_ms and settings.create_tyre_movement_from_service_job_card):
            return

        tyre_serial = (getattr(doc, "tyre_serial", None) or "").strip()
        tyre_movement_type = (getattr(doc, "tyre_movement_type", None) or "").strip()
        tyre_install_on = (getattr(doc, "tyre_install_on", None) or "").strip()
        tyre_from_position = (getattr(doc, "tyre_from_position", None) or "").strip()
        tyre_to_position = (getattr(doc, "tyre_to_position", None) or "").strip()
        tyre_position = (getattr(doc, "tyre_position", None) or "").strip()

        # Keep silent when user is not using tyre movement from SJC.
        if not tyre_serial and not tyre_movement_type:
            return
        if not tyre_serial or not tyre_movement_type:
            return skip("Please fill both Tyre Serial and Tyre Movement Type.")
        if not tyre_install_on:
            return skip("Please choose Movement On (Truck or Trailers).")

        if frappe.db.exists("Tyre Movement", {"service_job_card": doc.name, "docstatus": ["!=", 2]}):
            return skip(f"Tyre Movement is already created from Service Job Card {doc.name}.")

        tyre = frappe.get_doc("Tyre Master", tyre_serial)
        if not is_tyre_available_for_auto_movement(tyre, tyre_movement_type):
            return skip(
                f"Tyre {tyre_serial} with status '{tyre.status}' cannot be used for movement type '{tyre_movement_type}'."
            )

        if is_tyre_scrapped_in_ledger(tyre_serial):
            return skip(f"Tyre {tyre_serial} is already scrapped in Tyre Ledger.")

        movement = frappe.new_doc("Tyre Movement")
        movement.tyre_serial = tyre_serial
        movement.service_job_card = doc.name
        movement.movement_type = tyre_movement_type
        movement.odometer_km = getattr(doc, "odometer_reading", None)
        movement.remarks = "Auto-created from Service Job Card"
        selected_vehicle_type, selected_vehicle = get_selected_vehicle(doc, tyre_install_on)
        if not selected_vehicle_type or not selected_vehicle:
            return skip(f"No {tyre_install_on} selected in Service Job Card for Movement On.")

        if tyre_movement_type == "Installation":
            if not tyre_position:
                return skip("Please set Tyre Position for Installation.")
            movement.to_vehicle_type = selected_vehicle_type
            movement.to_vehicle = selected_vehicle
            movement.to_position = tyre_position

        elif tyre_movement_type == "Positional Change":
            if not tyre.current_vehicle_type or not tyre.current_vehicle:
                return skip(f"Tyre {tyre_serial} is not currently installed.")
            if not is_selected_vehicle_matches_tyre(tyre, selected_vehicle_type, selected_vehicle):
                return skip(
                    f"Selected {selected_vehicle_type} {selected_vehicle} does not match tyre current vehicle "
                    f"{tyre.current_vehicle_type} {tyre.current_vehicle}."
                )
            if not tyre_from_position or not tyre_to_position:
                return skip("Please set both From Position and To Position for Positional Change.")
            movement.from_vehicle_type = selected_vehicle_type
            movement.from_vehicle = selected_vehicle
            movement.from_position = tyre_from_position
            movement.to_vehicle_type = selected_vehicle_type
            movement.to_vehicle = selected_vehicle
            movement.to_position = tyre_to_position

        elif tyre_movement_type == "Removal":
            if not tyre.current_vehicle_type or not tyre.current_vehicle or not tyre_position:
                return skip(f"Tyre {tyre_serial} is not properly installed with position details.")
            if not is_selected_vehicle_matches_tyre(tyre, selected_vehicle_type, selected_vehicle):
                return skip(
                    f"Selected {selected_vehicle_type} {selected_vehicle} does not match tyre current vehicle "
                    f"{tyre.current_vehicle_type} {tyre.current_vehicle}."
                )
            movement.from_vehicle_type = selected_vehicle_type
            movement.from_vehicle = selected_vehicle
            movement.from_position = tyre_position

        else:
            if not tyre.current_vehicle_type or not tyre.current_vehicle:
                return skip(f"Tyre {tyre_serial} is not currently installed.")
            if not is_selected_vehicle_matches_tyre(tyre, selected_vehicle_type, selected_vehicle):
                return skip(
                    f"Selected {selected_vehicle_type} {selected_vehicle} does not match tyre current vehicle "
                    f"{tyre.current_vehicle_type} {tyre.current_vehicle}."
                )
            movement.from_vehicle_type = selected_vehicle_type
            movement.from_vehicle = selected_vehicle
            movement.from_position = tyre_position or tyre.position
            if not movement.from_position:
                return skip("Please set Tyre Position.")

            if tyre_movement_type in ["Vehicle Transfer", "Return from Repair"]:
                to_vehicle_type, to_vehicle = get_transfer_target_vehicle(doc, selected_vehicle_type, selected_vehicle)
                if not to_vehicle_type or not to_vehicle or not tyre_position:
                    return skip(
                        "Target vehicle/position not found. Set truck/trailer and tyre position correctly for transfer."
                    )
                movement.to_vehicle_type = to_vehicle_type
                movement.to_vehicle = to_vehicle
                movement.to_position = tyre_position

        movement.insert(ignore_permissions=True)
        movement.submit()
    except Exception:
        # Do not block Service Job Card submit for optional tyre integration.
        frappe.log_error(frappe.get_traceback(), "Tyre movement auto-create from Service Job Card failed")
        frappe.msgprint(
            "Tyre Movement auto-creation failed. Check Error Log for details.",
            title="Tyre Movement Not Created",
            indicator="red",
            alert=True,
        )


def is_tyre_available_for_auto_movement(tyre, movement_type):
    if tyre.status == "Scrapped":
        return False

    if movement_type == "Installation":
        # Installation should be for not-installed tyres only.
        return tyre.status in ["In Store", "Under Repair"]

    # All other moves require an already installed tyre.
    return tyre.status == "In Service" and bool(tyre.current_vehicle_type) and bool(tyre.current_vehicle)


def is_tyre_scrapped_in_ledger(tyre_serial):
    last_ledger = frappe.get_all(
        "Tyre Ledger",
        filters={"tyre": tyre_serial},
        fields=["transaction_type", "movement_type"],
        order_by="creation desc",
        limit=1,
    )
    if not last_ledger:
        return False
    row = last_ledger[0]
    return row.get("movement_type") == "Scrap" or row.get("transaction_type") == "Scrap"


def get_selected_vehicle(doc, tyre_install_on):
    truck_value = (getattr(doc, "service_item_name", None) or "").strip()
    trailer_value = (getattr(doc, "custom_trailer", None) or "").strip()

    if tyre_install_on == "Truck" and truck_value:
        return ("Truck", truck_value)
    if tyre_install_on == "Trailers" and trailer_value:
        return ("Trailers", trailer_value)
    return ("", "")


def is_selected_vehicle_matches_tyre(tyre, selected_vehicle_type, selected_vehicle):
    return (
        tyre.current_vehicle_type == selected_vehicle_type
        and tyre.current_vehicle == selected_vehicle
    )


def get_transfer_target_vehicle(doc, selected_vehicle_type, selected_vehicle):
    truck_value = (getattr(doc, "service_item_name", None) or "").strip()
    trailer_value = (getattr(doc, "custom_trailer", None) or "").strip()

    if selected_vehicle_type == "Trailers":
        if truck_value:
            return ("Truck", truck_value)
        if trailer_value and trailer_value != selected_vehicle:
            return ("Trailers", trailer_value)
        return ("", "")

    if selected_vehicle_type == "Truck":
        if trailer_value:
            return ("Trailers", trailer_value)
        if truck_value and truck_value != selected_vehicle:
            return ("Truck", truck_value)
        return ("", "")

    return ("", "")
