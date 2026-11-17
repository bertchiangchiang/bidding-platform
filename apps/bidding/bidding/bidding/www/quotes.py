import frappe
from frappe.utils import format_datetime


no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        context.is_guest = True
        context.is_supplier = False
        context.is_admin = False
        context.tenders = []
        return
    context.is_guest = False
    roles = frappe.get_roles()
    if frappe.session.user == "Administrator":
        context.is_supplier = False
        context.is_admin = True
    else:
        context.is_supplier = "供应商" in roles
        context.is_admin = "System Manager" in roles or "招标管理员" in roles

    if context.is_supplier:
        context.my_quotes = frappe.get_all(
            "Supplier Quote",
            filters={"owner": frappe.session.user},
            fields=["name", "tender", "supplier_name", "total_price", "docstatus", "modified"],
            order_by="modified desc",
        )
    filters = {"status": ("in", ["草稿", "进行中"])} if context.is_supplier else {}
    tenders = frappe.get_all(
        "Tender",
        filters=filters,
        fields=["name", "title", "description", "deadline", "status"],
        order_by="creation desc",
    )
    for t in tenders:
        t["deadline_str"] = (
            format_datetime(t.deadline, "yyyy-MM-dd HH:mm") if t.deadline else "不限"
        )
    context.tenders = tenders
