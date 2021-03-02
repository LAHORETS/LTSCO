# -*- coding: utf-8 -*-
# from odoo import http


# class FbrNtn(http.Controller):
#     @http.route('/fbr_ntn/fbr_ntn/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fbr_ntn/fbr_ntn/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fbr_ntn.listing', {
#             'root': '/fbr_ntn/fbr_ntn',
#             'objects': http.request.env['fbr_ntn.fbr_ntn'].search([]),
#         })

#     @http.route('/fbr_ntn/fbr_ntn/objects/<model("fbr_ntn.fbr_ntn"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fbr_ntn.object', {
#             'object': obj
#         })
