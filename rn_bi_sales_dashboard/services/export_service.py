# -*- coding: utf-8 -*-
"""Export stubs for PDF/Excel/CSV dashboard dumps."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnBiExportService(models.AbstractModel):
    """Generate export files for dashboard data."""

    _name = 'rn.bi.export.service'
    _description = 'BI Export Service'

    def export_csv(self, payload):
        """Return CSV string of KPI cards."""
        cards = (payload or {}).get('cards') or {}
        lines = ['kpi,value']
        for key, value in cards.items():
            lines.append('%s,%s' % (key, value))
        return {
            'ok': True,
            'filename': 'bi_sales_dashboard.csv',
            'datas': '\n'.join(lines),
        }

    def export_excel(self, payload):
        """Excel export pending Phase 8."""
        _logger.info('Excel export placeholder')
        return {'ok': False, 'error': 'Excel export pending (later phase).'}

    def export_pdf(self, payload):
        """PDF export pending Phase 8."""
        _logger.info('PDF export placeholder')
        return {'ok': False, 'error': 'PDF export pending (later phase).'}
