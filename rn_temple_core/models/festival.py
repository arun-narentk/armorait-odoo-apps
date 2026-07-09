# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnTempleFestival(models.Model):
    _name = 'rn.temple.festival'
    _description = 'Temple Festival'
    _inherit = ['mail.thread']
    _order = 'date_start desc'

    name = fields.Char(required=True, tracking=True)
    date_start = fields.Date(required=True, index=True)
    date_end = fields.Date()
    description = fields.Html()
    budget = fields.Float()
    sponsor_note = fields.Text(string='Sponsors')
    volunteer_ids = fields.Many2many('rn.temple.volunteer', string='Volunteers')
    donation_ids = fields.One2many('rn.temple.donation', 'festival_id')
    donation_total = fields.Float(compute='_compute_totals', store=True)
    state = fields.Selection(
        [('planned', 'Planned'), ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        default='planned',
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('donation_ids.amount', 'donation_ids.state')
    def _compute_totals(self):
        for fest in self:
            fest.donation_total = sum(
                fest.donation_ids.filtered(lambda d: d.state == 'confirmed').mapped('amount')
            )
