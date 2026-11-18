import frappe


no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        context.is_guest = True
        return
    context.is_guest = False
    roles = frappe.get_roles()
    context.is_admin = frappe.session.user == "Administrator" or (
        "System Manager" in roles or "招标管理员" in roles
    )
    if not context.is_admin:
        return

    tenders = frappe.get_all(
        "Tender",
        fields=["name", "title", "status", "deadline", "evaluation_mode", "modified"],
        order_by="creation desc",
    )
    for t in tenders:
        t.quote_count = frappe.db.count(
            "Supplier Quote", {"tender": t.name, "docstatus": 1}
        )
        t.eval_count = frappe.db.count(
            "Evaluation", {"tender": t.name, "docstatus": 1}
        )
    context.tenders = tenders

    context.suppliers = frappe.get_all(
        "Supplier",
        fields=[
            "name", "supplier_name", "contact_person", "phone",
            "status", "business_scope", "review_note", "linked_user", "modified",
        ],
        order_by="status asc, modified desc",
    )
    context.templates = frappe.get_all("Score Template", pluck="name")
