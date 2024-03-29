# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare

_logger = logging.getLogger(__name__)
class FbrTaxesPartner(models.Model):
    _inherit = 'res.partner'

    fbr_ntn = fields.Boolean("NTN")
    exempt = fields.Boolean("Exemption Certificate")
    fbr_stn = fields.Boolean("STN")
    tax_type = fields.Selection(selection=[("unregister", "Unregistered"),
                                           ("register", "Register")], default="unregister", string="Tax type Scope")

class AccountPayment(models.Model):
    _inherit = 'res.partner'

    partner_type=fields.Selection([("individual", "Individual"),
                                           ("company", "Company"),("aop", "AOP")])

    @api.onchange('partner_type')
    def _onchange_company_type(self):
        if self.partner_type =='individual' or 'aop':
            self.company_type='person'
        if self.partner_type == 'company':
            print("working")
            self.company_type = 'company'



class AccountMove(models.Model):
    _inherit = "account.move"

    exempt = fields.Boolean("Exemption Certificate",related='partner_id.exempt')
    wth_amount = fields.Integer("WHT")
    after_wht = fields.Float("WHT Amt", compute="compute_after_WHT")
    tax_amount = fields.Float("Tax %")
    after_tax_wht = fields.Float("Tax Amt", compute="compute_after_tax_wht")
    grand_total = fields.Float("Grand Total", compute="compute_grand_total")
    case1 = fields.Boolean("Case 1", compute="compute_case_partner")
    case2 = fields.Boolean("Case 2", compute="compute_case_partner")
    case3 = fields.Boolean("Case 3", compute="compute_case_partner")
    case4 = fields.Boolean("Case 3", compute="compute_case_partner")
    case = fields.Boolean("Case")
    fbr_taxes = fields.Integer(compute='compute_count')

    def compute_count(self):
        self.fbr_taxes=0
        self.fbr_taxes = self.env['account.move'].search_count([('ref', '=', self.name)])

    @api.depends("partner_id")
    def compute_case_partner(self):
        self.case1 = False
        self.case2 = False
        self.case3 = False
        self.case4 = False
        self.case = False
        if self.partner_id.tax_type == "unregister" and self.partner_id.fbr_ntn == True:
            if self.partner_id.fbr_stn == True:
                self.case1 = True
                self.case = True
                for i in self.invoice_line_ids:
                    i.case = True

        if self.partner_id.tax_type == "unregister" and self.partner_id.fbr_ntn == False:
            if self.partner_id.fbr_stn == True:
                self.case2 = True
                self.case = True

        if self.partner_id.tax_type == "register" and self.partner_id.fbr_ntn == True:
            if self.partner_id.fbr_stn == True:
                # if self.partner_id.company_type == 'person' or self.partner_id.company_type == 'aop':
                    self.case3 = True
                    self.case = True

        if self.partner_id.tax_type == "register" and self.partner_id.fbr_ntn == True:
            if self.partner_id.fbr_stn == True:
                if self.partner_id.company_type == 'company':
                    self.case4 = True
                    self.case = True

    @api.depends("wth_amount", "tax_amount", 'global_discount_type',
                 'global_order_discount')
    def compute_after_WHT(self):
        self.after_wht = 0
        if self.case1 == True:
            print("CASE WHT 1")
            total = (self.amount_untaxed * (100 / (100 - self.wth_amount)))
            self.after_wht = total
        if self.case2 == True:
            print("CASE WHT 2")
            total = (self.amount_untaxed + self.after_tax_wht) * (self.wth_amount / 100)
            self.after_wht = total
        if self.case3 == True:
            total = (self.amount_untaxed + self.after_tax_wht) * (self.wth_amount / 100)
            self.after_wht = total
        if self.case4 == True:
            total = (self.amount_untaxed +float(self.amount_tax)) * (self.wth_amount / 100)
            self.after_wht = total
            self.global_order_discount = self.after_wht

    @api.depends("wth_amount", "tax_amount", 'global_discount_type',
                 'global_order_discount')
    def compute_after_tax_wht(self):
        self.after_tax_wht = 0
        if self.case1 == True:
            total = ((self.tax_amount / 100) * self.after_wht)
            self.after_tax_wht = total
        if self.case2 == True:
            print("Case 2")
            total = ((self.tax_amount / 100) * self.amount_untaxed)
            self.after_tax_wht = total
        if self.case3 == True:
            print("Case 3")
            total = ((self.tax_amount / 100) * self.amount_untaxed)
            self.after_tax_wht = total
        if self.case4 == True:
            print("Case 4")
            total = ((self.tax_amount / 100) * self.amount_untaxed)
            self.after_tax_wht = float(self.amount_tax)

    @api.depends("after_tax_wht",'global_discount_type',
                 'global_order_discount')
    def compute_grand_total(self):
        self.grand_total = 0
        if self.case1 == True:
            self.grand_total = self.after_tax_wht + self.after_wht
        if self.case2 == True:
            self.grand_total = self.after_tax_wht + self.amount_untaxed
            self.global_order_discount = self.after_wht
        if self.case3 == True:
            self.grand_total = self.after_tax_wht + self.amount_untaxed
            self.global_order_discount = self.after_wht
        if self.case4==True:
            print("--------->",self.after_wht)
            self.grand_total = self.after_tax_wht + self.amount_untaxed


    def action_post(self):
        rec = super(AccountMove, self).action_post()
        self.action_calculate()
        return rec


    def get_vehicles(self):

        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'FBR Bills',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('ref', '=', self.name)],
            'context': "{'create': False}"
        }

    def action_calculate(self):
        if self.case1 == True:
            sale_expense = self.env['account.account'].search([('name', '=', 'Sales Tax Expenses')])[0]
            sale_payable = self.env['account.account'].search([('name', '=', 'Sales Tax Payable')])[0]
            income_expense = self.env['account.account'].search([('name', '=', 'Income Tax Expenses')])[0]
            income_payable = self.env['account.account'].search([('name', '=', 'Income Tax payable')])[0]
            journal = self.env['account.journal'].search([('name', 'ilike', 'Miscellaneous Operations')])[0]
            income_partner = self.env['res.partner'].search([('name', 'ilike', 'Income Tax Payable')], limit=1)
            sales_partner = self.env['res.partner'].search([('name', 'ilike', 'Sales Tax Payable')], limit=1)
            print("sales_partner",sales_partner)
            ref = self.name
            total_income_tax = 0
            total_sale_tax = 0
            total_income_tax = self.after_wht - self.amount_untaxed
            self.general_entry('Sale Tax Expense', 'Sales Tax Payable', sale_expense, sale_payable, self.after_tax_wht,
                               ref, journal,sales_partner)
            self.general_entry('Income Tax Expense', 'Income Tax Payable', income_expense, income_payable,
                               total_income_tax, ref, journal,income_partner)

        if self.case2 == True:
            journal = self.env['account.journal'].search([('name', 'ilike', 'Miscellaneous Operations')])[0]
            sales_partner = self.env['res.partner'].search([('name', 'ilike', 'Sales Tax Payable')], limit=1)
            ref = self.name
            sale_expense = self.env['account.account'].search([('name', '=', 'Sales Tax Expenses')])[0]
            sale_payable = self.env['account.account'].search([('name', '=', 'Sales Tax Payable')])[0]
            total_sale_tax = self.after_tax_wht
            self.general_entry('Sale Tax Expense', 'Sales Tax Payable', sale_expense, sale_payable, total_sale_tax, ref,
                               journal,sales_partner )

        if self.case3 == True:
            journal = self.env['account.journal'].search([('name', 'ilike', 'Miscellaneous Operations')])[0]
            sales_partner = self.env['res.partner'].search([('name', 'ilike', 'Sales Tax Payable')], limit=1)
            ref = self.name
            sale_current_asset = self.env['account.account'].search([('name', '=', 'Sales Tax Current Asset')])[0]
            sale_payable = self.env['account.account'].search([('name', '=', 'Sales Tax Payable')])[0]
            total_sale_tax = self.after_tax_wht

            self.general_entry('Sales Tax Current Asset', 'Sales Tax Payable', sale_current_asset, sale_payable,
                               total_sale_tax, ref, journal,sales_partner )

    def action_create_line(self):
        product = self.env['product.product'].search([('name', '=', 'FBR')], limit=1)
        income_payable = self.env['account.account'].search([('name', '=', 'Income Tax payable')])[0]
        vals = {
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,
            'price_unit': -1 * (self.after_wht),
            'account_id': income_payable.id,
            'move_id': self.id,
        }
        move = self.env['account.move.line'].create(vals)


    def general_entry(self, name_first, name_second, account, account_2, amount, ref, journal,partner):

        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        print("parnter",partner)
        product = self.env['product.product'].search([('name', '=', 'FBR')], limit=1)
        if partner and product:
            debit_line = (0, 0, {
                'name': name_first,
                'debit': amount,
                'credit': 0.0,
                'partner_id': partner.id,
                'account_id': account.id,
                'exclude_from_invoice_tab': True,
            })
            line_ids.append(debit_line)
            debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
            credit_line = (0, 0, {
                'name': name_second,
                'debit': 0.0,
                'partner_id': partner.id,
                'credit': amount,
                'account_id': account_2.id,
                'exclude_from_invoice_tab': True,
            })
            line_ids.append(credit_line)
            credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            vals = {
                'date': fields.Date.today(),
                'ref': ref,
                'invoice_origin': ref,
                'journal_id': journal.id,
                'partner_id': partner.id,
                'type': 'entry',
                'line_ids': line_ids,
                'auto_post': True,
            }
            move = self.env['account.move'].create(vals)

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        ''' Compute the dynamic tax lines of the journal entry.

        :param lines_map: The line_ids dispatched by type containing:
            * base_lines: The lines having a tax_ids set.
            * tax_lines: The lines having a tax_line_id set.
            * terms_lines: The lines generated by the payment terms of the invoice.
            * rounding_lines: The cash rounding lines of the invoice.
        '''
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                if base_line.currency_id:
                    if base_line.discount_type and base_line.discount_type == 'fixed':
                        price_unit_foreign_curr = sign * (base_line.price_unit - (base_line.discount / (base_line.quantity or 1.0)))
                    else:
                        price_unit_foreign_curr = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
                    price_unit_comp_curr = base_line.currency_id._convert(price_unit_foreign_curr, move.company_id.currency_id, move.company_id, move.date, round=False)
                else:
                    price_unit_foreign_curr = 0.0
                    if base_line.discount_type and base_line.discount_type == 'fixed':
                        price_unit_comp_curr = sign * (base_line.price_unit - (base_line.discount / (base_line.quantity or 1.0)))
                    else:
                        price_unit_comp_curr = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
                tax_type = 'sale' if move.type.startswith('out_') else 'purchase'
                is_refund = move.type in ('out_refund', 'in_refund')
            else:
                handle_price_include = False
                quantity = 1.0
                price_unit_foreign_curr = base_line.amount_currency
                price_unit_comp_curr = base_line.balance
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)

            balance_taxes_res = base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
                price_unit_comp_curr,
                currency=base_line.company_currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
            )

            if move.type == 'entry':
                repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
                repartition_tags = base_line.tax_ids.mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
                tags_need_inversion = (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund)
                if tags_need_inversion:
                    balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
                    for tax_res in balance_taxes_res['taxes']:
                        tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

            if base_line.currency_id:
                # Multi-currencies mode: Taxes are computed both in company's currency / foreign currency.
                amount_currency_taxes_res = base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
                    price_unit_foreign_curr,
                    currency=base_line.currency_id,
                    quantity=quantity,
                    product=base_line.product_id,
                    partner=base_line.partner_id,
                    is_refund=self.type in ('out_refund', 'in_refund'),
                    handle_price_include=handle_price_include,
                )

                if move.type == 'entry':
                    repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
                    repartition_tags = base_line.tax_ids.mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
                    tags_need_inversion = (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund)
                    if tags_need_inversion:
                        balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
                        for tax_res in balance_taxes_res['taxes']:
                            tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

                for b_tax_res, ac_tax_res in zip(balance_taxes_res['taxes'], amount_currency_taxes_res['taxes']):
                    tax = self.env['account.tax'].browse(b_tax_res['id'])
                    b_tax_res['amount_currency'] = ac_tax_res['amount']

                    # A tax having a fixed amount must be converted into the company currency when dealing with a
                    # foreign currency.
                    if tax.amount_type == 'fixed':
                        b_tax_res['amount'] = base_line.currency_id._convert(b_tax_res['amount'], move.company_id.currency_id, move.company_id, move.date)

            return balance_taxes_res

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'balance': 0.0,
                    'amount_currency': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                line.tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            line.tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]

            tax_exigible = True
            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                if tax.tax_exigibility == 'on_payment':
                    tax_exigible = False

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'balance': 0.0,
                    'amount_currency': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['balance'] += tax_vals['amount']
                taxes_map_entry['amount_currency'] += tax_vals.get('amount_currency', 0.0)
                taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'], tax_repartition_line)
                taxes_map_entry['grouping_dict'] = grouping_dict
            line.tax_exigible = tax_exigible

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # Don't create tax lines with zero balance.
            if self.currency_id.is_zero(taxes_map_entry['balance']) and self.currency_id.is_zero(taxes_map_entry['amount_currency']):
                taxes_map_entry['grouping_dict'] = False

            tax_line = taxes_map_entry['tax_line']

            if not tax_line and not taxes_map_entry['grouping_dict']:
                continue
            elif tax_line and not taxes_map_entry['grouping_dict']:
                # The tax line is no longer used, drop it.
                self.line_ids -= tax_line
            elif tax_line and recompute_tax_base_amount:
                tax_line.tax_base_amount = taxes_map_entry['tax_base_amount']
            elif tax_line:
                tax_line.update({
                    'amount_currency': taxes_map_entry['amount_currency'],
                    'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
                    'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
                    'tax_base_amount': taxes_map_entry['tax_base_amount'],
                })
            else:
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                tax_line = create_method({
                    'name': tax.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'quantity': 1.0,
                    'date_maturity': False,
                    'amount_currency': taxes_map_entry['amount_currency'],
                    'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
                    'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
                    'tax_base_amount': taxes_map_entry['tax_base_amount'],
                    'exclude_from_invoice_tab': True,
                    'tax_exigible': tax.tax_exigibility == 'on_invoice',
                    **taxes_map_entry['grouping_dict'],
                })

            if in_draft_mode:
                tax_line._onchange_amount_currency()
                tax_line._onchange_balance()

    @api.depends('line_ids.debit', 'line_ids.credit', 'line_ids.currency_id',
                 'line_ids.amount_currency', 'line_ids.amount_residual',
                 'line_ids.amount_residual_currency',
                 'line_ids.payment_id.state', 'global_discount_type',
                 'global_order_discount')
    def _compute_amount(self):
        invoice_ids = [
            move.id for move in self
            if move.id and move.is_invoice(include_receipts=True)
        ]
        self.env['account.payment'].flush(['state'])
        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                UNION
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(invoice_ids), tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            total_global_discount = 0.0
            total_discount = 0.0
            global_discount = 0.0
            global_discount_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                        total_discount += line.discount if line.discount_type == 'fixed' else line.quantity * line.price_unit * line.discount / 100.0
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.is_global_line:
                        # Discount amount.
                        global_discount = line.balance
                        global_discount_currency = line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1

            total_global_discount = -1 * sign * (global_discount_currency if len(
                currencies) == 1 else global_discount)
            total_discount += total_global_discount
            move.total_global_discount = total_global_discount
            move.total_discount = total_discount
            move.amount_untaxed = sign * (total_untaxed_currency if len(
                currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.type == 'entry':
                move.invoice_payment_state = False
            elif move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
            else:
                move.invoice_payment_state = 'not_paid'

    total_global_discount = fields.Monetary(string='Total Income Tax',
        store=True, readonly=True, default=0, compute='_compute_amount')
    total_discount = fields.Monetary(string='Income Tax Payalbe', store=True,
        readonly=True, default=0, compute='_compute_amount', tracking=True)
    global_discount_type = fields.Selection([('fixed', 'Percent'),
                                             ('percent', 'Fixed')],
                                            string="Income Tax Type", default='percent',tracking=True)
    global_order_discount = fields.Float(string='Income Tax', store=True, tracking=True)

    @api.onchange('global_discount_type', 'global_order_discount')
    def _onchange_global_order_discount(self):
        # if self.global_discount_type:
        #     self.wth_amount=6
        #     self.tax_amount=16
        if not self.global_order_discount:
            global_discount_line = self.line_ids.filtered(lambda line: line.is_global_line)
            self.line_ids -= global_discount_line
        self._recompute_dynamic_lines()

    def _recompute_global_discount_lines(self):
        ''' Compute the dynamic global discount lines of the journal entry.'''
        self.ensure_one()
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)

        def _compute_payment_terms(self):
            sign = 1 if self.is_inbound() else -1

            IrConfigPrmtrSudo = self.env['ir.config_parameter'].sudo()
            discTax = IrConfigPrmtrSudo.get_param('account.global_discount_tax')
            if not discTax:
                discTax = 'untax'

            discount_balance = 0.0

            total = self.amount_untaxed + self.amount_tax
            if discTax != 'taxed':
                total = self.amount_untaxed

            if self.global_discount_type == 'fixed':
                discount_balance = sign * (self.global_order_discount or 0.0)
            else:
                discount_balance = sign * (total * (self.global_order_discount or 0.0) / 100)

            if self.currency_id == self.company_id.currency_id:
                discount_amount_currency = 0.0
            else:
                discount_amount_currency = discount_balance
                discount_balance = self.currency_id._convert(
                    discount_amount_currency, self.company_id.currency_id, self.company_id, self.date)

            if self.invoice_payment_term_id:
                date_maturity = self.invoice_date or today
            else:
                date_maturity = self.invoice_date_due or self.invoice_date or today
            return [(date_maturity, discount_balance, discount_amount_currency)]

        def _compute_diff_global_discount_lines(self, existing_global_lines, account, to_compute):
            new_global_discount_lines = self.env['account.move.line']
            for date_maturity, balance, amount_currency in to_compute:
                if existing_global_lines:
                    candidate = existing_global_lines[0]
                    candidate.update({
                        'date_maturity': date_maturity,
                        'amount_currency': amount_currency,
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                    })
                else:
                    create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                    candidate = create_method({
                        'name': 'Income Tax Payable',
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                        'quantity': 1.0,
                        'amount_currency': amount_currency,
                        'date_maturity': date_maturity,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                        'is_global_line': True,
                    })
                new_global_discount_lines += candidate
                if in_draft_mode:
                    candidate._onchange_amount_currency()
                    candidate._onchange_balance()
            return new_global_discount_lines

        existing_global_lines = self.line_ids.filtered(lambda line: line.is_global_line)
        others_lines = self.line_ids.filtered(lambda line: not line.is_global_line)

        if not others_lines:
            self.line_ids -= existing_global_lines
            return

        if existing_global_lines:
            account = existing_global_lines[0].account_id
        else:
            IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
            if self.type in ['out_invoice', 'out_refund', 'out_receipt']:
                account = self.env.company.discount_account_invoice
            else:
                account = self.env.company.discount_account_bill
            if not account:
                raise UserError(
                    _("Income Tax Type!\nPlease first set account for global discount in account setting."))

        to_compute = _compute_payment_terms(self)

        new_terms_lines = _compute_diff_global_discount_lines(self, existing_global_lines, account, to_compute)

        self.line_ids -= existing_global_lines - new_terms_lines

    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        ''' Recompute all lines that depend of others.

        For example, tax lines depends of base lines (lines having tax_ids set). This is also the case of cash rounding
        lines that depend of base lines or tax lines depending the cash rounding strategy. When a payment term is set,
        this method will auto-balance the move with payment term lines.

        :param recompute_all_taxes: Force the computation of taxes. If set to False, the computation will be done
                                    or not depending of the field 'recompute_tax_line' in lines.
        '''
        for invoice in self:
            if invoice.global_order_discount:
                # Dispatch lines and pre-compute some aggregated values like taxes.
                for line in invoice.line_ids:
                    if line.recompute_tax_line:
                        recompute_all_taxes = True
                        line.recompute_tax_line = False

                # Compute taxes.
                if recompute_all_taxes:
                    invoice._recompute_tax_lines()
                if recompute_tax_base_amount:
                    invoice._recompute_tax_lines(recompute_tax_base_amount=True)

                if invoice.is_invoice(include_receipts=True):

                    # Compute cash rounding.
                    invoice._recompute_cash_rounding_lines()

                    # Compute global discount line.
                    invoice._recompute_global_discount_lines()

                    # Compute payment terms.
                    invoice._recompute_payment_terms_lines()

                    # Only synchronize one2many in onchange.
                    if invoice != invoice._origin:
                        invoice.invoice_line_ids = invoice.line_ids.filtered(
                            lambda line: not line.exclude_from_invoice_tab)
            else:
                super(AccountMove, invoice)._recompute_dynamic_lines(
                    recompute_all_taxes=recompute_all_taxes,
                    recompute_tax_base_amount=recompute_tax_base_amount)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_type = fields.Selection([('fixed', 'Fixed'),
                                      ('percent', 'Percent')],
                                     string="Income Tax Type", default="percent")
    is_global_line = fields.Boolean(string='Global Discount Line',
        help="This field is used to separate global discount line.")

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        # Compute 'price_subtotal'.
        discount_type = ''
        if self._context and self._context.get('wk_vals_list', []):
            for vals in self._context.get('wk_vals_list', []):
                if price_unit == vals.get('price_unit', 0.0) and quantity == vals.get('quantity', 0.0) and discount == vals.get('discount', 0.0) and product.id == vals.get('product_id', False) and partner.id == vals.get('partner_id', False):
                    discount_type = vals.get('discount_type', '')
        discount_type = self.discount_type or discount_type or ''
        if discount_type == 'fixed':
            price_unit_wo_discount = price_unit * quantity - discount
            quantity = 1.0
        else:
            price_unit_wo_discount = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * price_unit_wo_discount

        # Compute 'price_total'.
        if taxes:
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(price_unit_wo_discount,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res

    @api.model
    def _get_fields_onchange_balance_model(self, quantity, discount, balance, move_type, currency, taxes, price_subtotal, force_computation=False):
        ''' This method is used to recompute the values of 'quantity', 'discount', 'price_unit' due to a change made
        in some accounting fields such as 'balance'.

        This method is a bit complex as we need to handle some special cases.
        For example, setting a positive balance with a 100% discount.

        :param quantity:        The current quantity.
        :param discount:        The current discount.
        :param balance:         The new balance.
        :param move_type:       The type of the move.
        :param currency:        The currency.
        :param taxes:           The applied taxes.
        :param price_subtotal:  The price_subtotal.
        :return:                A dictionary containing 'quantity', 'discount', 'price_unit'.
        '''
        balance_form = 'credit' if balance > 0 else 'debit'
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        balance *= sign

        # Avoid rounding issue when dealing with price included taxes. For example, when the price_unit is 2300.0 and
        # a 5.5% price included tax is applied on it, a balance of 2300.0 / 1.055 = 2180.094 ~ 2180.09 is computed.
        # However, when triggering the inverse, 2180.09 + (2180.09 * 0.055) = 2180.09 + 119.90 = 2299.99 is computed.
        # To avoid that, set the price_subtotal at the balance if the difference between them looks like a rounding
        # issue.
        if not force_computation and currency.is_zero(balance - price_subtotal):
            return {}

        taxes = taxes.flatten_taxes_hierarchy()
        if taxes and any(tax.price_include for tax in taxes):
            # Inverse taxes. E.g:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 110           | 10% incl, 5%  |                   | 100               | 115
            # 10            |               | 10% incl          | 10                | 10
            # 5             |               | 5%                | 5                 | 5
            #
            # When setting the balance to -200, the expected result is:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 220           | 10% incl, 5%  |                   | 200               | 230
            # 20            |               | 10% incl          | 20                | 20
            # 10            |               | 5%                | 10                | 10
            taxes_res = taxes._origin.compute_all(balance, currency=currency, handle_price_include=False)
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                if tax.price_include:
                    balance += tax_res['amount']

        discount_type = ''
        if self._context and self._context.get('wk_vals_list', []):
            for vals in self._context.get('wk_vals_list', []):
                if quantity == vals.get('quantity', 0.0) and discount == vals.get('discount', 0.0) and balance == vals.get(balance_form, 0.0):
                    discount_type = vals.get('discount_type', '')
        discount_type = self.discount_type or discount_type or ''
        if discount_type == 'fixed':
            if balance:
                vals = {
                    'quantity': quantity or 1.0,
                    'price_unit': (balance + discount) / (quantity or 1.0),
                }
            else:
                vals = {'price_unit': 0.0}
        else:
            discount_factor = 1 - (discount / 100.0)
            if balance and discount_factor:
                # discount != 100%
                vals = {
                    'quantity': quantity or 1.0,
                    'price_unit': balance / discount_factor / (quantity or 1.0),
                }
            elif balance and not discount_factor:
                # discount == 100%
                vals = {
                    'quantity': quantity or 1.0,
                    'discount': 0.0,
                    'price_unit': balance / (quantity or 1.0),
                }
            elif not discount_factor:
                # balance of line is 0, but discount  == 100% so we display the normal unit_price
                vals = {}
            else:
                # balance is 0, so unit price is 0 as well
                vals = {'price_unit': 0.0}
        return vals

    @api.onchange('quantity', 'discount', 'discount_type', 'price_unit', 'tax_ids')
    def _onchange_price_subtotal(self):
        return super(AccountMoveLine, self)._onchange_price_subtotal()

    @api.model_create_multi
    def create(self, vals_list):
        context = self._context.copy()
        context.update({'wk_vals_list': vals_list})
        res = super(AccountMoveLine, self.with_context(context)).create(vals_list)
        return res
