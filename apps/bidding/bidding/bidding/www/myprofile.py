import frappe

from bidding.api import _is_admin, _my_supplier, PROFILE_FIELDS


no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        context.is_guest = True
        return
    context.is_guest = False
    context.is_admin = _is_admin()
    prof = _my_supplier()
    if prof:
        doc = frappe.db.get_value(
            "Supplier", prof.name, PROFILE_FIELDS + ("review_note",), as_dict=1
        )
        context.profile = doc
        context.status = prof.status
    else:
        context.profile = None
        context.status = None
