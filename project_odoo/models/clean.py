from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class CleanAlfolk(models.Model):
    _name = 'folk.clean'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Cleanliness"
    _rec_name = 'customer_id'

    customer_id = fields.Many2one('hr.employee', store=True, string="Customer Name",tracking=True)
    time_clean = fields.Date(string="Date", store=True,tracking=True,  default=datetime.today())
    notes = fields.Text(string="Notes", store=True,tracking=True)
    responsible_id = fields.Many2one('hr.employee', store=True, string="Responsible",tracking=True)
    places = fields.Many2many('folk.rooms', string="Places", store=True,tracking=True)
