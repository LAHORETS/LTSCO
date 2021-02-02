# -*- coding: utf-8 -*-
# from odoo import http


# class Lts-emp(http.Controller):
#     @http.route('/lts-emp/lts-emp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lts-emp/lts-emp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lts-emp.listing', {
#             'root': '/lts-emp/lts-emp',
#             'objects': http.request.env['lts-emp.lts-emp'].search([]),
#         })

#     @http.route('/lts-emp/lts-emp/objects/<model("lts-emp.lts-emp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lts-emp.object', {
#             'object': obj
#         })
