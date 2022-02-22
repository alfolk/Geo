# -*- coding: utf-8 -*-
# from odoo import http


# class AlfolkExpensePersonal(http.Controller):
#     @http.route('/alfolk_expense_personal/alfolk_expense_personal', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alfolk_expense_personal/alfolk_expense_personal/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('alfolk_expense_personal.listing', {
#             'root': '/alfolk_expense_personal/alfolk_expense_personal',
#             'objects': http.request.env['alfolk_expense_personal.alfolk_expense_personal'].search([]),
#         })

#     @http.route('/alfolk_expense_personal/alfolk_expense_personal/objects/<model("alfolk_expense_personal.alfolk_expense_personal"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alfolk_expense_personal.object', {
#             'object': obj
#         })
