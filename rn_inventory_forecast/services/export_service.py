# -*- coding: utf-8 -*-
"""Export stubs for forecast and analysis reports."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnInvExportService(models.AbstractModel):
    """CSV/PDF/Excel export helpers."""

    _name = 'rn.inv.export.service'
    _description = 'Inventory Forecast Export Service'

    def export_forecast_csv(self, run):
        """Export forecast lines as CSV string."""
        lines = ['product,forecast_qty,safety_stock,reorder_point,purchase_qty']
        for line in run.line_ids:
            lines.append('%s,%s,%s,%s,%s' % (
                line.product_id.display_name.replace(',', ' '),
                line.forecast_qty,
                line.safety_stock,
                line.reorder_point,
                line.recommended_purchase_qty,
            ))
        return {
            'ok': True,
            'filename': 'inventory_forecast_%s.csv' % run.id,
            'datas': '\n'.join(lines),
        }

    def export_excel(self, payload):
        _logger.info('Excel export placeholder')
        return {'ok': False, 'error': 'Excel export pending (later phase).'}

    def export_pdf(self, payload):
        _logger.info('PDF export placeholder')
        return {'ok': False, 'error': 'PDF export pending (later phase).'}
