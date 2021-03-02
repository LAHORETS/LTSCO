# -*- coding: utf-8 -*-
# from odoo import http


# class FbrRegister(http.Controller):
#     @http.route('/fbr_register/fbr_register/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fbr_register/fbr_register/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fbr_register.listing', {
#             'root': '/fbr_register/fbr_register',
#             'objects': http.request.env['fbr_register.fbr_register'].search([]),
#         })

#     @http.route('/fbr_register/fbr_register/objects/<model("fbr_register.fbr_register"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fbr_register.object', {
#             'object': obj
#         })
