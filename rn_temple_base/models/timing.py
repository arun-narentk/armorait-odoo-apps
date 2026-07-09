# -*- coding: utf-8 -*-
"""Daily darshan and service timings."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RnTempleTiming(models.Model):
    """Daily opening, darshan, and service schedule."""

    _name = 'rn.temple.timing'
    _description = 'Temple Daily Timing'
    _order = 'day_of_week, time_open'

    name = fields.Char(compute='_compute_name', store=True)
    temple_id = fields.Many2one(
        'rn.temple.temple',
        required=True,
        ondelete='cascade',
        index=True,
    )
    branch_id = fields.Many2one('rn.temple.branch', string='Branch', index=True)
    day_of_week = fields.Selection(
        selection=[
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday'),
            ('all', 'Every Day'),
        ],
        default='all',
        required=True,
    )
    session_type = fields.Selection(
        selection=[
            ('darshan', 'Darshan'),
            ('morning', 'Morning Puja'),
            ('afternoon', 'Afternoon Service'),
            ('evening', 'Evening Aarti'),
            ('special', 'Special Session'),
            ('closed', 'Closed'),
        ],
        default='darshan',
        required=True,
    )
    time_open = fields.Float(string='Opens At', help='Hours in 24h format, e.g. 6.5 = 06:30')
    time_close = fields.Float(string='Closes At')
    active = fields.Boolean(default=True)
    note = fields.Char()
    company_id = fields.Many2one(
        related='temple_id.company_id',
        store=True,
        index=True,
    )

    @api.depends('day_of_week', 'session_type', 'time_open')
    def _compute_name(self):
        day_labels = dict(self._fields['day_of_week'].selection)
        session_labels = dict(self._fields['session_type'].selection)
        for rec in self:
            day = day_labels.get(rec.day_of_week, '')
            session = session_labels.get(rec.session_type, '')
            rec.name = f'{day} {session}'.strip()

    @api.constrains('time_open', 'time_close', 'session_type')
    def _check_times(self):
        for rec in self:
            if rec.session_type == 'closed':
                continue
            if rec.time_open and rec.time_close and rec.time_close <= rec.time_open:
                raise ValidationError('Close time must be after open time.')
