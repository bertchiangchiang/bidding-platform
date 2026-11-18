import frappe
from frappe import _
from frappe.utils import flt


class ScoreTemplate(frappe.model.document.Document):
    def validate(self):
        total = sum(flt(r.weight) for r in self.dimensions or [])
        if flt(total, 2) != 100:
            frappe.throw(_("维度权重合计必须等于 100%，当前合计 {0}%").format(total))
