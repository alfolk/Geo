# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

_STATES = [
    ('draft', 'Draft'),
    ('confirm', 'Confirm'), ('cancel', 'Cancel')
]


class alfolk_expense_personal(models.Model):
    _name = 'alfolk.expense.personal'

    _description = 'Expense Personal'
    _inherit = ['mail.thread']
    _rec_name = 'code'

    def unlink(self):
        for l in self:
            if not l.state != 'draft':
                raise UserError(_('Cannot delete a item in post state'))
            return super(alfolk_expense_personal, self).unlink()

    # Fields Defi ne
    state = fields.Selection(selection=_STATES, string='Status', index=True, track_visibility='onchange', required=True,
                             copy=False, default='draft', store=True)
    customer = fields.Many2one('res.partner', string='Customer', store=True, index=True, tracking=True)
    amount = fields.Float(string='Amount', store=True, index=True, tracking=True, required=True)
    date = fields.Date(string='Date', store=True, tracking=True, required=True, default=fields.Date.today())

    @api.model
    def _getjournalId(self):
        current_user_id = self.env.user

        if current_user_id.has_group('base.user_admin'):
            return [('type', 'in', ('cash', 'bank')),
                    ]
        if not current_user_id.has_group('base.user_admin'):
            return [('id', '=', self.env.user.journal_ids.ids), ('type', 'in', ('cash', 'bank')),
                    ]

    treasury = fields.Many2one('account.journal', string='Treasury', store=True,
                               domain=_getjournalId)
    treasury_to = fields.Many2one('account.journal', string='To Treasury', store=True,
                                  domain="[('type', 'in', ('cash','bank'))]")
    account_to = fields.Many2one('account.account', string='To Account', store=True,
                                 )
    account_id = fields.Many2one('account.account', string='Account', store=True,
                                 )
    account_from = fields.Many2one('account.account', string='From Account', store=True,
                                   )
    code = fields.Char('Reference', size=32, copy=False,
                       store=True,
                       default=lambda self: (" "))
    description = fields.Char(string='Expense For', store=True, index=True, tracking=True)
    note = fields.Char(string='Note', store=True, index=True, tracking=True)
    employee = fields.Many2one('hr.employee', string='Employee', store=True, index=True, tracking=True, )

    payment_type = fields.Selection([
        ('receive_money', 'Receive Money'),
        ('expense_money', 'Expense Money'), ('transfer_money', 'Transfer Money')],
        string='Type', default='receive_money', store=True, track_visibility='onchange')

    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('name', '=', self.code)],
        }

    @api.constrains('amount')
    def check_amount(self):
        if self.amount <= 0:
            raise ValidationError(_('Amount must be Positive'))

    def confirm(self):
        for expense in self:
            res = self.env['account.move'].search([('name', '=', expense.code)])
            ff = self.env['account.move.line'].search([('move_id', '=', res.id)])
            if res:
                if self.payment_type == 'receive_money':
                    if self.customer:
                        debit = credit = self.amount
                        move = {
                            'date': expense.date,
                            'ref': expense.code,
                            'line_ids': [(0, 0, {
                                'name': expense.code,
                                'debit': debit,
                                'account_id': expense.treasury.default_account_id.id,

                            }), (0, 0, {
                                'name': expense.code,
                                'credit': credit,
                                'account_id': expense.customer.property_account_receivable_id.id,
                                'partner_id': expense.customer.id,

                            })]
                        }
                    else:
                        debit = credit = self.amount
                        move = {
                            'date': expense.date,
                            'ref': expense.code,
                            'line_ids': [(0, 0, {
                                'name': expense.code,
                                'debit': debit,
                                'account_id': expense.treasury.default_account_id.id,

                            }), (0, 0, {
                                'name': expense.code,
                                'credit': credit,
                                'account_id': expense.account_id.id,
                                'partner_id': expense.customer.id,

                            })]
                        }
                    res.line_ids -= res.line_ids
                    move_id = res.write(move)
                    res.action_post()
                    self.write({'state': 'confirm'})

                elif self.payment_type == 'expense_money':
                    debit = credit = self.amount
                    if self.customer:
                        move = {
                            'journal_id': expense.treasury.id,
                            'date': expense.date,
                            'ref': expense.code,
                            'line_ids': [(0, 0, {
                                'name': expense.description,
                                'debit': debit,
                                'account_id': expense.customer.property_account_receivable_id.id,
                                'partner_id': expense.customer.id,
                            }), (0, 0, {
                                'name': expense.description,
                                'credit': credit,
                                'account_id': expense.treasury.default_account_id.id,

                            })]
                        }
                    else:
                        move = {
                            'journal_id': expense.treasury.id,
                            'date': expense.date,
                            'ref': expense.code,
                            'line_ids': [(0, 0, {
                                'name': expense.description,
                                'debit': debit,
                                'account_id': expense.account_id.id,
                                'partner_id': expense.customer.id,
                            }), (0, 0, {
                                'name': expense.description,
                                'credit': credit,
                                'account_id': expense.treasury.default_account_id.id,

                            })]
                        }
                elif self.payment_type == 'transfer_money':
                    debit = credit = self.amount
                    move = {
                        # 'journal_id': expense.treasury.id,
                        'date': expense.date,
                        'ref': expense.code,
                        'line_ids': [(0, 0, {
                            'name': expense.description,
                            'debit': debit,
                            'account_id': expense.account_to.id,
                            'partner_id': expense.customer.id,
                        }), (0, 0, {
                            'name': expense.description,
                            'credit': credit,
                            'account_id': expense.account_from.id,

                        })]
                    }
            else:
                if self.payment_type == 'receive_money':
                    if self.customer:
                        debit = credit = self.amount
                        move = {
                            'journal_id': expense.treasury.id,
                            'date': expense.date,
                            'ref': expense.code,
                            'line_ids': [(0, 0, {
                                'name': expense.code,
                                'debit': debit,
                                'account_id': expense.treasury.default_account_id.id,

                            }), (0, 0, {
                                'name': expense.code,
                                'credit': credit,
                                'account_id': expense.customer.property_account_receivable_id.id,
                                'partner_id': expense.customer.id,

                            })]
                        }
                    else:
                        debit = credit = self.amount
                        move = {
                            'journal_id': expense.treasury.id,
                            'date': expense.date,
                            'ref': expense.code,
                            'line_ids': [(0, 0, {
                                'name': expense.code,
                                'debit': debit,
                                'account_id': expense.treasury.default_account_id.id,

                            }), (0, 0, {
                                'name': expense.code,
                                'credit': credit,
                                'account_id': expense.account_id.id,
                                'partner_id': expense.customer.id,

                            })]
                        }
                elif self.payment_type == 'expense_money':
                    debit = credit = self.amount
                    if self.customer:
                        move = {
                            'journal_id': expense.treasury.id,
                            'date': expense.date,
                            'ref': expense.code,
                            'line_ids': [(0, 0, {
                                'name': expense.description,
                                'debit': debit,
                                'account_id': expense.customer.property_account_receivable_id.id,
                                'partner_id': expense.customer.id,
                            }), (0, 0, {
                                'name': expense.description,
                                'credit': credit,
                                'account_id': expense.treasury.default_account_id.id,

                            })]
                        }
                    else:
                        move = {
                            'journal_id': expense.treasury.id,
                            'date': expense.date,
                            'ref': expense.code,
                            'line_ids': [(0, 0, {
                                'name': expense.description,
                                'debit': debit,
                                'account_id': expense.account_id.id,
                                'partner_id': expense.customer.id,
                            }), (0, 0, {
                                'name': expense.description,
                                'credit': credit,
                                'account_id': expense.treasury.default_account_id.id,

                            })]
                        }
                elif self.payment_type == 'transfer_money':
                    debit = credit = self.amount
                    move = {
                        # 'journal_id': expense.treasury.id,
                        'date': expense.date,
                        'ref': expense.code,
                        'line_ids': [(0, 0, {
                            'name': expense.description,
                            'debit': debit,
                            'account_id': expense.account_to.id,
                            'partner_id': expense.customer.id,
                        }), (0, 0, {
                            'name': expense.description,
                            'credit': credit,
                            'account_id': expense.account_from.id,

                        })]
                    }

                move_id = self.env['account.move'].create(move)

                move_id.post()
                self.write({'state': 'confirm',
                            'code': move_id.name
                            })

    def draft(self):
        for record in self:
            res = self.env['account.move'].search([('name', '=', record.code)])
            if res:
                res.button_draft()
                self.write({'state': 'draft'})

    def cancel(self):
        for record in self:
            res = self.env['account.move'].search([('name', '=', record.code)])
            if res:
                res.button_cancel()
                self.write({'state': 'cancel'})
