from odoo import models, fields, api


class FbrTaxesPartner(models.Model):
    _inherit = 'res.partner'

    fbr_ntn = fields.Boolean("NTN")
    fbr_stn = fields.Boolean("STN")
    tax_type = fields.Selection(selection=[("unregister", "Unregistered"),
                                           ("register", "Register")], default="unregister", string="Tax type Scope")


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

    @api.depends("partner_id")
    def compute_case_partner(self):
        self.case1 = False
        self.case2 = False
        self.case3 = False
        if self.partner_id.tax_type == "unregister" and self.partner_id.fbr_ntn == True:
            if self.partner_id.fbr_stn == True:
                self.case1=True
        if self.partner_id.tax_type == "unregister" and self.partner_id.fbr_ntn == False:
            if self.partner_id.fbr_stn == True:
                self.case2 = True
        if self.partner_id.tax_type == "unregister" and self.partner_id.fbr_ntn == True:
            if self.partner_id.fbr_stn == False:
                self.case3 = True

    @api.depends("wth_amount", "tax_amount")
    def compute_after_WHT(self):
        self.amount_by_group = 0
        self.after_wht = 0

        if self.case1 == True:
            total = (self.amount_untaxed * (100 / (100 - self.wth_amount)))
            self.after_wht = total
            self.amount_by_group = self.after_wht - self.amount_untaxed

        # if self.case2 == True:
        #     total = self.grand_total * (self.wth_amount / 100)
        #     self.after_wht = total
        #     self.global_order_discount = total
        #     print("self.global_order_discount",self.global_order_discount)
        #     self.amount_by_group = self.after_wht - self.amount_untaxed


    @api.depends("tax_amount")
    def compute_after_tax_wht(self):
        self.after_tax_wht = 0
        if self.case1 == True:
            total = ((self.tax_amount / 100) * self.amount_untaxed)
            self.after_tax_wht = total


    @api.depends("after_tax_wht")
    def compute_grand_total(self):
        self.grand_total = 0
        if self.case1 == True:
            self.grand_total = self.after_tax_wht + self.after_wht



    @api.model
    def create(self, vals):
        rec=super(FbrTaxesAccount, self).create(vals)
        rec.action_calculate()

        return rec




    def action_calculate(self):
        if self.case1== True:
            expense_account = self.env['account.account'].search([('user_type_id', 'ilike', 'Expenses')])[0]
            pay_account = self.env['account.account'].search([('user_type_id', 'ilike', 'Payable')])[0]
            total_income_tax = 0
            total_sale_tax = 0
            total_income_tax = self.after_wht - self.amount_untaxed


            self.general_entry('Income Tax Expense', 'Income Tax Payable', expense_account, total_income_tax)
            self.general_entry('Sale Tax Expense', 'Sales Tax Payable', pay_account, self.after_tax_wht)




        # if self.case2== True:
        #     self.global_discount_type = 'fixed'
        #     expense_account = self.env['account.account'].search([('user_type_id', '=', 'Expenses')])[0]
        #     pay_account = self.env['account.account'].search([('user_type_id', '=', 'Payable')])[0]
        #     total_income_tax = 0
        #     total_sale_tax = 0
        #     total_income_tax = self.after_wht - self.amount_untaxed
        #     print("CASE 2",self.after_tax_wht)
        #
        #     # self.general_entry('Income Tax Expense', 'Income Tax Payable', expense_account, self.after_wht)
        #
        #     self.general_entry('Sale Tax Expense', 'Sales Tax Payable', pay_account, self.after_tax_wht)


    def general_entry(self, name_first, name_second, account, amount):

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
            'account_id': account.id,
            'exclude_from_invoice_tab': True
        })
        line_ids.append(credit_line)
        credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
        self.update({
            'line_ids': line_ids,

        })
        print("General entry created")




    def create_genral_entry(self):
        expense_account = self.env['account.account'].search([('user_type_id', '=', 'Expenses')])[0]
        pay_account = self.env['account.account'].search([('user_type_id', '=', 'Payable')])[0]
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        debit_line = (0, 0, {
            'name': "HUNAIN",
            'debit': 50,
            'credit': 0.0,
            'partner_id': self.partner_id.id,
            'account_id': expense_account.id,
            'exclude_from_invoice_tab': True
        })
        line_ids.append(debit_line)
        debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
        credit_line = (0, 0, {
            'name': "KHAN",
            'debit': 0.0,
            'partner_id': self.partner_id.id,
            'credit': 50,
            'account_id': pay_account.id,
            'exclude_from_invoice_tab': True
        })
        line_ids.append(credit_line)
        credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
        self.update({
            'line_ids': line_ids,
            'type':"entry"

        })
        print("General entry created")
