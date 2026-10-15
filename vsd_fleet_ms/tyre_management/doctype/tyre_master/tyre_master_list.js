// Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt

frappe.listview_settings["Tyre Master"] = {
  get_indicator(doc) {
    const colors = {
      "In Store": "blue",
      "In Service": "green",
      "Under Repair": "orange",
      Scrapped: "red",
    };
    return [__(doc.status), colors[doc.status], "status,=," + doc.status];
  },
};
