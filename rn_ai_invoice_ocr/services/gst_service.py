# -*- coding: utf-8 -*-
"""India GST field parsing."""

import logging
import re

from odoo import models

_logger = logging.getLogger(__name__)

CGST_RE = re.compile(r'CGST[:\s@]*([\d,]+\.?\d*)', re.I)
SGST_RE = re.compile(r'SGST[:\s@]*([\d,]+\.?\d*)', re.I)
IGST_RE = re.compile(r'IGST[:\s@]*([\d,]+\.?\d*)', re.I)
HSN_RE = re.compile(r'HSN[:\s/]*(?:SAC)?[:\s]*(\d{4,8})', re.I)


class RnAiInvoiceGstService(models.AbstractModel):
    """Parse CGST, SGST, IGST, HSN from Indian tax invoices."""

    _name = 'rn.ai.invoice.gst.service'
    _description = 'Invoice GST Service'

    def parse_gst(self, text, fields_data=None):
        text = text or ''
        return {
            'gstin': (fields_data or {}).get('gstin'),
            'cgst_amount': self._amount(CGST_RE.search(text)),
            'sgst_amount': self._amount(SGST_RE.search(text)),
            'igst_amount': self._amount(IGST_RE.search(text)),
            'hsn_code': self._hsn(HSN_RE.search(text)),
        }

    def _amount(self, match):
        if not match:
            return 0.0
        try:
            return float(match.group(1).replace(',', ''))
        except (TypeError, ValueError):
            return 0.0

    def _hsn(self, match):
        return match.group(1) if match else False
