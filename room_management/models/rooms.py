from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class RoomsAlfolk(models.Model):
    _name = 'folk.rooms'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Text(string="Name", store=True, tracking=True)
    room_no = fields.Integer(string="Room", store=True, tracking=True)
    beds_no = fields.Integer(string="No Of Beds", store=True, tracking=True)
    notes = fields.Html(string="Notes", store=True, tracking=True)
    responsible_id = fields.Many2one('hr.employee', string="Responsible", tracking=True)
    floor_id = fields.Many2one('folk.floor', string="Floor", store=True, tracking=True)
    bed_id = fields.One2many('folk.beds', 'rooms_ids', string="Bed", store=True, tracking=True)
    # bed_capacity_num = fields.Integer(related="bed_id.bed_capacity", store=True, tracking=True)
    room_capacity_num = fields.Integer(related="floor_id.room_capacity", store=True, tracking=True)
    room_type = fields.Selection([("lab", "Lab"),
                                  ("dorm room", "Dorm Room"),
                                  ("other", "Other")], string="Type Of Room", store=True, tracking=True)
    # type_id = fields.Many2one('folk.type', string="Type", store=True, tracking=True)
    image = fields.Binary(string="Image", store=True, tracking=True)
    status = fields.Selection([("available", "Available"),
                               ("occupied", "Occupied")],
                              "Status", tracking=True, default="available",
                              compute='check_room_availability'
                              )

    # room_line_id = fields.One2many('folk.rooms.accommodations', 'room_id', 'Room', store=True, tracking=True)

    @api.constrains("floor_id")
    def check_floor_id(self):
        room_counts = len(self.floor_id.room_ids)
        floor_capacity = self.floor_id.room_capacity
        if room_counts > floor_capacity:
            raise UserError("Floor is Full !")

    def check_room_availability(self):
        for r in self:
          if r.bed_id:
             for x in r.bed_id:
                if x.bed_status == "available":
                    r.status = 'available'
                else:
                   r.status = 'occupied'
          else:
                   r.status = 'available'
