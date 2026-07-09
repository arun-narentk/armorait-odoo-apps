# -*- coding: utf-8 -*-
"""Heuristic document type classification."""

from __future__ import annotations

import logging

from odoo import models

_logger = logging.getLogger(__name__)

CLASSIFICATION_RULES = [
    ('purchase_order', ['purchase order', 'po number', 'po no', 'purchase order no']),
    ('delivery_challan', ['delivery challan', 'challan no', 'dc no']),
    ('goods_receipt', ['goods receipt', 'grn', 'material receipt']),
    ('transport_bill', ['lorry receipt', 'lr no', 'transport bill', 'freight invoice']),
    ('expense_receipt', ['expense receipt', 'reimbursement', 'petty cash']),
    ('credit_note', ['credit note', 'credit memo']),
    ('debit_note', ['debit note', 'debit memo']),
    ('contract', ['agreement', 'contract', 'nda', 'memorandum of understanding']),
    ('vendor_invoice', ['tax invoice', 'vendor invoice', 'supplier invoice', 'bill to']),
    ('customer_invoice', ['invoice to', 'sales invoice', 'customer invoice']),
]


class RnDocumentIdpClassificationService(models.AbstractModel):
    _name = 'rn.document.idp.classification.service'
    _description = 'IDP Classification Service'

    def classify(self, text: str):
        text_lower = (text or '').lower()
        best_type = 'other'
        best_score = 0.0
        for doc_type, keywords in CLASSIFICATION_RULES:
            hits = sum(1 for keyword in keywords if keyword in text_lower)
            if hits:
                score = min(95.0, 55.0 + hits * 15.0)
                if score > best_score:
                    best_score = score
                    best_type = doc_type
        if best_type == 'other' and 'invoice' in text_lower:
            best_type = 'vendor_invoice'
            best_score = 70.0
        return best_type, round(best_score, 1)
