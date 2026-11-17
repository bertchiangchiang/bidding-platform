import frappe


def get_permission_query_conditions(user):
    if not user:
        return "0=1"
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "招标管理员" in roles:
        return ""
    return "`tabSupplier Quote`.`owner` = {}".format(frappe.db.escape(user))


def has_permission(doc, ptype, user):
    if not user:
        return False
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "招标管理员" in roles:
        return True
    if ptype in ("read", "write", "create") and doc.owner == user:
        return True
    return False


def update_website_context(context):
    # 框架登录页标题硬编码英文，App 层纠偏
    if context.get("title") == "Login":
        context["title"] = "登录"


def user_force_zh(doc, method=None):
    """新用户创建时强制默认简体中文（覆盖注册/后台新建/API 创建等所有路径）"""
    doc.language = "zh"
