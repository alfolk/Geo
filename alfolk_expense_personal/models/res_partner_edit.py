from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
class account_journal(models.Model):
    _inherit = 'account.journal'
    send_receive = fields.Selection([('send_money', 'Send Money'),('receive_money', 'Receive Money')],
                                     string='Send/Receive Type')


class journal_default(models.Model):
    _inherit = ['res.users']

    journal_ids = fields.Many2many(
        'account.journal', 'account_journal_users_rel',
        'user_id', 'account_journal_id', string='Restrict Journal')


