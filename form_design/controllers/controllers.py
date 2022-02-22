# -*- coding: utf-8 -*-
# from odoo import http


# class FormDesign(http.Controller):
#     @http.route('/form_design/form_design', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/form_design/form_design/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('form_design.listing', {
#             'root': '/form_design/form_design',
#             'objects': http.request.env['form_design.form_design'].search([]),
#         })

#     @http.route('/form_design/form_design/objects/<model("form_design.form_design"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('form_design.object', {
#             'object': obj
#         })
