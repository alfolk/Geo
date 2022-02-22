from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class RoomsAccommodationsAlfolk(models.Model):
    _name = 'folk.rooms.accommodations'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "room_id"

    room_id = fields.Many2one("folk.rooms", "Room", tracking=True, domain=[('status', '=', 'available')])
    # floor_id = fields.Many2one("folk.floor", "Floor", store=True, string="Floor")
    # customer_id = fields.Many2one('res.partner', store=True, string="Customer Name", tracking=True)
    customer_name = fields.Many2one('res.partner', store=True, string="Customer Name", tracking=True)

    # check_in = fields.Date("Check In Date", store=True, tracking=True)
    # check_out = fields.Date("Check Out Date", store=True, tracking=True)

    bed_reserve_from = fields.Date("Reservation From", store=True, tracking=True, default=datetime.today())
    bed_reserve_to = fields.Date("Reservation To", store=True, tracking=True, default=datetime.today())
    responsible_id = fields.Many2one('hr.employee', store=True, tracking=True)
    status = fields.Selection([("available", "Available"),
                               ("occupied", "Occupied")],
                              "Status",
                              default="available", compute="check_room_availability", tracking=True,
                              )
    # bed_ids = fields.Many2many('folk.beds', string="beds", store=True, tracking=True)
    bed_id = fields.Many2one('folk.beds', string="Bed", store=True, tracking=True)

    # @api.depends('bed_reserve_from', 'bed_reserve_to', 'bed_id')
    def check_room_availability(self):
        for bed in self:
            if bed.bed_reserve_from and bed.bed_reserve_to and bed.bed_id:
                self.status = "occupied"
            elif bed.bed_reserve_from and not bed.bed_reserve_to and bed.bed_id:
                self.status = "occupied"
            elif not bed.bed_reserve_from and not bed.bed_reserve_to and bed.bed_id:
                self.status = "available"

    @api.constrains('bed_reserve_from', 'bed_reserve_to')
    def check_in_out(self):
        for rec in self:
            if rec.bed_reserve_from and rec.bed_reserve_to:
                if rec.bed_reserve_to < rec.bed_reserve_from:
                    raise ValidationError(_("Date Of Reservation From Must Be Before Date Of Reservation TO"))

    @api.constrains('bed_reserve_from', 'bed_reserve_to')
    def check_bed_availability(self):
        # search_bed = self.env['folk.rooms.accommodations'].search()
        for rec in self:
            if rec.bed_reserve_from and rec.bed_reserve_to and rec.bed_id:
                raise ValidationError(_("This Bed Is Occupied"))

    # @api.constrains('status')
    # def check_availability_bed(self):
    #     for rec in self:
    #         if rec.status == 'occupied':
    #             raise ValidationError(_("Sorry! You Can Not Reserve This bed"))

    # record.description = "Test for partner %s" % record.partner_id.name
