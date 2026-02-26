from frappe import _


def get_data():
    return {
        "fieldname": "tyre_serial",
        "non_standard_fieldnames": {
            "Tyre Inspection": "tyre",
            "Tyre Ledger": "tyre",
        },
        "transactions": [
            {
                "label": _("Tyre Transactions"),
                "items": ["Tyre Movement", "Tyre Inspection", "Tyre Ledger"],
            }
        ],
    }

