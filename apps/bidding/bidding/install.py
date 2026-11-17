import frappe


def after_install():
    for role_name, desk in (("招标管理员", 1), ("供应商", 0)):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc(
                {"doctype": "Role", "role_name": role_name, "desk_access": desk}
            ).insert(ignore_permissions=True)
    frappe.db.commit()
