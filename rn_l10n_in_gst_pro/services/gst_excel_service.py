# -*- coding: utf-8 -*-
"""Excel export for GST reports."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnGstExcelService(models.AbstractModel):
    """Produce multi-sheet Excel workbooks for GST returns."""

    _name = 'rn.gst.excel.service'
    _description = 'GST Excel Service'

    def generate_excel(self, gst_return):
        """Return Excel binary payload (Phase 8)."""
        gst_return.ensure_one()
        _logger.info('Excel export placeholder for %s', gst_return.name)
        return {'ok': False, 'datas': False, 'filename': False, 'error': 'Excel pending (Phase 8).'}
