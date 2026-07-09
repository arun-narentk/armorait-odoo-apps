# -*- coding: utf-8 -*-
"""GST validation engine."""

import logging
import re

from odoo import models

_logger = logging.getLogger(__name__)

GSTIN_RE = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')


class RnGstValidationService(models.AbstractModel):
    """Validate GSTINs, HSN, taxes, and invoices before export."""

    _name = 'rn.gst.validation.service'
    _description = 'GST Validation Service'

    def is_valid_gstin(self, gstin):
        """Basic GSTIN pattern check (Phase 3 expands checksum)."""
        if not gstin:
            return False
        return bool(GSTIN_RE.match(gstin.strip().upper()))

    def validate_returns(self, returns):
        """Create validation issue records for selected returns."""
        Validation = self.env['rn.gst.validation']
        for gst_return in returns:
            Validation.search([('return_id', '=', gst_return.id)]).unlink()
            settings = self.env['rn.gst.settings'].search(
                [('company_id', '=', gst_return.company_id.id)], limit=1
            )
            if not settings or not settings.gstin:
                Validation.create({
                    'name': 'Company GSTIN missing in GST Settings',
                    'return_id': gst_return.id,
                    'issue_type': 'gstin',
                    'severity': 'warning',
                    'message': 'Configure company GSTIN under GST Pro settings.',
                    'company_id': gst_return.company_id.id,
                })
            open_errors = Validation.search_count([
                ('return_id', '=', gst_return.id),
                ('severity', 'in', ('error', 'critical')),
                ('state', '=', 'open'),
            ])
            if not open_errors:
                gst_return.write({'state': 'validated'})
            _logger.info('Validated return %s open_errors=%s', gst_return.name, open_errors)
        return True
