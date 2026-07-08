# -*- coding: utf-8 -*-
"""PDF export for GST reports."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnGstPdfService(models.AbstractModel):
    """Render professional PDF summaries for returns."""

    _name = 'rn.gst.pdf.service'
    _description = 'GST PDF Service'

    def generate_pdf(self, gst_return):
        """Return PDF binary payload (Phase 8)."""
        gst_return.ensure_one()
        _logger.info('PDF export placeholder for %s', gst_return.name)
        return {'ok': False, 'datas': False, 'filename': False, 'error': 'PDF pending (Phase 8).'}
