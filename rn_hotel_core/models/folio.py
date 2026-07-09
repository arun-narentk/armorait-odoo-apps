# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnHotelFolio(models.Model):
    _name = 'rn.hotel.folio'
    _description = 'Guest Folio'
    _inherit = ['mail.thread']
    _order = 'open_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    guest_id = fields.Many2one('rn.hotel.guest', required=True, index=True)
    reservation_id = fields.Many2one('rn.hotel.reservation', index=True)
    room_id = fields.Many2one('rn.hotel.room')
    state = fields.Selection(
        [('open', 'Open'), ('closed', 'Closed'), ('invoiced', 'Invoiced')],
        default='open',
        tracking=True,
    )
    open_date = fields.Datetime(default=fields.Datetime.now)
    close_date = fields.Datetime()
    line_ids = fields.One2many('rn.hotel.folio.line', 'folio_id')
    amount_total = fields.Float(compute='_compute_total', store=True)
    invoice_id = fields.Many2one('account.move', copy=False)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('line_ids.amount')
    def _compute_total(self):
        for folio in self:
            folio.amount_total = sum(folio.line_ids.mapped('amount'))

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.hotel.folio') or 'FOL'
        return super().create(vals_list)
