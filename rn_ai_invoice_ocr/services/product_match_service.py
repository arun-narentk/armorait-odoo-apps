# -*- coding: utf-8 -*-
"""Fuzzy product matching."""

import logging
import re

from odoo import models

_logger = logging.getLogger(__name__)


class RnAiInvoiceProductMatchService(models.AbstractModel):
    """Match OCR line description to product.product."""

    _name = 'rn.ai.invoice.product.match.service'
    _description = 'Invoice Product Match Service'

    def match_product(self, description, company_id=None):
        company_id = company_id or self.env.company.id
        if not description:
            return self.env['product.product'], 0.0

        Mapping = self.env['rn.ai.invoice.product.mapping']
        mapping = Mapping.search([
            ('ocr_text', '=ilike', description.strip()),
            ('company_id', '=', company_id),
        ], limit=1)
        if mapping:
            return mapping.product_id, 96.0

        Product = self.env['product.product']
        norm_desc = re.sub(r'[^a-z0-9]', '', description.lower())
        best = Product
        best_score = 0.0
        for product in Product.search([('purchase_ok', '=', True)], limit=300):
            norm_name = re.sub(r'[^a-z0-9]', '', (product.name or '').lower())
            if not norm_name:
                continue
            if norm_desc == norm_name:
                score = 95.0
            elif norm_desc in norm_name or norm_name in norm_desc:
                score = 80.0
            else:
                continue
            if score > best_score:
                best_score = score
                best = product

        if best_score >= 75:
            self._record_mapping(description, best, company_id)
        return best, best_score

    def _record_mapping(self, ocr_text, product, company_id):
        Mapping = self.env['rn.ai.invoice.product.mapping']
        existing = Mapping.search([
            ('ocr_text', '=ilike', ocr_text.strip()),
            ('company_id', '=', company_id),
        ], limit=1)
        if existing:
            existing.hit_count += 1
        else:
            Mapping.create({
                'ocr_text': ocr_text.strip(),
                'product_id': product.id,
                'company_id': company_id,
            })
