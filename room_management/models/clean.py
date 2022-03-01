from datetime import datetime, date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class CleanAlfolk(models.Model):
    _name = 'folk.clean'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Cleanliness"
    _rec_name = 'customer_id'

    customer_id = fields.Many2one('hr.employee', store=True, string="Customer clean Name", tracking=True)
    time_clean = fields.Date(string="Date", store=True,tracking=True,default=lambda self: date.today())
    notes = fields.Text(string="Notes", store=True,tracking=True)
    responsible_id = fields.Many2one('hr.employee', store=True, string="Responsible",tracking=True)
    places = fields.Many2many('folk.rooms', string="Places", store=True,tracking=True)
