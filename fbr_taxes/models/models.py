from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError


class FbrTaxesPartner(models.Model):
    _inherit = 'res.partner'

    fbr_ntn = fields.Boolean("NTN")
    fbr_stn = fields.Boolean("STN")
    tax_type = fields.Selection(selection=[("unregister", "Unregistered"),
                                           ("register", "Register")], default="unregister", string="Tax type Scope")

    company_type = fields.Selection(string='Company Type', selection=[('person', 'Individual/AOP'), ('company', 'Company')],  compute='_compute_company_type', inverse='_write_company_type')


class FbrTaxesAccount(models.Model):
    _inherit = 'account.move'

    wth_amount=fields.Integer("WHT")
    after_wht = fields.Float("WHT Amt",compute="compute_after_WHT")
    tax_amount = fields.Float("Tax %")
    after_tax_wht = fields.Float("Tax Amt", compute="compute_after_tax_wht")
    grand_total= fields.Float("Grand Total", compute="compute_grand_total")
    case1= fields.Boolean("Case 1", compute="compute_case_partner")
    case2 = fields.Boolean("Case 2", compute="compute_case_partner")
    case3 = fields.Boolean("Case 3", compute="compute_case_partner")
    case = fields.Boolean("Case")

    @api.depends("partner_id")
    def compute_case_partner(self):
        self.case1 = False
        self.case2 = False
        self.case3 = False
        self.case = False
        if self.partner_id.tax_type == "unregister" and self.partner_id.fbr_ntn == True:
            if self.partner_id.fbr_stn == True:
                self.case1=True
                self.case = True
                for i in self.invoice_line_ids:
                    i.case=True

        if self.partner_id.tax_type == "unregister" and self.partner_id.fbr_ntn == False:
            if self.partner_id.fbr_stn == True:
                self.case2 = True
                self.case = True


        if self.partner_id.tax_type == "unregister" and self.partner_id.fbr_ntn == False:
            if self.partner_id.fbr_stn == False:
                self.case3 = True
                self.case = True

    @api.depends("wth_amount", "tax_amount")
    def compute_after_WHT(self):
        self.amount_by_group = 0
        self.after_wht = 0

        if self.case1 == True:
            print("CASE WHT 1")
            total = (self.amount_untaxed * (100 / (100 - self.wth_amount)))
            self.after_wht = total
        if self.case2 == True:
            print("CASE WHT 2")
            total = (self.amount_untaxed +self.after_tax_wht)*(self.wth_amount/100)
            self.after_wht = total
        if self.case3 == True:
            total = (self.amount_untaxed + self.after_tax_wht) * (self.wth_amount / 100)
            self.after_wht = total

    @api.depends("tax_amount")
    def compute_after_tax_wht(self):
        self.after_tax_wht = 0
        if self.case1 == True:
            total = ((self.tax_amount / 100) * self.after_wht)
            self.after_tax_wht = total
            # self.amount_by_group =total
        if self.case2 == True:
            print("Case 2")
            total = ((self.tax_amount / 100) * self.amount_untaxed)
            self.after_tax_wht = total
        if self.case3 == True:
            print("Case 3")
            total = ((self.tax_amount / 100) * self.amount_untaxed)
            self.after_tax_wht = total

    @api.depends("after_tax_wht")
    def compute_grand_total(self):
        self.grand_total = 0
        if self.case1 == True:
            self.grand_total = self.after_tax_wht + self.after_wht
        if self.case2 == True:
            self.grand_total = self.after_tax_wht + self.amount_untaxed
            self.global_order_discount=self.after_wht
        if self.case3 == True:
            self.grand_total = self.after_tax_wht + self.amount_untaxed
            self.global_order_discount=self.after_wht

    @api.model
    def create(self, vals):
        rec=super(FbrTaxesAccount, self).create(vals)
        rec.action_calculate()
        # rec.onchange_global_order_discount()
        return rec

    def action_calculate(self):
        if self.case1== True:
            sale_expense = self.env['account.account'].search([('name', '=', 'Sales Tax Expenses')])[0]
            if not sale_expense:
                raise UserError(_("Create account of Sales Tax Expenses"))
            sale_payable = self.env['account.account'].search([('name', '=', 'Sales Tax Payable')])[0]
            if not sale_payable:
                raise UserError(_("Create account of Sales Tax Payable"))
            income_expense = self.env['account.account'].search([('name', '=', 'Income Tax Expenses')])[0]
            if not income_expense:
                raise UserError(_("Create account of Income Tax Expenses"))
            income_payable = self.env['account.account'].search([('name', '=', 'Income Tax payable')])[0]
            if not income_payable:
                raise UserError(_("Create account of Income Tax payable"))

            total_income_tax = 0
            total_sale_tax = 0
            total_income_tax = self.after_wht - self.amount_untaxed
            self.general_entry('Sale Tax Expense', 'Sales Tax Payable', sale_expense,sale_payable,self.after_tax_wht )
            self.general_entry('Income Tax Expense', 'Income Tax Payable',income_expense,income_payable, total_income_tax)


        if self.case2 == True:
            print("Case 2 running")
            sale_expense = self.env['account.account'].search([('name', '=', 'Sales Tax Expenses')])[0]
            if not sale_expense:
                raise UserError(_("Create account of Sales Tax Expenses"))

            sale_payable = self.env['account.account'].search([('name', '=', 'Sales Tax Payable')])[0]
            if not sale_payable:
                raise UserError(_("Create account of Sales Tax Expenses"))

            income_expense = self.env['account.account'].search([('name', '=', 'Income Tax Expenses')])[0]
            if not income_expense:
                raise UserError(_("Create account of Sales Tax Expenses"))

            income_payable = self.env['account.account'].search([('name', '=', 'Income Tax payable')])[0]
            if not income_payable:
                raise UserError(_("Create account of Sales Tax Expenses"))

            total_sale_tax = self.after_tax_wht
            self.general_entry('Sale Tax Expense', 'Sales Tax Payable', sale_expense,sale_payable,  total_sale_tax)

        if self.case3== True:
            sale_current_asset = self.env['account.account'].search([('name', '=', 'Sales Tax Current Asset')])[0]
            if not sale_current_asset :
                raise UserError(_("Create account of Sales Tax Current Asset"))

            sale_payable = self.env['account.account'].search([('name', '=', 'Sales Tax Payable')])[0]
            if not sale_payable:
                raise UserError(_("Create account of Sales Tax Payable"))

            income_expense = self.env['account.account'].search([('name', '=', 'Income Tax Expenses')])[0]
            if not income_expense:
                raise UserError(_("Create account of Income Tax Expenses"))

            income_payable = self.env['account.account'].search([('name', '=', 'Income Tax Expenses')])[0]
            if not income_payable:
                raise UserError(_("Create account of Income Tax Expenses"))

            total_sale_tax = self.after_tax_wht
            self.general_entry('Sales Tax Current Asset', 'Sales Tax Payable', sale_current_asset,sale_payable, total_sale_tax)

    def general_entry(self, name_first, name_second, account,account_2, amount):

        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        debit_line = (0, 0, {
            'name': name_first,
            'debit': amount,
            'credit': 0.0,
            'partner_id': self.partner_id.id,
            'account_id': account.id,
            'exclude_from_invoice_tab': True
        })
        line_ids.append(debit_line)
        debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
        credit_line = (0, 0, {
            'name': name_second,
            'debit': 0.0,
            'partner_id': self.partner_id.id,
            'credit': amount,
            'account_id': account_2.id,
            'exclude_from_invoice_tab': True
        })
        line_ids.append(credit_line)
        credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
        self.update({
            'line_ids': line_ids, })