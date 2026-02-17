# -*- coding: utf-8 -*-
# from odoo import http


# class G3Bank(http.Controller):
#     @http.route('/g3_bank/g3_bank', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/g3_bank/g3_bank/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('g3_bank.listing', {
#             'root': '/g3_bank/g3_bank',
#             'objects': http.request.env['g3_bank.g3_bank'].search([]),
#         })

#     @http.route('/g3_bank/g3_bank/objects/<model("g3_bank.g3_bank"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('g3_bank.object', {
#             'object': obj
#         })
