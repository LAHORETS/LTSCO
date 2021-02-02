from odoo import models, fields, api,_


class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee Information'

    reference_no = fields.Char()
    employee_name=fields.Char()
    father_name = fields.Char(string="Father's Name")
    father_occupation = fields.Char(string="Father Occupation")
    blood_group = fields.Char(string="Blood Group")
    performance_manager = fields.Char(string="Performance Manager")
    leaving_date = fields.Date(string="Date Of Leaving")
    last_promotional_date = fields.Date(string="Last Promotional Date")
    joining_date = fields.Date(string="Date Of Joining")
    employee_type = fields.Selection([('permanent', 'Permanent'), ('contractual', 'Contractual'), ('part_time', 'Part Time')],string="Employment Type" )
    location_work = fields.Selection([('site', 'Site'), ('office', 'Office')],string="Work Location" )
    gender_c = fields.Selection([('male', 'Male'), ('female', 'Female')],string="Gender" )

    serial_number = fields.Char( copy=False, compute="_emp_serial_number_inherit",
                           index=True)

    def _emp_serial_number_inherit(self):
        for i in self:
            i.serial_number=('LTS-00'+str(i.id))


