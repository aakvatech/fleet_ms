// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Management Settings", {
  setup(frm) {
    ["store_warehouse", "in_service_warehouse", "repair_warehouse"].forEach((field) => {
      frm.set_query(field, () => ({
        filters: { company: frm.doc.company, is_group: 0 },
      }));
    });
    frm.set_query("scrap_expense_account", () => ({
      filters: { company: frm.doc.company, is_group: 0, root_type: "Expense" },
    }));
  },
});
