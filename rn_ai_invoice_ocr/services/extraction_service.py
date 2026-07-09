# -*- coding: utf-8 -*-
"""Regex and heuristic field parsing from invoice text."""

import logging
import re
from datetime import datetime

from odoo import fields, models

_logger = logging.getLogger(__name__)

GSTIN_RE = re.compile(r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b')
INVOICE_NO_RE = re.compile(
    r'(?:invoice\s*(?:no|number|#)?[:\s]*)([A-Z0-9\-/]+)',
    re.IGNORECASE,
)
AMOUNT_TOTAL_RE = re.compile(
    r'(?:grand\s*total|total\s*amount|amount\s*payable)[:\s]*(?:rs\.?|inr|₹)?\s*([\d,]+\.?\d*)',
    re.IGNORECASE,
)
DATE_RE = re.compile(
    r'(?:invoice\s*date|date)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
    re.IGNORECASE,
)
LINE_RE = re.compile(
    r'^(.+?)\s+(\d+(?:\.\d+)?)\s+(?:x|@)?\s*([\d,]+\.?\d*)\s*([\d,]+\.?\d*)$',
    re.MULTILINE,
)


class RnAiInvoiceExtractionService(models.AbstractModel):
    """Parse structured invoice fields from raw OCR text."""

    _name = 'rn.ai.invoice.extraction.service'
    _description = 'Invoice Extraction Service'

    def parse_invoice_text(self, text):
        text = text or ''
        gstin_match = GSTIN_RE.search(text.upper())
        inv_match = INVOICE_NO_RE.search(text)
        date_match = DATE_RE.search(text)
        total_match = AMOUNT_TOTAL_RE.search(text)

        partner_name = self._guess_vendor_name(text)
        invoice_date = self._parse_date(date_match.group(1)) if date_match else False
        amount_total = self._parse_amount(total_match.group(1)) if total_match else 0.0
        lines = self._parse_lines(text)

        amount_untaxed = sum(l.get('price_subtotal', 0) for l in lines) or amount_total
        amount_tax = max(amount_total - amount_untaxed, 0.0) if amount_total else 0.0

        return {
            'partner_name': partner_name,
            'gstin': gstin_match.group(0) if gstin_match else False,
            'invoice_number': inv_match.group(1) if inv_match else False,
            'invoice_date': invoice_date,
            'due_date': False,
            'amount_untaxed': amount_untaxed,
            'amount_tax': amount_tax,
            'amount_total': amount_total or amount_untaxed,
            'lines': lines,
        }

    def _guess_vendor_name(self, text):
        for line in text.splitlines()[:8]:
            line = line.strip()
            if len(line) > 4 and not GSTIN_RE.search(line) and 'invoice' not in line.lower():
                if re.search(r'pvt|ltd|limited|industries|traders|enterprises', line, re.I):
                    return line
        first = next((l.strip() for l in text.splitlines() if l.strip()), '')
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
            return float(value.replace(',', ''))
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
