// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Master", {
  setup(frm) {
    frm.set_query("tyre_item", () => ({
      filters: { is_tyre: 1, has_serial_no: 1, disabled: 0 },
    }));
    frm.set_query("serial_no", () => ({
      filters: { item_code: frm.doc.tyre_item },
    }));
  },

  refresh(frm) {
    if (frm.is_new() || frm.doc.status === "Scrapped") return;

    frm.add_custom_button(__("Tyre Movement"), () => {
      frappe.new_doc("Tyre Movement", { tyre_serial: frm.doc.name });
    }, __("Create"));
    frm.add_custom_button(__("Tyre Inspection"), () => {
      frappe.new_doc("Tyre Inspection", { tyre: frm.doc.name });
    }, __("Create"));
  },

  tyre_item(frm) {
    frm.set_value("serial_no", "");
  },
});
