# -*- coding: utf-8 -*-
# from odoo import http


# class FbrNonRegister(http.Controller):
#     @http.route('/fbr_non_register/fbr_non_register/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fbr_non_register/fbr_non_register/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fbr_non_register.listing', {
#             'root': '/fbr_non_register/fbr_non_register',
#             'objects': http.request.env['fbr_non_register.fbr_non_register'].search([]),
#         })

#     @http.route('/fbr_non_register/fbr_non_register/objects/<model("fbr_non_register.fbr_non_register"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fbr_non_register.object', {
#             'object': obj
#         })
