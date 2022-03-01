from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class BedsAlfolk(models.Model):
    _name = 'folk.beds'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "bed_no"

    # customer_id = fields.Many2one('hr.employee', store=True, string="Customer Name",tracking=True)
    bed_no = fields.Char(string="Bed No", store=True, tracking=True)
    # no_of_beds_in_room = fields.Integer(compute="calc_number_of_beds", store=True)
    # responsible_id = fields.Many2one('hr.employee', store=True, string="Responsible", tracking=True)
    notes = fields.Text(string="Notes", store=True, tracking=True)
    rooms_ids = fields.Many2one('folk.rooms', string="Room", store=True, tracking=True)
    bed_status = fields.Selection([("available", "Available"),
                                   ("occupied", "Occupied")],
                                  "Status",
                                  default="available", compute="check_bed_availability", tracking=True)

    # bed_capacity = fields.Integer(string="Beds  Capacity", store=True, tracking=True)

    def check_bed_availability(self):
        for record in self:
            check_date = date.today()
            available_bed = self.env['folk.rooms.accommodations'].search(
                [('bed_id', '=', record.id)])
            if available_bed:
                for a in available_bed:
                    if a.bed_reserve_to < check_date:
                        record.bed_status = 'available'
                    else:
                        record.bed_status = 'occupied'
            else:

                record.bed_status = 'available'
