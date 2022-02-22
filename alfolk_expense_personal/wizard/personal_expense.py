from datetime import datetime, date
from itertools import groupby
from operator import itemgetter

from dateutil.relativedelta import relativedelta
from datetime import timedelta

from odoo import api, fields, models, _


class personalExpense(models.TransientModel):
    _name = 'alfolk.personal.expense.report'

    amount_payment = fields.Float('Amount')
    end_amount = fields.Float('e')
    amount_cash = fields.Char('Amount')
    customer = fields.Many2one('res.partner', 'Customer', store=True, track_visibility='onchange', required=True, )
    treasury = fields.Many2one('account.journal', string='Treasury', required=True, store=True,
                               domain="[('type', 'in', ('cash','bank'))]")

    def computereceiveamount(self):
        value = 0
        if self.customer:
            receive = self.env['alfolk.expense.personal'].search(
                [('date', '>=', self.date_from),
                 ('date', '<=', self.date_to), ('customer', '=', self.customer.id), ('treasury', '=', self.treasury.id),
                 ('payment_type', '=', 'receive_money'), ('state', '=', 'confirm')
                 ])
            for line in receive:
                value += (line.amount)

        return round(value, 0)

    def computeresidualamount(self):
        value_receive = 0
        value_expense = 0
        residual = 0
        if self.customer:
            receive = self.env['alfolk.expense.personal'].search(
                [('date', '>=', self.date_from),
                 ('date', '<=', self.date_to), ('customer', '=', self.customer.id), ('treasury', '=', self.treasury.id),
                 ('payment_type', '=', 'receive_money'), ('state', '=', 'confirm')
                 ])
            for line in receive:
                value_receive += (line.amount)
            expense = self.env['alfolk.expense.personal'].search(
                [('date', '>=', self.date_from),
                 ('date', '<=', self.date_to), ('customer', '=', self.customer.id),
                 ('treasury', '=', self.treasury.id), ('payment_type', '=', 'expense_money'),
                 ('state', '=', 'confirm')
                 ])
            for line in expense:
                value_expense += (line.amount)

        return round(value_receive - value_expense, 0)

    @api.model
    def _get_from_date(self):
        company = self.env.user.company_id
        current_date = datetime.today()
        from_date = company.compute_fiscalyear_dates(current_date)['date_from']
        return from_date

    def _get_date(self):
        today = date.today()
        first_day = today.replace(day=1)

        return first_day

    date_from = fields.Date("Start Date", default=_get_date)
    date_to = fields.Date("End Date", default=datetime.today(), )
    line_ids = fields.One2many('alfolk.personal.expense.report.line', 'wizard_id', required=True, ondelete='cascade')

    def print_pdf_personal_expense_report(self):
        line_ids = []
        for wizard in self:

            if wizard.customer:

                expense = self.env['alfolk.expense.personal'].search(
                    [('date', '>=', wizard.date_from),
                     ('date', '<=', wizard.date_to), ('customer', '=', wizard.customer.id),
                     ('treasury', '=', self.treasury.id), ('payment_type', '=', 'expense_money'),
                     ('state', '=', 'confirm')
                     ])

                if expense:
                    for ex in expense:
                        line_ids.append((0, 0, {
                            'date': ex.date,
                            'description': ex.description,
                            'journal_id': ex.treasury.name,
                            'expense_amount': ex.amount,
                            'employee': ex.employee.name,
                            'code': ex.code,
                            'note': ex.note,

                        }))
        self.write({'line_ids': line_ids})
        context = {
            'lang': 'en_US',
            'active_ids': [self.id],
        }
        return {
            'context': context,
            'data': None,
            'type': 'ir.actions.report',
            'report_name': 'alfolk_expense_personal.alfolk_personal_expense_report',
            'report_type': 'qweb-html',
            'report_file': 'alfolk_expense_personal.alfolk.personal_expense_report',
            'name': 'personal_expense',
            'flags': {'action_buttons': True},
        }


class PersonalExpenseLine(models.TransientModel):
    _name = 'alfolk.personal.expense.report.line'

    wizard_id = fields.Many2one('alfolk.personal.expense.report', required=True, ondelete='cascade')
    date = fields.Char("Date")
    reference = fields.Char("Code")
    customer = fields.Char("Code")
    description = fields.Char("Description")
    note = fields.Char("Description")
    code = fields.Char("Code")
    journal_id = fields.Char(string="Safe")
    expense_amount = fields.Float("Amount Paid")
    partner_id = fields.Char("Partner")
    employee = fields.Char("Employee")
    _order = 'date asc'
