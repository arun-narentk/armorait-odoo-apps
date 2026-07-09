# -*- coding: utf-8 -*-
"""Duplicate vendor bill detection."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnAiInvoiceDuplicateService(models.AbstractModel):
    """Detect existing vendor bills with same ref and partner."""

    _name = 'rn.ai.invoice.duplicate.service'
    _description = 'Invoice Duplicate Service'

    def find_duplicate(self, partner_id, invoice_number, company_id=None):
        if not invoice_number:
            return self.env['account.move']
        company_id = company_id or self.env.company.id
        domain = [
            ('move_type', 'in', ('in_invoice', 'in_refund')),
            ('company_id', '=', company_id),
            ('ref', '=ilike', invoice_number),
            ('state', '!=', 'cancel'),
        ]
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        return self.env['account.move'].search(domain, limit=1)
