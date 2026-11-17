import json

import frappe
from frappe.utils import flt


def _is_admin():
    roles = frappe.get_roles()
    return "System Manager" in roles or "招标管理员" in roles


@frappe.whitelist()
def get_ranking(tender):
    """评标排名。管理员可见价格；供应商只见排名与自己的价格。"""
    if not frappe.db.exists("Tender", tender):
        frappe.throw("招标单不存在")
    quotes = frappe.get_all(
        "Supplier Quote",
        filters={"tender": tender, "docstatus": 1},
        fields=["name", "supplier_name", "total_price", "owner", "creation"],
        order_by="total_price asc, creation asc",
    )
    is_admin = _is_admin()
    result = []
    for i, q in enumerate(quotes, 1):
        row = {"rank": i, "supplier_name": q.supplier_name}
        if is_admin:
            row["total_price"] = flt(q.total_price)
        elif q.owner == frappe.session.user:
            row["total_price"] = flt(q.total_price)
            row["is_me"] = 1
        result.append(row)
    return {"is_admin": is_admin, "count": len(result), "ranking": result}


@frappe.whitelist(methods=["POST"])
def submit_quote(tender, supplier_name, items):
    """供应商门户提交报价。items 为 JSON 数组字符串。"""
    roles = frappe.get_roles()
    if "供应商" not in roles and "System Manager" not in roles:
        frappe.throw("只有供应商角色可以提交报价")
    t = frappe.get_doc("Tender", tender)
    if t.status in ("已截止", "已定标"):
        frappe.throw("该招标已截止报名或已定标，无法报价")
    doc = frappe.get_doc(
        {
            "doctype": "Supplier Quote",
            "tender": tender,
            "supplier_name": supplier_name,
            "items": json.loads(items),
        }
    )
    doc.insert(ignore_permissions=True)
    doc.submit()
    frappe.db.commit()
    return {"name": doc.name, "total_price": doc.total_price}
