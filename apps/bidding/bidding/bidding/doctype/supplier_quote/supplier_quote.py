import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SupplierQuote(Document):
    def validate(self):
        total = 0
        for d in self.items:
            d.amount = flt(d.unit_price) * flt(d.qty)
            total += d.amount
        self.total_price = total
