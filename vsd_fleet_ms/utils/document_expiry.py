import frappe
from frappe.utils import getdate, nowdate


DEFAULT_ALERT_DAYS = {7, 3, 1, 0}


def _get_recipients_by_roles(roles):
    if not roles:
        return []

    users = frappe.get_all(
        "Has Role",
        filters={"role": ["in", roles]},
        fields=["parent"],
        distinct=True,
    )
    user_ids = [u.parent for u in users]
    if not user_ids:
        return []

    return [
        u.email
        for u in frappe.get_all(
            "User",
            filters={"name": ["in", user_ids], "enabled": 1},
            fields=["email"],
        )
        if u.email
    ]


def _already_notified(subject):
    return frappe.db.exists(
        "Notification Log",
        {"subject": subject, "creation": (">=", nowdate())},
    )


def notify_expiring_documents():
    """Notify on expiring Truck/Trailer documents (Document Attachments)."""
    today = getdate(nowdate())
    roles = ["Fleet Manager", "Logistic Master", "System Manager"]
    recipients = _get_recipients_by_roles(roles)

    rows = frappe.get_all(
        "Document Attachments",
        filters={"parenttype": ["in", ["Truck", "Trailers"]]},
        fields=["name1", "reference_number", "expire_date", "parenttype", "parent"],
    )

    for row in rows:
        if not row.expire_date:
            continue
        exp_date = getdate(row.expire_date)
        days_left = (exp_date - today).days

        is_expired = days_left < 0
        if not is_expired and days_left not in DEFAULT_ALERT_DAYS:
            continue

        if is_expired:
            subject = (
                f"Document expiry Reminder: {row.parenttype} {row.parent} "
                f"Document {row.name1 or row.reference_number} expired"
            )
        else:
            subject = (
                f"Document expiry Reminder: {row.parenttype} {row.parent} "
                f"Document {row.name1 or row.reference_number} expires in {days_left} day(s)"
            )

        if _already_notified(subject):
            continue

        if is_expired:
            days_ago = abs(days_left)
            message = (
                f"{row.parenttype} {row.parent} document "
                f"{row.name1 or row.reference_number} expired on {exp_date} "
                f"({days_ago} day(s) ago). "
                "Please update the document validation."
            )
        else:
            message = (
                f"{row.parenttype} {row.parent} document "
                f"{row.name1 or row.reference_number} expires on {exp_date} "
                f"({days_left} day(s) left). "
                "Please update the document validation."
            )

        frappe.get_doc(
            {
                "doctype": "Notification Log",
                "subject": subject,
                "type": "Alert",
                "document_type": row.parenttype,
                "document_name": row.parent,
                "email_content": message,
                "for_user": "Administrator",
            }
        ).insert(ignore_permissions=True)

        if recipients:
            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=message,
                now=True,
            )
