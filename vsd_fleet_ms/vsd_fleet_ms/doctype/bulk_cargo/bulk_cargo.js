// Copyright (c) 2024, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Cargo", {
  refresh: function (frm) {
    apply_truck_filter(frm);
    frm.set_query("service_item", function () {
      return { filters: { item_group: "Services" } };
    });
  },

  onload: function (frm) {
    apply_truck_filter(frm);
  },

  validate: function (frm) {
    calculate_all_totals(frm);
  },

  save: function (frm) {
    calculate_all_totals(frm);
  },

  create_sales_invoice: function (frm) {
    frappe.call({
      method:
        "vsd_fleet_ms.vsd_fleet_ms.doctype.bulk_cargo.bulk_cargo.create_sales_invoice",
      args: { name: frm.doc.name },
      callback: function (response) {
        if (response.message && response.message.status === "success") {
          frm.set_value("sales_invoice_id", response.message.invoice_name);

          // Optional: update extra fields on Sales Invoice
          if (frm.doc.total_loss && response.message.rate) {
            let loss_total = frm.doc.total_loss * response.message.rate;
            frappe.call({
              method: "frappe.client.set_value",
              args: {
                doctype: "Sales Invoice",
                name: response.message.invoice_name,
                fieldname: {
                  total_loss: frm.doc.total_loss,
                  loss_total: loss_total,
                },
              },
              callback: function (set_value_response) {
                if (set_value_response.message) {
                  frappe.msgprint(
                    __("Total loss and loss total updated successfully.")
                  );
                }
              },
            });
          }

          frappe.msgprint(
            __("Sales Invoice {0} created successfully", [
              response.message.invoice_name,
            ])
          );
        } else {
          frappe.msgprint(__("Error: {0}", [response.message.message]));
        }
      },
    });
  },

  cargo_trips_remove: function (frm) {
    calculate_all_totals(frm);
    apply_truck_filter(frm);
  },
});

// ---------------------- Cargo Trip Child Table ----------------------

frappe.ui.form.on("Cargo Trip", {
  truck_number: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (!row.truck_number) return;

    // Auto-fill cargo_type from parent if missing
    if (!row.cargo_type && frm.doc.cargo_type) {
      frappe.model.set_value(cdt, cdn, "cargo_type", frm.doc.cargo_type);
      row.cargo_type = frm.doc.cargo_type;
    }

    if (!row.cargo_type) return;

    frappe.call({
      method: "frappe.client.get",
      args: { doctype: "Truck", name: row.truck_number },
      callback: function (r) {
        if (r.message && r.message.compartment_details) {
          let matched = r.message.compartment_details.find(
            (c) => c.cargo === row.cargo_type
          );
          if (matched) {
            frappe.model.set_value(
              cdt,
              cdn,
              "truck_capacity",
              matched.capacity
            );
            calculate_total_capacity(frm);
          } else {
            frappe.msgprint(
              __("No compartment found for cargo type: {0}", [row.cargo_type])
            );
          }
        } else {
          frappe.msgprint("Truck not found or has no compartments.");
        }
      },
    });

    apply_truck_filter(frm);
  },

  truck_capacity: function (frm) {
    calculate_total_capacity(frm);
  },

  loaded_volume: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    calculate_total_loaded_volume(frm);
    update_loss(frm, row);
  },

  offloaded_volume: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    calculate_total_offloaded_volume(frm);
    update_loss(frm, row);
  },

  cargo_registration: async function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.cargo_registration_id) {
      frappe.show_alert({
        message: __(
          'Cargo Registration already exists: <a href="/app/cargo-registration/{0}">{0}</a>',
          [row.cargo_registration_id]
        ),
        indicator: "orange",
      });
      return;
    }

    // Defaults
    let number_of_packages = 1;
    let cargo_location_country = "Tanzania";
    let cargo_destination_country = "Tanzania";
    let loading_date = frm.doc.posting_date;
    let expected_offloading_date = frappe.datetime.now_date();

    // Fetch starting_point and ending_point from Trip Route
    let cargo_location_city = "";
    let cargo_destination_city = "";
    if (frm.doc.trip_route) {
      await frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Trip Routes",
          name: frm.doc.trip_route,
        },
        callback: function (r) {
          if (r.message) {
            cargo_location_city = r.message.starting_point || "";
            cargo_destination_city = r.message.ending_point || "";
          }
        },
      });
    }

    let args = {
      customer: frm.doc.customer_name,
      trip_route: frm.doc.trip_route,
      posting_date: frm.doc.posting_date,
      rate: frm.doc.rate,
      cargo_type: row.cargo_type,
      truck_capacity: row.truck_capacity,
      service_item: frm.doc.service_item,
      number_of_packages: number_of_packages,
      cargo_location_country: cargo_location_country,
      cargo_location_city: cargo_location_city,
      loading_date: loading_date,
      cargo_destination_country: cargo_destination_country,
      cargo_destination_city: cargo_destination_city,
      expected_offloading_date: expected_offloading_date,
    };

    frappe.call({
      method:
        "vsd_fleet_ms.vsd_fleet_ms.doctype.bulk_cargo.bulk_cargo.create_cargo_registration",
      args: args,
      callback: function (r) {
        if (r.message) {
          frappe.model.set_value(
            cdt,
            cdn,
            "cargo_registration_id",
            r.message.name
          );
          frappe.show_alert({
            message: __(
              'Cargo Registration Created: <a href="/app/cargo-registration/{0}">{0}</a>',
              [r.message.name]
            ),
            indicator: "green",
          });
          frappe.msgprint({
            message: __(
              "Please update the Offloading Date and The location country"
            ),
            indicator: "orange",
          });
        } else {
          frappe.show_alert({
            message: __("Failed to create Cargo Registration"),
            indicator: "red",
          });
        }
      },
    });
  },

  manifest: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    // Prevent multiple creation
    if (row.manifest_id) {
      frappe.show_alert({
        message: __(
          'Manifest already exists: <a href="/app/manifest/{0}">{0}</a>',
          [row.manifest_id]
        ),
        indicator: "orange",
      });
      return;
    }

    // Ensure cargo_registration_id is present
    if (!row.cargo_registration_id) {
      frappe.msgprint({
        message: __(
          "Please create Cargo Registration first before creating Manifest."
        ),
        indicator: "red",
      });
      return;
    }

    frappe.call({
      method: "frappe.client.insert",
      args: {
        doc: {
          doctype: "Manifest",
          cargo_trip: row.name,
          bulk_cargo: frm.doc.name,
          route: frm.doc.trip_route,
          manifest_date: frappe.datetime.now_date(),
          customer: frm.doc.customer_name,
          truck: row.truck_number,
          cargo_id: row.cargo_registration_id, // Set cargo_id from cargo_registration_id
        },
      },
      callback: function (r) {
        if (r.message && r.message.name) {
          // Set manifest_id in the row after creation
          frappe.model.set_value(cdt, cdn, "manifest_id", r.message.name);
          frm.refresh_field("cargo_trips");
          frappe.msgprint(
            __(
              'Manifest created successfully: <a href="/app/manifest/{0}">{0}</a>',
              [r.message.name]
            )
          );
        } else {
          frappe.show_alert({
            message: __(
              "Failed to create Manifest. Please check your data and try again."
            ),
            indicator: "red",
          });
        }
      },
      error: function (err) {
        frappe.show_alert({
          message: __(
            "Failed to create Manifest. Please check your data and try again."
          ),
          indicator: "red",
        });
      },
    });
  },

  cargo_trips_add: function (frm) {
    apply_truck_filter(frm);
  },

  cargo_trips_remove: function (frm) {
    calculate_all_totals(frm);
    apply_truck_filter(frm);
  },
});

// ---------------------- Calculations ----------------------

function calculate_total_capacity(frm) {
  let total = 0;
  frm.doc.cargo_trips.forEach((row) => {
    total += parseFloat(row.truck_capacity) || 0;
  });
  frm.set_value("total_capacity", total);
  if (frm.doc.fuel_capacity) {
    frm.set_value(
      "remained_capacity",
      parseFloat(frm.doc.fuel_capacity) - total
    );
  }
}

function calculate_total_loaded_volume(frm) {
  let total = 0;
  frm.doc.cargo_trips.forEach((row) => {
    total += parseFloat(row.loaded_volume) || 0;
  });
  frm.set_value("total_loaded_volume", total);
}

function calculate_total_offloaded_volume(frm) {
  let total = 0;
  frm.doc.cargo_trips.forEach((row) => {
    total += parseFloat(row.offloaded_volume) || 0;
  });
  frm.set_value("total_offloaded_volume", total);
}

function update_loss(frm, row) {
  let loaded = parseFloat(row.loaded_volume) || 0;
  let offloaded = parseFloat(row.offloaded_volume) || 0;
  let loss = Math.max(0, loaded - offloaded);
  frappe.model.set_value(row.doctype, row.name, "loss", loss);
  calculate_total_loss(frm);
}

function calculate_total_loss(frm) {
  let total = 0;
  frm.doc.cargo_trips.forEach((row) => {
    total += parseFloat(row.loss) || 0;
  });
  frm.set_value("total_loss", total);
}

function calculate_all_totals(frm) {
  calculate_total_capacity(frm);
  calculate_total_loaded_volume(frm);
  calculate_total_offloaded_volume(frm);
  calculate_total_loss(frm);
}

function apply_truck_filter(frm) {
  let selected = frm.doc.cargo_trips.map((r) => r.truck_number).filter(Boolean);
  frm.fields_dict["cargo_trips"].grid.get_field("truck_number").get_query =
    function () {
      return { filters: { name: ["not in", selected] } };
    };
}
