// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Ledger", {
  refresh: function (frm) {
    if (frm.is_new()) return;

    const readonly_fields = [
      "tyre",
      "posting_date",
      "transaction_type",
      "movement_type",
      "from_vehicle_type",
      "from_vehicle",
      "from_position",
      "to_vehicle_type",
      "to_vehicle",
      "to_position",
    ];

    readonly_fields.forEach((fieldname) => {
      frm.set_df_property(fieldname, "read_only", 1);
    });
  },
});
