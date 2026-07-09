# -*- coding: utf-8 -*-
"""CSV export helpers for rental assets and bookings."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnRentalExportService(models.AbstractModel):
    """Export rental master data."""

    _name = 'rn.rental.export.service'
    _description = 'Rental Export Service'

    def export_assets_csv(self, assets):
        lines = ['code,name,category,state,daily_price']
        for asset in assets:
            lines.append('%s,%s,%s,%s,%s' % (
                asset.code or '',
                (asset.name or '').replace(',', ' '),
                (asset.category_id.name or '').replace(',', ' '),
                asset.state or '',
                asset.daily_price or 0.0,
            ))
        return {
            'ok': True,
            'filename': 'rental_assets.csv',
            'datas': chr(10).join(lines),
        }
