from datetime import datetime, date
from itertools import groupby
from operator import itemgetter

from dateutil.relativedelta import relativedelta
from datetime import timedelta

from odoo import api, fields, models, _


class FolkCleanWizard(models.TransientModel):
    _name = 'alfolk.clean.report'
    floor_id = fields.Many2one('folk.floor', string="Floor")
    from_date = fields.Date(string="Date From", default=datetime.today())
    # from_date = fields.Date(string="From Date", default=lambda self: date.today())
    to_date = fields.Date(string="Date To", default=datetime.today())
    line_ids = fields.One2many('alfolk.clean.report.line', 'wizard_id')

    def print_pdf_clean_report(self):
        line_ids = []
        for wizard in self:
            all_workers = self.env['folk.clean'].search([('time_clean', '>=', wizard.from_date),
                                                         ('time_clean', '<=', wizard.to_date)])
            # all_workers = self.env['folk.clean'].search([])

            if all_workers:
                for ex in all_workers:
                    line_ids.append((0, 0, {
                        'customer_id': ex.customer_id.name,
                        'time_clean': ex.time_clean,
                        'responsible_id': ex.responsible_id.name,
                        # 'places': [(6, 0, ex.places.ids)],
                        'places_name': ",".join(ex.places.mapped('name')),
                        'notes': ex.notes,

                    }))
        self.write({'line_ids': line_ids})
        context = {
            'lang': 'en_US',
            'active_ids': [self.id],
        }
        return {
            'context': context,
            # 'data': None,
            'type': 'ir.actions.report',
            'report_name': 'project_odoo.alfolk_clean_report_new',
            'report_type': 'qweb-html',
            'report_file': 'project_odoo.alfolk_clean_report_new',
            'name': 'folk_clean',
            'flags': {'action_buttons': True},
        }


class PersonalExpenseLine(models.TransientModel):
    _name = 'alfolk.clean.report.line'

    wizard_id = fields.Many2one('alfolk.clean.report', ondelete='cascade')
    customer_id = fields.Char("Customer")
    time_clean = fields.Date("Time Clean", default=datetime.today())
    responsible_id = fields.Char("Responsible")
    # places = fields.Many2many("folk.clean")
    places_name = fields.Char("folk.clean")
    notes = fields.Char("Notes")
