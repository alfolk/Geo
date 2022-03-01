from datetime import datetime, date
from itertools import groupby
from operator import itemgetter

from dateutil.relativedelta import relativedelta
from datetime import timedelta

from odoo import api, fields, models, _


class FolkBedWizard(models.TransientModel):
    _name = 'alfolk.bed.report'
    # bed_num = fields.Many2one('folk.rooms.accommodations', string="Bed")
    from_date = fields.Date(string="Date From", default=datetime.today())
    # from_date = fields.Date(string="From Date", default=lambda self: date.today())
    to_date = fields.Date(string="Date To", default=datetime.today())
    reserved = fields.Boolean(string="Reserved", default=True)
    line_ids = fields.One2many('alfolk.bed.report.line', 'wizard_id')

    def print_pdf_bed_report(self):
        line_ids = []
        for wizard in self:
            if wizard.reserved:
                bed_reserved_search = self.env['folk.rooms.accommodations'].search(
                    [('bed_reserve_from', '>=', wizard.from_date),
                     ('bed_reserve_to', '<=', wizard.to_date)])

                if bed_reserved_search:
                    for ex in bed_reserved_search:
                        line_ids.append((0, 0, {
                            'customer_name': ex.customer_name.name,
                            'responsible_id': ex.responsible_id.name,
                            'bed_reserve_from': ex.bed_reserve_from,
                            'bed_reserve_to': ex.bed_reserve_to,
                            'room_id': ex.room_id.name,
                            'bed_id': ex.bed_id.bed_no,

                        }))
            # else:
            #     bed_search = self.env['folk.beds'].search([])
            #     for bed in bed_search:

        self.write({'line_ids': line_ids})
        context = {
            'lang': 'en_US',
            'active_ids': [self.id],
        }
        return {
            'context': context,
            # 'data': None,
            'type': 'ir.actions.report',
            'report_name': 'room_management.folk_bed_report',
            'report_type': 'qweb-html',
            'report_file': 'room_management.folk_bed_report',
            'name': 'folk_clean',
            'flags': {'action_buttons': True},
        }


class BedWizardLine(models.TransientModel):
    _name = 'alfolk.bed.report.line'

    wizard_id = fields.Many2one('alfolk.bed.report', ondelete='cascade')
    customer_name = fields.Char("Customer")
    bed_reserve_from = fields.Date("Reserve From", default=datetime.today())
    bed_reserve_to = fields.Date("Reserve To", default=datetime.today())
    room_id = fields.Char("Room")
    bed_id = fields.Char("Bed")
    responsible_id = fields.Char("Responsible")
