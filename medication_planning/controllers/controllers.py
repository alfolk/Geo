# -*- coding: utf-8 -*-
# from odoo import http


# class AlfolkMedicationChartRecord(http.Controller):
#     @http.route('/medication_planning/medication_planning', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/medication_planning/medication_planning/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('medication_planning.listing', {
#             'root': '/medication_planning/medication_planning',
#             'objects': http.request.env['medication_planning.medication_planning'].search([]),
#         })

#     @http.route('/medication_planning/medication_planning/objects/<model("medication_planning.medication_planning"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('medication_planning.object', {
#             'object': obj
#         })
