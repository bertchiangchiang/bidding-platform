

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
        "language": "en", "new_password": "CHANGE_ME_TEST_PASSWORD", "send_welcome_email": 0,
    }).insert(ignore_permissions=True)
    print("创建后 language =", doc.language)
    frappe.delete_doc("User", name)
    frappe.db.commit()
    print("已删除测试用户")
