# -*- coding: utf-8 -*-
"""Core appointment / booking record."""

from odoo import api, fields, models


class RnBookingAppointment(models.Model):
    """Customer appointment managed by the booking engine."""

    _name = 'rn.booking.appointment'
    _description = 'Booking Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'start_datetime desc, id desc'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ('no_show', 'No Show'),
        ],
        default='draft',
        tracking=True,
        index=True,
    )
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    service_id = fields.Many2one('rn.booking.service', required=True, tracking=True)
    staff_id = fields.Many2one('rn.booking.staff', tracking=True)
    location_id = fields.Many2one('rn.booking.location', tracking=True)
    resource_id = fields.Many2one('rn.booking.resource')
    industry_id = fields.Many2one(related='service_id.industry_id', store=True)
    start_datetime = fields.Datetime(required=True, index=True, tracking=True)
    stop_datetime = fields.Datetime(required=True, index=True, tracking=True)
    duration_minutes = fields.Integer(compute='_compute_duration', store=True)
    booking_source = fields.Selection(
        selection=[
            ('backend', 'Backend'),
            ('portal', 'Customer Portal'),
            ('public', 'Public Website'),
            ('api', 'API'),
            ('staff', 'Staff Portal'),
        ],
        default='backend',
        index=True,
    )
    is_guest = fields.Boolean()
    payment_state = fields.Selection(
        selection=[
            ('not_paid', 'Not Paid'),
            ('partial', 'Partial'),
            ('paid', 'Paid'),
            ('refunded', 'Refunded'),
        ],
        default='not_paid',
        tracking=True,
    )
    amount_total = fields.Monetary(currency_field='currency_id')
    amount_paid = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)
    calendar_event_id = fields.Many2one('calendar.event', copy=False)
    meeting_url = fields.Char(string='Meeting URL')
    meeting_provider = fields.Selection(
        selection=[
            ('none', 'None'),
            ('google_meet', 'Google Meet'),
            ('zoom', 'Zoom'),
            ('teams', 'Microsoft Teams'),
        ],
        default='none',
    )
    rating = fields.Selection(
        selection=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
    )
    review = fields.Text()
    cancel_reason = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Html()

    @api.depends('start_datetime', 'stop_datetime')
    def _compute_duration(self):
        for appt in self:
            if appt.start_datetime and appt.stop_datetime:
                delta = appt.stop_datetime - appt.start_datetime
                appt.duration_minutes = int(delta.total_seconds() // 60)
            else:
                appt.duration_minutes = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rn.booking.appointment') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        self.env['rn.booking.booking.service'].confirm_appointments(self)
        return True

    def action_done(self):
        self.write({'state': 'done'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        self.env['rn.booking.notification.service'].notify_cancellation(self)
        return True

    def action_no_show(self):
        self.write({'state': 'no_show'})
        return True

    def action_create_invoice(self):
        return self.env['rn.booking.payment.service'].create_invoice(self)
