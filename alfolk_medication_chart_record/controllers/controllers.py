# -*- coding: utf-8 -*-
# from odoo import http


# class AlfolkMedicationChartRecord(http.Controller):
#     @http.route('/alfolk_medication_chart_record/alfolk_medication_chart_record', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alfolk_medication_chart_record/alfolk_medication_chart_record/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('alfolk_medication_chart_record.listing', {
#             'root': '/alfolk_medication_chart_record/alfolk_medication_chart_record',
#             'objects': http.request.env['alfolk_medication_chart_record.alfolk_medication_chart_record'].search([]),
#         })

#     @http.route('/alfolk_medication_chart_record/alfolk_medication_chart_record/objects/<model("alfolk_medication_chart_record.alfolk_medication_chart_record"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alfolk_medication_chart_record.object', {
#             'object': obj
#         })
