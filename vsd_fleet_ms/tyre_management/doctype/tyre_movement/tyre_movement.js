// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Movement", {
  setup(frm) {
    // Which statuses each movement accepts is checked on the server.
    frm.set_query("tyre_serial", () => ({ filters: { status: ["!=", "Scrapped"] } }));
  },

  refresh(frm) {
    if (frm.doc.stock_entry) {
      frm.add_custom_button(__("Stock Entry"), () => frappe.set_route("Form", "Stock Entry", frm.doc.stock_entry), __("View"));
    }
  },

  movement_type(frm) {
    frm.trigger("tyre_serial");
  },

  tyre_serial(frm) {
    if (!frm.doc.tyre_serial) return;

    frappe.db.get_doc("Tyre Master", frm.doc.tyre_serial).then((tyre) => {
      const fitted = tyre.status === "In Service";
      frm.set_value("from_vehicle_type", fitted ? tyre.current_vehicle_type : "");
      frm.set_value("from_vehicle", fitted ? tyre.current_vehicle : "");
      frm.set_value("from_position", fitted ? tyre.position : "");
      if (frm.doc.movement_type === "Positional Change") {
        frm.set_value("to_vehicle_type", tyre.current_vehicle_type);
        frm.set_value("to_vehicle", tyre.current_vehicle);
      }
    });
  },
});
