// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Inspection", {
  tyre: function (frm) {
    if (!frm.doc.tyre) return;

    frappe.db.get_doc("Tyre Master", frm.doc.tyre).then((doc) => {
      if (!doc) return;
      frm.set_value("vehicle_type", doc.current_vehicle_type || "");
      frm.set_value("vehicle", doc.current_vehicle || "");
      frm.set_value("position", doc.position || "");
    });
  },
});
