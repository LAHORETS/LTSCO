# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    tax_state = fields.Selection([
        ('register', 'Register'),
        ('non_register', 'Non Register')
    ], string="Tax State")

    sale_tax = fields.Boolean("Sale Tax")
    income_tax = fields.Boolean("Income Tax")


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    tax_states = fields.Char("Tax State", readonly=True)
    sale_tax = fields.Boolean("Sale Tax")
    sale_tax2 = fields.Char("Sale Tax")
    income_tax = fields.Boolean("Income Tax")
    income_tax2 = fields.Char("Income Tax")

    @api.onchange('partner_id')
    def _onchange_customer(self):
        self.tax_states = self.partner_id.tax_state
        self.sale_tax = self.partner_id.sale_tax
        self.income_tax = self.partner_id.income_tax

    @api.onchange('income_tax2')
    def _onchange(self):
        self.amount_total += int(self.income_tax2) + int(self.sale_tax2)

    def _prepare_invoice(self):
        self.ensure_one()
        fbr_sale = self.env.ref('fbr_non_register.fbr_sale_tax').id
        fbr_income = self.env.ref('fbr_non_register.fbr_income_tax').id

        self = self.with_context(default_company_id=self.company_id.id, force_company=self.company_id.id)
        journal = self.env['account.move'].with_context(default_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'invoice_partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_payment_ref': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }

        so_line = self.order_line[0]
        line1 = {
            'name': 'Sale Tax',
            'price_unit': self.sale_tax2,
            'account_id': fbr_sale,
            # 'exclude_from_invoice_tab': True,

        }
        line2 = {
            'name': 'Income Tax',
            'price_unit': self.income_tax2,
            'account_id': fbr_income,
            # 'exclude_from_invoice_tab': True,

        }

        lines = [line1, line2]

        for line in lines:
            line['quantity'] = 1.0
            line['sale_line_ids'] = [(6, 0, [so_line.id])]
            line['analytic_tag_ids'] = [(6, 0, so_line.analytic_tag_ids.ids)]
            line['analytic_account_id'] = self.analytic_account_id.id or False

            invoice_vals['invoice_line_ids'].append(line)
        return invoice_vals

class VisioJournalItem(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_line = super(VisioJournalItem, self)._prepare_invoice_values(order, name, amount, so_line)
        # account_a = self.env.ref('visio_chargers_journal_item.visio_b_dividends').id
        # account_id = self.env.ref('visio_chargers_journal_item.visio_a_dividends').id
        # account_o = self.env.ref('visio_chargers_journal_item.visio_c_dividends').id

        fbr_sale = self.env.ref('fbr_non_register.fbr_sale_tax').id
        fbr_purchase = self.env.ref('fbr_non_register.fbr_purchase_tax').id
        fbr_income = self.env.ref('fbr_non_register.fbr_income_tax').id
        fbr_po_income = self.env.ref('fbr_non_register.fbr_purchase_income_tax').id

        # freight_account=self.env['account.account'].search([('name', '=', 'Freight Charger')])
        # insurance_account=self.env['account.account'].search([('name', '=', 'Premium Amount')])
        # account=self.env['account.account'].search([('name', '=', 'Tax Amount NTN')])

        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        order = sale_orders[0]
        po_order = purchase_orders[0]
        so_line = order.order_line[0]
        po_line = po_order.order_line[0]

        line1= {
            'name': 'Sale Tax',
            'price_unit': order.sale_tax2,
            'account_id': fbr_sale,
            # 'exclude_from_invoice_tab': True,

        }
        line2 = {
            'name': 'Income Tax',
            'price_unit': order.income_tax2,
            'account_id': fbr_income,
            # 'exclude_from_invoice_tab': True,

        }
        po_tax_line = {
            'name': 'Purchase Tax',
            'price_unit': po_order.purchase_tax,
            'account_id': fbr_purchase,
            'exclude_from_invoice_tab': True,

        }
        po_line_income = {
            'name': 'Purchase Income Tax',
            'price_unit': po_order.purchase_income_tax,
            'account_id': fbr_po_income,
            'exclude_from_invoice_tab': True,

        }
        # line3 = {
        #     'name': 'Tax Amount NTN',
        #     'price_unit': order.tax_id,
        #     'account_id': account_o,
        #     'exclude_from_invoice_tab': True,
        # }
        lines = [line1, line2]
        po_non_lines = [po_tax_line, po_line_income]

        for line in lines:
            line['quantity'] = 0.0
            line['sale_line_ids'] = [(6, 0, [so_line.id])]
            line['analytic_tag_ids'] = [(6, 0, so_line.analytic_tag_ids.ids)]
            line['analytic_account_id'] = order.analytic_account_id.id or False

            invoice_line['invoice_line_ids'].append(line)

        for po in po_non_lines:
            po['quantity'] = 1.0
            po['line_ids'] = [(6, 0, [po_line.id])]
            po['analytic_tag_ids'] = [(6, 0, po_line.analytic_tag_ids.ids)]
            po['analytic_account_id'] = po_order.analytic_account_id.id or False

            invoice_line['invoice_line_ids'].append(po)
        invoice_line.append(line2)

        # self.env['account.move'].sudo().create(invoice_vals).with_user(self.env.uid)
        return invoice_line

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    tax_states1 = fields.Char("Tax State")
    sale_tax1 = fields.Float("Sale Tax")
    income_tax1 = fields.Float("Income Tax")

    # @api.onchange('sale_tax1', 'income_tax1')
    # def _onchange_product(self):
    #     self.price_subtotal += self.sale_tax1 + self.income_tax1
    #     print("here is the subtotal", self.price_subtotal)

#
class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    purchase_tax = fields.Char('Sale Tax')
    purchase_income_tax = fields.Char("Income Tax")


#
#     def _prepare_invoice(self):
#         self.ensure_one()
#         # fbr_sale = self.env.ref('fbr_non_register.fbr_sale_tax').id
#         # fbr_income = self.env.ref('fbr_non_register.fbr_income_tax').id
#
#         fbr_purchase = self.env.ref('fbr_non_register.fbr_purchase_tax').id
#         fbr_po_income = self.env.ref('fbr_non_register.fbr_purchase_income_tax').id
#
#         self = self.with_context(default_company_id=self.company_id.id, force_company=self.company_id.id)
#         journal = self.env['account.move'].with_context(default_type='in_invoice')._get_default_journal()
#         # journal = self.env['account.move'].with_context(default_type='out_invoice')._get_default_journal()
#         if not journal:
#             raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (
#                 self.company_id.name, self.company_id.id))
#
#         invoice_vals = {
#             'ref': self.client_order_ref or '',
#             'type': 'in_invoice',
#             'narration': self.note,
#             'currency_id': self.pricelist_id.currency_id.id,
#             'campaign_id': self.campaign_id.id,
#             'medium_id': self.medium_id.id,
#             'source_id': self.source_id.id,
#             'invoice_user_id': self.user_id and self.user_id.id,
#             'team_id': self.team_id.id,
#             'partner_id': self.partner_invoice_id.id,
#             'partner_shipping_id': self.partner_shipping_id.id,
#             'invoice_partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
#             'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
#             'journal_id': journal.id,  # company comes from the journal
#             'invoice_origin': self.name,
#             'invoice_payment_term_id': self.payment_term_id.id,
#             'invoice_payment_ref': self.reference,
#             'transaction_ids': [(6, 0, self.transaction_ids.ids)],
#             'invoice_line_ids': [],
#             'company_id': self.company_id.id,
#         }
#
#         po_order = self.order_line[0]
#         po_tax_line = {
#             'name': 'Purchase Tax',
#             'price_unit': po_order.purchase_tax,
#             'account_id': fbr_purchase,
#             'exclude_from_invoice_tab': True,
#
#         }
#         po_line_income = {
#             'name': 'Purchase Income Tax',
#             'price_unit': po_order.purchase_income_tax,
#             'account_id': fbr_po_income,
#             'exclude_from_invoice_tab': True,
#
#         }
#
#         # lines = [line1, line2
#         po_non_lines = [po_tax_line, po_line_income]
#
#         # for line in lines:
#         for po in po_non_lines:
#             po['quantity'] = 1.0
#             po['sale_line_ids'] = [(6, 0, [po_order.id])]
#             po['analytic_tag_ids'] = [(6, 0, po_order.analytic_tag_ids.ids)]
#             po['analytic_account_id'] = self.analytic_account_id.id or False
#
#             invoice_vals['invoice_line_ids'].append(po)
#         return invoice_vals
