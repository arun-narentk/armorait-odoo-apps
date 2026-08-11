# -*- coding: utf-8 -*-
"""Quotation expiry countdown on sale.order."""

from datetime import datetime, time

from odoo import _, api, fields, models

PARAM_WARNING_HOURS = 'rn_quotation_expiry_countdown.warning_hours'
DEFAULT_WARNING_HOURS = 24
QUOTATION_STATES = ('draft', 'sent')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quotation_expiry_countdown = fields.Char(
        string='Countdown',
        compute='_compute_quotation_expiry_countdown',
        help='Time remaining before this quotation expires.',
    )
    quotation_expiry_urgency = fields.Selection(
        selection=[
            ('none', 'None'),
            ('ok', 'OK'),
            ('warning', 'Warning'),
            ('expired', 'Expired'),
        ],
        string='Expiry Urgency',
        compute='_compute_quotation_expiry_countdown',
    )

    @api.depends('validity_date', 'state')
    @api.depends_context('tz', 'uid')
    def _compute_quotation_expiry_countdown(self):
        warning_hours = self._rn_get_expiry_warning_hours()
        for order in self:
            text, urgency = order._rn_build_quotation_expiry_countdown(warning_hours)
            order.quotation_expiry_countdown = text
            order.quotation_expiry_urgency = urgency

    @api.model
    def _rn_get_expiry_warning_hours(self):
        raw = self.env['ir.config_parameter'].sudo().get_param(
            PARAM_WARNING_HOURS, str(DEFAULT_WARNING_HOURS),
        )
        try:
            hours = int(raw)
        except (TypeError, ValueError):
            hours = DEFAULT_WARNING_HOURS
        return hours if hours > 0 else DEFAULT_WARNING_HOURS

    def _rn_build_quotation_expiry_countdown(self, warning_hours=None):
        """Return (display_text, urgency) for the current quotation.

        urgency: none | ok | warning | expired
        """
        self.ensure_one()
        if self.state not in QUOTATION_STATES or not self.validity_date:
            return '', 'none'

        if warning_hours is None:
            warning_hours = self._rn_get_expiry_warning_hours()

        today = fields.Date.context_today(self)
        validity = self.validity_date

        if validity < today:
            days = (today - validity).days
            if days <= 1:
                return _('Expired 1 day ago'), 'expired'
            return _('Expired %s days ago') % days, 'expired'

        if validity == today:
            return _('Expires today'), 'warning'

        # Future validity: treat end-of-day in the user timezone as expiry instant.
        now_utc = fields.Datetime.now()
        now_local = fields.Datetime.context_timestamp(self, now_utc)
        expiry_local = datetime.combine(
            validity, time(23, 59, 59),
        ).replace(tzinfo=now_local.tzinfo)
        remaining = expiry_local - now_local
        remaining_seconds = remaining.total_seconds()
        if remaining_seconds <= 0:
            return _('Expires today'), 'warning'

        calendar_days = (validity - today).days
        remaining_hours = remaining_seconds / 3600.0

        if remaining_hours < 1:
            minutes = max(1, int(remaining_seconds // 60))
            if minutes == 1:
                text = _('Expires in 1 minute')
            else:
                text = _('Expires in %s minutes') % minutes
            return text, 'warning'

        if remaining_hours < float(warning_hours):
            hours = max(1, int(remaining_hours))
            if hours == 1:
                text = _('Expires in 1 hour')
            else:
                text = _('Expires in %s hours') % hours
            return text, 'warning'

        if calendar_days <= 1:
            return _('Expires in 1 day'), 'ok'

        return _('Expires in %s days') % calendar_days, 'ok'
