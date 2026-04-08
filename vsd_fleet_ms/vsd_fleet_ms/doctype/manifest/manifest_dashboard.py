from frappe import _


def get_data():
    return {
        "fieldname": "manifest",
        "transactions": [
            {
                "label": _("Reference"),
                "items": ["Cargo Registration"],
            },
        ],
    }
