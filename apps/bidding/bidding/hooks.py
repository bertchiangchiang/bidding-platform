app_name = "bidding"
app_title = "招标询比价"
app_publisher = "IT Center"
app_description = "招标询比价系统：外发需求、供应商报价、评标排名（价格对供应商隐藏）"
app_license = "MIT"

after_install = "bidding.install.after_install"
update_website_context = "bidding.overrides.update_website_context"

permission_query_conditions = {
    "Supplier Quote": "bidding.overrides.get_permission_query_conditions",
}
has_permission = {
    "Supplier Quote": "bidding.overrides.has_permission",
}

doc_events = {
    "User": {"before_insert": "bidding.overrides.user_force_zh"},
}
