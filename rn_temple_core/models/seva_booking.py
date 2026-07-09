# -*- coding: utf-8 -*-

from odoo import api, fields, models
import uuid


class RnTempleSevaBooking(models.Model):
    _name = 'rn.temple.seva.booking'
    _description = 'Seva Booking'
    _inherit = ['mail.thread']
    _order = 'booking_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    devotee_id = fields.Many2one('rn.temple.devotee', required=True, index=True)
    seva_type_id = fields.Many2one('rn.temple.seva.type', required=True, index=True)
    booking_date = fields.Datetime(required=True, index=True)
    slot_label = fields.Char(string='Time Slot')
    amount = fields.Float()
    qr_token = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    festival_id = fields.Many2one('rn.temple.festival')
    note = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.temple.seva.booking') or 'SEVA'
            if not vals.get('qr_token'):
                vals['qr_token'] = uuid.uuid4().hex[:12].upper()
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})
