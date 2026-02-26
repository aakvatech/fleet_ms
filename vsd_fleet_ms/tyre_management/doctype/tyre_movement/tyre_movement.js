// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Movement", {
  refresh: function (frm) {
    frm.set_query("tyre_serial", function () {
      return {
        filters: {
          status: ["!=", "Scrapped"],
        },
      };
    });
  },

  movement_type: function (frm) {
    if (frm.doc.movement_type === "Installation") {
      frm.set_value("from_vehicle_type", "");
      frm.set_value("from_vehicle", "");
      frm.set_value("from_position", "");
    }

    if (frm.doc.movement_type === "Removal") {
      frm.set_value("to_vehicle_type", "");
      frm.set_value("to_vehicle", "");
      frm.set_value("to_position", "");
    }
  },

  tyre_serial: function (frm) {
    if (!frm.doc.tyre_serial || frm.doc.movement_type === "Installation") {
      return;
    }

    frappe.db.get_doc("Tyre Master", frm.doc.tyre_serial).then((doc) => {
      if (!doc) return;
      frm.set_value("from_vehicle_type", doc.current_vehicle_type || "");
      frm.set_value("from_vehicle", doc.current_vehicle || "");
      frm.set_value("from_position", doc.position || "");
    });
  },
});
