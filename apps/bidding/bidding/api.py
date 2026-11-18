import json

import frappe
from frappe.utils import flt


def _is_admin():
    roles = frappe.get_roles()
    return "System Manager" in roles or "招标管理员" in roles


def _avg_scores(tender):
    """每个报价单的评审加权总分（多评审人取平均）。返回 {quote_name: avg_score}"""
    rows = frappe.get_all(
        "Evaluation",
        filters={"tender": tender, "docstatus": 1},
        fields=["quote", "total_score"],
    )
    agg = {}
    for r in rows:
        agg.setdefault(r.quote, []).append(flt(r.total_score))
    return {q: flt(sum(v) / len(v), 2) for q, v in agg.items()}


@frappe.whitelist()
def get_ranking(tender, mode=None):
    """评标排名。管理员可见价格；供应商只见排名与自己的价格。分数对所有人可见。"""
    if not frappe.db.exists("Tender", tender):
        frappe.throw("招标单不存在")
    t = frappe.db.get_value(
        "Tender", tender, ["status", "evaluation_mode", "score_template"], as_dict=1
    )
    quotes = frappe.get_all(
        "Supplier Quote",
        filters={"tender": tender, "docstatus": 1},
        fields=["name", "supplier_name", "total_price", "owner", "awarded", "creation"],
    )
    is_admin = _is_admin()

    scores = _avg_scores(tender)
    if mode is None:
        mode = "score" if (t.evaluation_mode == "按评分" and scores) else "price"

    if mode == "score":
        quotes.sort(key=lambda q: (-scores.get(q.name, 0), flt(q.total_price), q.creation))
    else:
        quotes.sort(key=lambda q: (flt(q.total_price), q.creation))

    result = []
    for i, q in enumerate(quotes, 1):
        row = {
            "rank": i,
            "supplier_name": q.supplier_name,
            "quote": q.name,
            "total_score": scores.get(q.name),
            "awarded": 1 if q.awarded else 0,
        }
        if is_admin:
            row["total_price"] = flt(q.total_price)
        elif q.owner == frappe.session.user:
            row["total_price"] = flt(q.total_price)
            row["is_me"] = 1
        result.append(row)
    return {
        "is_admin": is_admin,
        "mode": mode,
        "tender_status": t.status,
        "has_score_template": bool(t.score_template),
        "count": len(result),
        "ranking": result,
    }


@frappe.whitelist(methods=["POST"])
def award(quote):
    """定标：管理员选中某报价，招标单转已定标，其余报价标记未中标。"""
    if not _is_admin():
        frappe.throw("只有管理员可以定标")
    q = frappe.get_doc("Supplier Quote", quote)
    if q.docstatus != 1:
        frappe.throw("只能对已提交的报价定标")
    t = frappe.get_doc("Tender", q.tender)
    if t.status == "已定标":
        frappe.throw("该招标已定标，如需改标请先联系管理员处理")
    if t.status != "已截止":
        frappe.throw("请先等报价截止（当前状态：{0}）".format(t.status))

    others = frappe.get_all(
        "Supplier Quote", filters={"tender": t.name, "name": ("!=", q.name)}, pluck="name"
    )
    for name in others:
        frappe.db.set_value("Supplier Quote", name, "awarded", 0)
    q.db_set("awarded", 1)
    t.db_set("status", "已定标")
    frappe.db.commit()
    return {"tender": t.name, "winner": q.supplier_name, "quote": q.name}


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
