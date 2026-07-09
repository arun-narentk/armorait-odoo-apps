# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnTempleDevotee(models.Model):
    _name = 'rn.temple.devotee'
    _description = 'Temple Devotee'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    mobile = fields.Char(index=True)
    email = fields.Char()
    address = fields.Text()
    family_head_id = fields.Many2one('rn.temple.devotee', string='Family Head')
    family_member_ids = fields.One2many('rn.temple.devotee', 'family_head_id')
    membership_type = fields.Selection(
        [
            ('general', 'General'),
            ('patron', 'Patron'),
            ('life', 'Life Member'),
            ('trustee', 'Trustee'),
        ],
        default='general',
    )
    preferred_seva_ids = fields.Many2many('rn.temple.seva.type', string='Preferred Sevas')
    donation_ids = fields.One2many('rn.temple.donation', 'devotee_id')
    donation_total = fields.Float(compute='_compute_donation_total', store=True)
    seva_booking_ids = fields.One2many('rn.temple.seva.booking', 'devotee_id')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('donation_ids.amount', 'donation_ids.state')
    def _compute_donation_total(self):
        for devotee in self:
            devotee.donation_total = sum(devotee.donation_ids.filtered(
                lambda d: d.state == 'confirmed'
            ).mapped('amount'))
