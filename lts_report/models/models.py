# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    payment_mode = fields.Selection(selection=[("bank", "Bank"),
                                           ("cash", "Cash")], default="bank", string="Payment Mode")