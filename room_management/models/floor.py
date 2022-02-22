from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class FloorAlfolk(models.Model):
    _name = 'folk.floor'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _description = "Floor"
    _rec_name = "name"

    name = fields.Char(string="Floor", store=True, tracking=True)
    # description = fields.Text("Description")
    room_ids = fields.One2many('folk.rooms', 'floor_id', string="Room", store=True,tracking=True)
    room_capacity = fields.Integer(string="Capacity", store=True,tracking=True)

    _sql_constraints = [

        ('name_unique', 'UNIQUE(name)', _(' Floor Already Exist!')),

    ]

    @api.constrains("room_capacity")
    def _check_capacity(self):
        for room in self:
            if room.room_capacity <= 0:
                raise ValidationError(_("Room capacity must be more than 0"))
