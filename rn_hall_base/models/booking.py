# -*- coding: utf-8 -*-
"""Hall booking management."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError

FUNCTION_TYPES = [
    ('muhurtham', 'Muhurtham / Wedding'),
    ('reception', 'Reception'),
    ('engagement', 'Engagement'),
    ('birthday', 'Birthday'),
    ('corporate', 'Corporate Event'),
    ('conference', 'Conference'),
    ('other', 'Other'),
]

BOOKING_STATES = [
    ('draft', 'Draft'),
    ('tentative', 'Tentative'),
    ('waitlist', 'Waitlist'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
    ('completed', 'Completed'),
]

BLOCKING_STATES = ('tentative', 'waitlist', 'confirmed')


class RnHallBooking(models.Model):
    """Event booking for a hall with conflict detection."""

    _name = 'rn.hall.booking'
    _description = 'Hall Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(required=True, tracking=True, default='New')
    reference = fields.Char(copy=False, index=True, default='New', tracking=True)
    venue_id = fields.Many2one(
        'rn.hall.venue',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
    )
    hall_id = fields.Many2one(
        'rn.hall.hall',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
        domain="[('venue_id', '=', venue_id)]",
    )
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True, index=True)
    groom_name = fields.Char(tracking=True)
    bride_name = fields.Char(tracking=True)
    function_type = fields.Selection(
        selection=FUNCTION_TYPES,
        default='muhurtham',
        required=True,
        tracking=True,
    )
    date_start = fields.Datetime(required=True, tracking=True)
    date_end = fields.Datetime(required=True, tracking=True)
    muhurtham_time = fields.Float(string='Muhurtham Time', help='Optional ritual start time')
    guest_count = fields.Integer(default=200)
    state = fields.Selection(
        selection=BOOKING_STATES,
        default='draft',
        tracking=True,
        index=True,
    )
    advance_amount = fields.Monetary(currency_field='currency_id')
    total_amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    special_request = fields.Text()
    referral_source = fields.Char()
    conflict_warning = fields.Char(compute='_compute_conflict_warning', store=False)
    company_id = fields.Many2one(
        related='venue_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Html()

    @api.depends('hall_id', 'date_start', 'date_end', 'state')
    def _compute_conflict_warning(self):
        service = self.env['rn.hall.booking.service']
        for booking in self:
            if not booking.hall_id or not booking.date_start or not booking.date_end:
                booking.conflict_warning = False
                continue
            conflicts = service.find_conflicts(
                booking.hall_id.id,
                booking.date_start,
                booking.date_end,
                exclude_id=booking.id,
            )
            booking.conflict_warning = (
                f'{len(conflicts)} overlapping booking(s) on this hall.'
                if conflicts else False
            )

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for booking in self:
            if booking.date_start and booking.date_end and booking.date_end <= booking.date_start:
                raise ValidationError('Booking end must be after start.')

    @api.constrains('hall_id', 'date_start', 'date_end', 'state')
    def _check_no_confirmed_conflict(self):
        service = self.env['rn.hall.booking.service']
        for booking in self:
            if booking.state not in BLOCKING_STATES:
                continue
            conflicts = service.find_conflicts(
                booking.hall_id.id,
                booking.date_start,
                booking.date_end,
                exclude_id=booking.id,
                states=BLOCKING_STATES,
            )
            if conflicts:
                raise ValidationError(
                    'This hall already has a booking in the selected time slot. '
                    'Use waitlist or choose another hall.'
                )

    @api.onchange('venue_id')
    def _onchange_venue_id(self):
        if self.hall_id and self.hall_id.venue_id != self.venue_id:
            self.hall_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('rn.hall.booking') or 'New'
            if vals.get('name', 'New') == 'New' and vals.get('reference'):
                vals['name'] = vals['reference']
        return super().create(vals_list)

    def action_tentative(self):
        self.write({'state': 'tentative'})

    def action_waitlist(self):
        self.write({'state': 'waitlist'})

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_complete(self):
        self.write({'state': 'completed'})

    @api.model
    def _cron_upcoming_booking_reminder(self):
        """Notify staff about bookings starting in 3 days."""
        from datetime import timedelta
        target_start = fields.Datetime.now() + timedelta(days=3)
        target_end = target_start + timedelta(days=1)
        upcoming = self.search([
            ('date_start', '>=', target_start),
            ('date_start', '<', target_end),
            ('state', 'in', BLOCKING_STATES),
        ], limit=50)
        for booking in upcoming:
            booking.message_post(
                body='Booking starts in 3 days. Review catering, decoration, and room allocation.',
                message_type='notification',
            )
