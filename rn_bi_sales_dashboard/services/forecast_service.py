# -*- coding: utf-8 -*-
"""Simple forecast stubs based on current revenue and targets."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnBiForecastService(models.AbstractModel):
    """Predict remaining period revenue with a lightweight model."""

    _name = 'rn.bi.forecast.service'
    _description = 'BI Forecast Service'

    def forecast_revenue(self, current_revenue, target_info=None):
        """Return naive forecast: assume linear pace for remaining target."""
        target_info = target_info or {}
        target = target_info.get('target_amount') or 0.0
        projected = max(current_revenue, current_revenue * 1.05)
        return {
            'current_revenue': current_revenue,
            'projected_revenue': projected,
            'target_amount': target,
            'expected_orders': 0,
            'achievement_prediction': (
                min(100.0, (projected / target) * 100.0) if target else 0.0
            ),
        }
