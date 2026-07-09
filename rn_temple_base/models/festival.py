# -*- coding: utf-8 -*-
"""Festival calendar."""

from datetime import timedelta

from odoo import api, fields, models


class RnTempleFestival(models.Model):
    """Festival, utsavam, or special religious event."""

    _name = 'rn.temple.festival'
    _description = 'Temple Festival'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(required=True, tracking=True)
    temple_id = fields.Many2one(
        'rn.temple.temple',
        required=True,
        ondelete='cascade',
        index=True,
    )
    branch_id = fields.Many2one('rn.temple.branch', string='Branch', index=True)
    festival_type = fields.Selection(
        selection=[
            ('annual', 'Annual Festival'),
            ('monthly', 'Monthly Observance'),
            ('special', 'Special Event'),
            ('kumbhabishekam', 'Kumbabishekam'),
            ('brahmotsavam', 'Brahmotsavam'),
            ('navaratri', 'Navaratri'),
            ('other', 'Other'),
        ],
        default='annual',
        required=True,
    )
    date_start = fields.Date(required=True, tracking=True)
    date_end = fields.Date()
    state = fields.Selection(
        selection=[
            ('draft', 'Planned'),
            ('confirmed', 'Confirmed'),
            ('ongoing', 'Ongoing'),
            ('done', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    budget_estimate = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    description = fields.Html()
    company_id = fields.Many2one(
        related='temple_id.company_id',
        store=True,
        index=True,
    )

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start and not self.date_end:
            self.date_end = self.date_start

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_start(self):
        self.write({'state': 'ongoing'})

    def action_complete(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.model
    def _cron_upcoming_festival_reminder(self):
        """Placeholder cron for festival reminders (extended in companion modules)."""
        today = fields.Date.context_today(self)
        upcoming = self.search([
            ('date_start', '=', today + timedelta(days=7)),
            ('state', 'in', ('draft', 'confirmed')),
        ], limit=50)
        for fest in upcoming:
            fest.message_post(
                body='Festival starts in 7 days. Review budget, volunteers, and seva schedule.',
                message_type='notification',
            )
