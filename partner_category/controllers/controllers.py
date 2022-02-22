# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerCategory(http.Controller):
#     @http.route('/partner_category/partner_category', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_category/partner_category/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_category.listing', {
#             'root': '/partner_category/partner_category',
#             'objects': http.request.env['partner_category.partner_category'].search([]),
#         })

#     @http.route('/partner_category/partner_category/objects/<model("partner_category.partner_category"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_category.object', {
#             'object': obj
#         })
