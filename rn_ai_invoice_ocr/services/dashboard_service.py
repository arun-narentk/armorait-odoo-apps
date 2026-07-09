# -*- coding: utf-8 -*-
"""Invoice OCR dashboard."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnAiInvoiceOcrDashboardService(models.AbstractModel):
    """Dashboard KPIs for AI Invoice OCR."""

    _name = 'rn.ai.invoice.ocr.dashboard.service'
    _description = 'Invoice OCR Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        domain = [('company_id', '=', company_id)]
        Scan = self.env['rn.ai.invoice.scan']
        settings = self.env['rn.ai.invoice.ocr.settings'].search(
            [('company_id', '=', company_id)], limit=1,
        )
        return {
            'cards': {
                'total_scans': Scan.search_count(domain),
                'pending_review': Scan.search_count(domain + [('state', '=', 'review')]),
                'billed': Scan.search_count(domain + [('state', '=', 'billed')]),
                'duplicates': Scan.search_count(domain + [('is_duplicate', '=', True)]),
                'avg_confidence': self._avg_confidence(company_id),
                'credits': settings.credit_balance if settings else 0,
            },
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def _avg_confidence(self, company_id):
        scans = self.env['rn.ai.invoice.scan'].search([
            ('company_id', '=', company_id),
            ('overall_confidence', '>', 0),
        ], limit=100)
        if not scans:
            return 0.0
        return round(sum(scans.mapped('overall_confidence')) / len(scans), 1)
