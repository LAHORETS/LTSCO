# -*- coding: utf-8 -*-
# from odoo import http


# class EmployeeCustomization(http.Controller):
#     @http.route('/employee_customization/employee_customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_customization/employee_customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_customization.listing', {
#             'root': '/employee_customization/employee_customization',
#             'objects': http.request.env['employee_customization.employee_customization'].search([]),
#         })

#     @http.route('/employee_customization/employee_customization/objects/<model("employee_customization.employee_customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_customization.object', {
#             'object': obj
#         })
