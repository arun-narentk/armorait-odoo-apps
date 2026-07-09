# -*- coding: utf-8 -*-
"""Field extraction from document text by type."""

from __future__ import annotations

import logging
import re
from datetime import datetime

from odoo import fields, models

_logger = logging.getLogger(__name__)

GSTIN_RE = re.compile(r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b')
DOC_NO_RE = re.compile(
    r'(?:invoice|challan|po|order|document)\s*(?:no|number|#)?[:\s]*([A-Z0-9\-/]+)',
    re.IGNORECASE,
)
AMOUNT_TOTAL_RE = re.compile(
    r'(?:grand\s*total|total\s*amount|amount\s*payable)[:\s]*(?:rs\.?|inr)?\s*([\d,]+\.?\d*)',
    re.IGNORECASE,
)
DATE_RE = re.compile(
    r'(?:date|dated)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
    re.IGNORECASE,
)
LINE_RE = re.compile(
    r'^(.+?)\s+(\d+(?:\.\d+)?)\s+(?:x|@)?\s*([\d,]+\.?\d*)\s*([\d,]+\.?\d*)$',
    re.MULTILINE,
)


class RnDocumentIdpExtractionService(models.AbstractModel):
    _name = 'rn.document.idp.extraction.service'
    _description = 'IDP Extraction Service'

    def extract(self, text: str, document_type: str):
        text = text or ''
        base = self._extract_common(text)
        if document_type == 'purchase_order':
            base['document_number'] = self._find_po_number(text) or base.get('document_number')
        return base

    def _extract_common(self, text):
        gstin_match = GSTIN_RE.search(text.upper())
        doc_match = DOC_NO_RE.search(text)
        date_match = DATE_RE.search(text)
        total_match = AMOUNT_TOTAL_RE.search(text)
        lines = self._parse_lines(text)
        amount_total = self._parse_amount(total_match.group(1)) if total_match else 0.0
        amount_untaxed = sum(line.get('price_subtotal', 0) for line in lines) or amount_total
        amount_tax = max(amount_total - amount_untaxed, 0.0) if amount_total else 0.0
        return {
            'partner_name': self._guess_partner_name(text),
            'gstin': gstin_match.group(0) if gstin_match else False,
            'document_number': doc_match.group(1) if doc_match else False,
            'document_date': self._parse_date(date_match.group(1)) if date_match else False,
            'due_date': False,
            'amount_untaxed': amount_untaxed,
            'amount_tax': amount_tax,
            'amount_total': amount_total or amount_untaxed,
            'lines': lines,
        }

    def _find_po_number(self, text):
        match = re.search(r'(?:purchase\s*order|po)\s*(?:no|number)?[:\s]*([A-Z0-9\-/]+)', text, re.I)
        return match.group(1) if match else False

    def _guess_partner_name(self, text):
        for line in text.splitlines()[:8]:
            line = line.strip()
            if len(line) > 4 and not GSTIN_RE.search(line):
                if re.search(r'pvt|ltd|limited|industries|traders|enterprises|logistics', line, re.I):
                    return line
        first = next((line.strip() for line in text.splitlines() if line.strip()), '')
        return first[:128] if first else False

    def _parse_date(self, value):
        for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%d-%m-%y', '%d/%m/%y'):
            try:
                return fields.Date.to_date(datetime.strptime(value.strip(), fmt).date())
            except ValueError:
                continue
        return False

    def _parse_amount(self, value):
        try:
            return float(str(value).replace(',', ''))
        except (TypeError, ValueError):
            return 0.0

    def _parse_lines(self, text):
        lines = []
        for match in LINE_RE.finditer(text):
            desc, qty, price, subtotal = match.groups()
            lines.append({
                'description': desc.strip(),
                'quantity': float(qty),
                'price_unit': self._parse_amount(price),
                'price_subtotal': self._parse_amount(subtotal),
                'tax_percent': 0.0,
            })
        return lines[:50]
