# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    tax_state = fields.Selection([
        ('Register', 'Register'),
        ('Non Register', 'Non Register')
    ], string="FBR Status")

    sale_tax = fields.Boolean("Sale Tax")
    income_tax = fields.Boolean("Income Tax")


class SaleOrderInherit(models.Model):
    _inherit = 'account.move'

    tax_states = fields.Char("FBR Status", readonly=True)
    sale_tax = fields.Boolean("Sale Tax")
    income_tax = fields.Boolean("Income Tax")

    @api.onchange('partner_id')
    def _onchange_customer(self):
        self.tax_states = self.partner_id.tax_state
        self.sale_tax = self.partner_id.sale_tax
        self.income_tax = self.partner_id.income_tax
