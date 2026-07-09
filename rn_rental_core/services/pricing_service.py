# -*- coding: utf-8 -*-
"""Rental pricing engine."""

import logging
import math
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnRentalPricingService(models.AbstractModel):
    """Quote rental prices from asset fields and pricing rules."""

    _name = 'rn.rental.pricing.service'
    _description = 'Rental Pricing Service'

    def _duration_units(self, plan, date_start, date_end):
        if not date_start or not date_end:
            return 1.0
        start = fields.Datetime.to_datetime(date_start)
        end = fields.Datetime.to_datetime(date_end)
        if end <= start:
            return 1.0
        seconds = (end - start).total_seconds()
        hours = seconds / 3600.0
        days = seconds / 86400.0
        if plan == 'hourly':
            return max(1.0, math.ceil(hours))
        if plan == 'half_day':
            return max(1.0, math.ceil(hours / 12.0))
        if plan == 'weekly':
            return max(1.0, math.ceil(days / 7.0))
        if plan == 'monthly':
            return max(1.0, math.ceil(days / 30.0))
        if plan == 'yearly':
            return max(1.0, math.ceil(days / 365.0))
        # daily / weekend default
        return max(1.0, math.ceil(days))

    def _asset_base_price(self, asset, plan):
        mapping = {
            'hourly': asset.hourly_price,
            'half_day': asset.half_day_price or (asset.daily_price or 0.0) * 0.6,
            'daily': asset.daily_price,
            'weekend': asset.daily_price,
            'weekly': asset.weekly_price or (asset.daily_price or 0.0) * 6,
            'monthly': asset.monthly_price or (asset.daily_price or 0.0) * 25,
            'yearly': asset.yearly_price or (asset.monthly_price or 0.0) * 10,
        }
        return mapping.get(plan) or asset.daily_price or 0.0

    def quote_asset(self, asset, plan='daily', date_start=None, date_end=None):
        """Return unit price and duration for one asset."""
        asset.ensure_one()
        duration = self._duration_units(plan, date_start, date_end)
        domain = [
            ('active', '=', True),
            ('plan', '=', plan),
            '|', ('asset_id', '=', asset.id), ('category_id', '=', asset.category_id.id),
        ]
        if date_start:
            day = fields.Date.to_date(fields.Datetime.to_datetime(date_start))
            domain += [
                '|', ('date_start', '=', False), ('date_start', '<=', day),
                '|', ('date_end', '=', False), ('date_end', '>=', day),
            ]
        rule = self.env['rn.rental.pricing'].search(domain, order='sequence, id', limit=1)
        unit_price = rule.amount if rule else self._asset_base_price(asset, plan)
        return {
            'unit_price': unit_price or 0.0,
            'duration': duration,
            'subtotal': (unit_price or 0.0) * duration,
            'rule_id': rule.id if rule else False,
        }

    def recompute_booking(self, bookings):
        for booking in bookings:
            for line in booking.line_ids:
                quote = self.quote_asset(
                    line.asset_id,
                    plan=booking.plan,
                    date_start=booking.date_start,
                    date_end=booking.date_end,
                )
                line.write({
                    'unit_price': quote['unit_price'],
                    'duration': quote['duration'],
                })
            booking.deposit_amount = sum(booking.line_ids.mapped('asset_id.deposit_amount'))
        _logger.info('Recomputed prices for %s bookings', len(bookings))
        return True
