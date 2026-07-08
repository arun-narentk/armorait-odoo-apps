# -*- coding: utf-8 -*-
"""Staff or location weekly working hours."""

from odoo import api, fields, models


class RnBookingWorkingHour(models.Model):
    """One weekday availability window."""

    _name = 'rn.booking.working.hour'
    _description = 'Booking Working Hour'
    _order = 'dayofweek, hour_from'

    name = fields.Char(compute='_compute_name', store=True)
    staff_id = fields.Many2one('rn.booking.staff', ondelete='cascade', index=True)
    location_id = fields.Many2one('rn.booking.location', ondelete='cascade', index=True)
    dayofweek = fields.Selection(
        selection=[
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday'),
        ],
        required=True,
        default='0',
    )
    hour_from = fields.Float(string='From', required=True, default=9.0)
    hour_to = fields.Float(string='To', required=True, default=17.0)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('dayofweek', 'hour_from', 'hour_to')
    def _compute_name(self):
        labels = dict(self._fields['dayofweek'].selection)
        for rec in self:
            rec.name = '%s %s-%s' % (
                labels.get(rec.dayofweek, rec.dayofweek),
                rec.hour_from,
                rec.hour_to,
            )
