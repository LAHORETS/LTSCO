# -*- coding: utf-8 -*-

from odoo import models, fields, api


class payroll(models.Model):
    _inherit = 'hr.payslip'

    month = fields.Char("Month", compute="compute_month")
    year = fields.Char("Year", compute="compute_year")
    dept = fields.Char("Department")

    def compute_month(self):
        for i in self:
            a = i.date_from.strftime("%B")
            i.month = a

    def compute_year(self):
        for i in self:
            a = i.date_from.strftime("%Y")
            i.year = a

