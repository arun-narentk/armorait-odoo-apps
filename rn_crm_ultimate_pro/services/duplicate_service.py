# -*- coding: utf-8 -*-
"""Duplicate detection for CRM leads."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnCrmDuplicateService(models.AbstractModel):
    """Detect duplicate leads by email, phone, company, and more."""

    _name = 'rn.crm.duplicate.service'
    _description = 'CRM Duplicate Service'

    def scan_leads(self, leads=None, sensitivity='balanced'):
        """Create a batch with suggested duplicate pairs."""
        Lead = self.env['crm.lead']
        leads = leads or Lead.search([], limit=200)
        batch = self.env['rn.crm.duplicate.batch'].create({
            'name': 'Duplicate Scan',
            'sensitivity': sensitivity,
        })
        # Phase 4: full fuzzy / phonetic matching.
        seen = {}
        lines = []
        for lead in leads:
            key = (lead.email_from or '').strip().lower()
            if not key:
                continue
            if key in seen:
                lines.append({
                    'batch_id': batch.id,
                    'lead_id': seen[key],
                    'duplicate_lead_id': lead.id,
                    'match_on': 'email',
                    'confidence': 95.0,
                })
            else:
                seen[key] = lead.id
        if lines:
            self.env['rn.crm.duplicate.line'].create(lines)
        batch.write({'state': 'done', 'match_count': len(lines)})
        _logger.info('Duplicate scan batch %s matches=%s', batch.id, len(lines))
        return batch
