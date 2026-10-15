// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt

// When a tyre item is picked on a receiving document, receive it into the
// Tyre Store warehouse from Tyre Management Settings. The server rejects any other.
(() => {
  // This file is loaded once per receiving doctype; register the handlers only once.
  if (frappe._vsd_tyre_receipt_loaded) return;
  frappe._vsd_tyre_receipt_loaded = true;

  const ROW_SETUP = {
    "Purchase Receipt Item": { field: "warehouse", applies: () => true },
    "Purchase Invoice Item": { field: "warehouse", applies: (frm) => frm.doc.update_stock },
    "Stock Entry Detail": { field: "t_warehouse", applies: (frm, row) => !row.s_warehouse },
  };

  function set_tyre_store_warehouse(frm, cdt, cdn, setup) {
    const row = locals[cdt][cdn];
    if (!row.item_code || !setup.applies(frm, row)) return;

    frappe
      .xcall("vsd_fleet_ms.utils.tyre_receipt.get_tyre_store_warehouse", {
        item_code: row.item_code,
        company: frm.doc.company,
      })
      .then((warehouse) => {
        if (!warehouse) return;
        // ERPNext fills the row warehouse from item details; set ours after that call returns.
        frappe.after_ajax(() => frappe.model.set_value(cdt, cdn, setup.field, warehouse));
      });
  }

  Object.entries(ROW_SETUP).forEach(([child_doctype, setup]) => {
    frappe.ui.form.on(child_doctype, {
      item_code(frm, cdt, cdn) {
        set_tyre_store_warehouse(frm, cdt, cdn, setup);
      },
    });
  });
})();
