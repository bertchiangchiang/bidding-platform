import frappe
from frappe import _
from frappe.utils import flt


class Evaluation(frappe.model.document.Document):
    def validate(self):
        quote = frappe.db.get_value(
            "Supplier Quote", self.quote, ["tender", "docstatus"], as_dict=1
        )
        if not quote or quote.tender != self.tender:
            frappe.throw(_("报价单与招标单不匹配"))
        if quote.docstatus != 1:
            frappe.throw(_("只能对已提交的报价评分"))

        # 评审人默认当前用户；同一评审人对同一报价只允许一张评分单
        if not self.evaluator:
            self.evaluator = frappe.session.user
        dup = frappe.db.exists(
            "Evaluation",
            {"quote": self.quote, "evaluator": self.evaluator, "name": ("!=", self.name)},
        )
        if dup:
            frappe.throw(_("该评审人已对此报价评分（{0}）").format(dup))

        # 明细为空时按招标单绑定的评分模板自动带出维度
        tender = frappe.get_doc("Tender", self.tender)
        if not (self.scores or []):
            if not tender.score_template:
                frappe.throw(_("该招标单未绑定评分模板，请先在招标单上设置"))
            tpl = frappe.get_doc("Score Template", tender.score_template)
            for row in tpl.dimensions:
                self.append(
                    "scores",
                    {"dimension_name": row.dimension_name, "weight": row.weight},
                )

        total = sum(flt(r.weight) * flt(r.score) for r in self.scores or []) / 100.0
        self.total_score = flt(total, 2)

        for r in self.scores or []:
            if not (0 <= flt(r.score) <= 100):
                frappe.throw(_("维度「{0}」得分必须在 0~100 之间").format(r.dimension_name))
