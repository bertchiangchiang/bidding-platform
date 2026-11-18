

def set_all_zh():
    import frappe
    users = frappe.get_all("User", filters={"enabled": 1, "name": ("!=", "Guest")}, pluck="name")
    for u in users:
        frappe.db.set_value("User", u, "language", "zh")
    frappe.db.commit()
    print("已设置中文的用户:", users)


def hook_test():
    import frappe
    name = "hooktest@demo.local"
    if frappe.db.exists("User", name):
        frappe.delete_doc("User", name)
    doc = frappe.get_doc({
        "doctype": "User", "email": name, "first_name": "钩子测试",
        "language": "en", "new_password": "Test@2026x", "send_welcome_email": 0,
    }).insert(ignore_permissions=True)
    print("创建后 language =", doc.language)
    frappe.delete_doc("User", name)
    frappe.db.commit()
    print("已删除测试用户")


def setup_eval_demo():
    """评标演示：建评分模板→绑定招标单→录两单评分→招标单转已截止（供定标测试）"""
    import frappe
    from frappe.utils import flt

    frappe.set_user("Administrator")

    tpl_name = "标准综合评分模板"
    if not frappe.db.exists("Score Template", tpl_name):
        frappe.get_doc({
            "doctype": "Score Template",
            "template_name": tpl_name,
            "dimensions": [
                {"dimension_name": "价格", "weight": 40},
                {"dimension_name": "资质", "weight": 25},
                {"dimension_name": "交期", "weight": 15},
                {"dimension_name": "同类案例", "weight": 20},
            ],
        }).insert(ignore_permissions=True)
    print("评分模板:", frappe.db.exists("Score Template", tpl_name))

    tender = "TENDER-2026-00001"
    frappe.db.set_value("Tender", tender, "score_template", tpl_name)
    frappe.db.set_value("Tender", tender, "evaluation_mode", "按评分")

    quotes = frappe.get_all("Supplier Quote",
                            filters={"tender": tender, "docstatus": 1},
                            fields=["name", "supplier_name"])
    print("报价单:", quotes)

    base = {"宏达服饰": {"价格": 80, "资质": 85, "交期": 90, "同类案例": 75},
            "锦华制衣": {"价格": 78, "资质": 70, "交期": 80, "同类案例": 95}}
    for q in quotes:
        if frappe.db.exists("Evaluation", {"quote": q.name, "evaluator": "Administrator"}):
            continue
        scores = base.get(q.supplier_name, {"价格": 70, "资质": 70, "交期": 70, "同类案例": 70})
        rows = [{"dimension_name": k, "weight": w, "score": scores.get(k, 70)}
                for k, w in (("价格", 40), ("资质", 25), ("交期", 15), ("同类案例", 20))]
        doc = frappe.get_doc({
            "doctype": "Evaluation", "tender": tender, "quote": q.name,
            "evaluator": "Administrator", "scores": rows,
        }).insert(ignore_permissions=True)
        doc.submit()
        print("评分单:", doc.name, doc.quote, "总分", doc.total_score)

    frappe.db.set_value("Tender", tender, "status", "已截止")
    frappe.db.commit()
    print("招标单状态:", frappe.db.get_value("Tender", tender, "status"))
