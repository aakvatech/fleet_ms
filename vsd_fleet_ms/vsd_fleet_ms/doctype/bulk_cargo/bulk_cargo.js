// Copyright (c) 2024, VV SYSTEMS DEVELOPER LTD and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Cargo', {
    refresh: function(frm) {
        apply_truck_filter(frm);
        
        // Set service item filter
        frm.set_query("service_item", function() {
            return {
                filters: {
                    item_group: "Services",
                }
            };
        });
    },
    
    onload: function(frm) {
        apply_truck_filter(frm);
    },
    
    save: function(frm) {
        calculate_total_capacity(frm);
        calculate_total_loaded_volume(frm);
        calculate_total_offloaded_volume(frm);
    },
    
    validate: function(frm) {
        calculate_total_capacity(frm);
        calculate_total_loaded_volume(frm);
        calculate_total_offloaded_volume(frm);
    },
    
    create_sales_invoice: function(frm) {
        frappe.call({
            method: "create_sales_invoice",
            args: {
                name: frm.doc.name
            },
            callback: function(response) {
                console.log("Response from create_sales_invoice:", response);
                if (response.message && response.message.status === "success") {
                    frm.set_value("sales_invoice_id", response.message.invoice_name);
                    
                    const total_loss = frm.doc.loss_quantity;  
                    const rate = response.message.rate;   
                    const loss_total = total_loss * rate;

                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Sales Invoice",
                            name: response.message.invoice_name,
                            fieldname: {
                                "total_loss": total_loss,
                                "loss_total": loss_total
                            }
                        },
                        callback: function(set_value_response) {
                            console.log("Response from set_value:", set_value_response);
                            if (set_value_response.message) {
                                frappe.msgprint(__("Total loss and loss total updated successfully."));
                            } else {
                                frappe.msgprint(__("Error updating total loss and loss total."));
                            }
                        }
                    });

                    frappe.msgprint(__("Sales Invoice {0} created successfully", [response.message.invoice_name]));
                } else {
                    frappe.msgprint(__("Error: {0}", [response.message.message]));
                }
            }
        });
    }
});

frappe.ui.form.on('Cargo Trip', {
    cargo_trips_add: function(frm) {
        apply_truck_filter(frm);
    },
    
    cargo_trips_remove: function(frm, cdt, cdn) {
        apply_truck_filter(frm);
        calculate_total_capacity(frm);
        calculate_total_loaded_volume(frm);
        calculate_total_offloaded_volume(frm);
        calculate_total_loss(frm);
    },
    
    truck_number: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.truck_number) return;

        // Ensure cargo_type is present before fetching truck details
        if (!row.cargo_type) {
            frappe.model.set_value(cdt, cdn, "cargo_type", frm.doc.cargo_type);
            frm.refresh_field("cargo_trips");
        }

        // Check again if cargo_type is set
        if (!row.cargo_type) {
            frappe.msgprint(__("Cargo type is missing in this row."));
            return;
        }

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Truck",
                name: row.truck_number
            },
            callback: function(response) {
                if (response.message) {
                    let truck = response.message;

                    if (truck.compartment_details && truck.compartment_details.length > 0) {
                        let matched_compartment = truck.compartment_details.find(compartment =>
                            compartment.cargo === row.cargo_type
                        );

                        if (matched_compartment) {
                            frappe.model.set_value(cdt, cdn, "truck_capacity", matched_compartment.capacity);
                            calculate_total_capacity(frm);
                        } else {
                            frappe.msgprint(__("No compartment found with cargo type: {0}", [row.cargo_type]));
                        }
                    } else {
                        frappe.msgprint(__("No compartments available in this truck."));
                    }
                } else {
                    frappe.msgprint(__("Truck not found."));
                }
            }
        });
    },
    
    truck_capacity: function(frm, cdt, cdn) {
        calculate_total_capacity(frm);
    },
    
    loaded_volume: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        calculate_total_loaded_volume(frm);
        update_loss(frm, row);
    },
    
    offloaded_volume: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        calculate_total_offloaded_volume(frm);
        update_loss(frm, row);
    },
    
    cargo_registration: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let parent = frm.doc;

        if (row.cargo_registration_id) {
            frappe.show_alert({
                message: __('Cargo Registration already exists: <a href="/app/cargo-registration/{0}">{0}</a>', [row.cargo_registration_id]),
                indicator: 'orange'
            });
            return;
        }

        // Build arguments dynamically, ignoring empty optional fields
        let args = {
            customer: parent.customer_name,
            trip_route: parent.trip_route,
            posting_date: parent.posting_date,
            rate: parent.rate,
            cargo_type: row.cargo_type,
            truck_capacity: row.truck_capacity
        };

        // Optional fields - only include if value is present
        const optional_fields = [
            "cargo_destination_country", 
            "cargo_destination_city", 
            "expected_offloading_date",
            "cargo_location_country",
            "cargo_location_city",
            "loading_date"
        ];
        
        optional_fields.forEach(field => {
            if (row[field]) {
                args[field] = row[field];
            }
        });

        frappe.call({
            method: "create_cargo_registration",
            args: args,
            callback: function(r) {
                if (r.message) {
                    frappe.model.set_value(cdt, cdn, 'cargo_registration_id', r.message.name);

                    // Update backend record to store cargo_registration_id
                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Cargo Trip",
                            name: row.name,
                            fieldname: "cargo_registration_id",
                            value: r.message.name
                        },
                        callback: function() {
                            frm.reload_doc();
                        }
                    });

                    frappe.show_alert({
                        message: __('Cargo Registration Created: <a href="/app/cargo-registration/{0}">{0}</a>', [r.message.name]),
                        indicator: 'green'
                    });
                } else {
                    frappe.show_alert({
                        message: __("Failed to create Cargo Registration"),
                        indicator: 'red'
                    });
                }
            }
        });
    },

    manifest: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.manifest_id) {
            frappe.show_alert({
                message: __('Manifest already exists: <a href="/app/manifest/{0}">{0}</a>', [row.manifest_id]),
                indicator: 'orange'
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
                    truck: row.truck_number
                }
            },
            callback: function(response) {
                if (response.message) {
                    // Update the cargo trip record with the new ID
                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Cargo Trip",
                            name: row.name,
                            fieldname: "manifest_id",
                            value: response.message.name
                        },
                        callback: function() {
                            frm.reload_doc();
                            frappe.msgprint(__('Manifest created successfully: <a href="/app/manifest/{0}">{0}</a>', [response.message.name]));
                        }
                    });
                }
            }
        });
    }
});

// ===== HELPER FUNCTIONS =====

function apply_truck_filter(frm) {
    let selected_trucks = frm.doc.cargo_trips.map(trip => trip.truck_number).filter(Boolean);

    frm.fields_dict['cargo_trips'].grid.get_field('truck_number').get_query = function() {
        return {
            filters: {
                name: ['not in', selected_trucks]
            }
        };
    };
}

function calculate_total_capacity(frm) {
    let total_capacity = 0;

    frm.doc.cargo_trips.forEach(row => {
        total_capacity += parseFloat(row.truck_capacity) || 0; 
    });

    frm.set_value('total_capacity', total_capacity);

    // Calculate remained capacity
    if (frm.doc.fuel_capacity) {
        frm.set_value('remained_capacity', parseFloat(frm.doc.fuel_capacity) - total_capacity);
    }

    frm.refresh_fields(['total_capacity', 'remained_capacity']);
}

function calculate_total_loaded_volume(frm) {
    let total_loaded_volume = 0;

    frm.doc.cargo_trips.forEach(row => {
        total_loaded_volume += parseFloat(row.loaded_volume) || 0; 
    });

    frm.set_value('total_loaded_volume', total_loaded_volume);
}

function calculate_total_offloaded_volume(frm) {
    let total_offloaded_volume = 0;

    frm.doc.cargo_trips.forEach(row => {
        total_offloaded_volume += parseFloat(row.offloaded_volume) || 0; 
    });

    frm.set_value('total_offloaded_volume', total_offloaded_volume);
}

function update_loss(frm, row) {
    let loaded_volume = row.loaded_volume || 0;
    let offloaded_volume = row.offloaded_volume || 0;
    let actual_loss = loaded_volume - offloaded_volume;

    frappe.db.get_value('Cargo Types', row.cargo_type, 'allowable_loss', (r) => {
        if (r.allowable_loss !== undefined && r.allowable_loss !== null) {
            let allowable_loss_percentage = r.allowable_loss;
            let allowable_loss = (allowable_loss_percentage / 100) * loaded_volume;

            if (actual_loss > allowable_loss) {
                let exceeded_loss = actual_loss - allowable_loss;
                frappe.model.set_value(row.doctype, row.name, 'loss', exceeded_loss);
            } else {
                frappe.model.set_value(row.doctype, row.name, 'loss', 0);
            }

            // Wait for async set_value before calculating total
            setTimeout(() => calculate_total_loss(frm), 300);
        }
    });
}

function calculate_total_loss(frm) {
    let total_loss = 0;
    frm.doc.cargo_trips.forEach(row => {
        total_loss += parseFloat(row.loss) || 0;
    });
    frm.set_value('total_loss', total_loss);
}