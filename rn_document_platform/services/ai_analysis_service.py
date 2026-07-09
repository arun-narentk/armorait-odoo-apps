# -*- coding: utf-8 -*-
"""AI contract summary and risk heuristics."""

import logging
import re

from odoo import models

_logger = logging.getLogger(__name__)

RISK_PATTERNS = [
    (r'unlimited\s+liability', 'Unlimited liability clause detected'),
    (r'auto[\s-]?renew', 'Auto renewal clause detected'),
    (r'exclusive\s+supplier', 'Exclusive supplier clause detected'),
    (r'penalty|liquidated\s+damages', 'Penalty or damages clause detected'),
    (r'no\s+termination|without\s+termination', 'Limited termination rights detected'),
]


class RnDocAiAnalysisService(models.AbstractModel):
    _name = 'rn.doc.ai.analysis.service'
    _description = 'Document AI Analysis Service'

    def analyze_request(self, request):
        request.ensure_one()
        text = self._extract_text(request.attachment_id)
        flags = self._detect_risks(text)
        risk_level = 'high' if len(flags) >= 3 else ('medium' if flags else 'low')

        value = self._find_amount(text)
        duration = self._find_duration(text)
        renewal = self._find_renewal(text)

        summary_lines = [
            f'<p><strong>Contract value:</strong> {value or "Not detected"}</p>',
            f'<p><strong>Duration:</strong> {duration or "Not detected"}</p>',
            f'<p><strong>Risk level:</strong> {risk_level.title()}</p>',
        ]
        if flags:
            summary_lines.append('<p><strong>Risk flags:</strong></p><ul>')
            summary_lines.extend(f'<li>{f}</li>' for f in flags)
            summary_lines.append('</ul>')

        return self.env['rn.doc.ai.analysis'].create({
            'name': f'Analysis {request.reference}',
            'request_id': request.id,
            'summary_html': ''.join(summary_lines),
            'contract_value': value,
            'duration': duration,
            'renewal_date': renewal,
            'risk_level': risk_level,
            'risk_flags': '\n'.join(flags),
            'company_id': request.company_id.id,
        })

    def _extract_text(self, attachment):
        if not attachment or not attachment.datas:
            return ''
        try:
            import base64
            raw = base64.b64decode(attachment.datas)
            try:
                from pypdf import PdfReader
                import io
                reader = PdfReader(io.BytesIO(raw))
                return '\n'.join(page.extract_text() or '' for page in reader.pages)
            except ImportError:
                return raw.decode('utf-8', errors='ignore')[:50000]
        except Exception:
            return ''

    def _detect_risks(self, text):
        flags = []
        for pattern, label in RISK_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                flags.append(label)
        return flags

    def _find_amount(self, text):
        match = re.search(r'(?:INR|Rs\.?|USD)\s*([\d,]+(?:\.\d+)?)', text, re.I)
        return match.group(0) if match else False

    def _find_duration(self, text):
        match = re.search(r'(\d+)\s*(?:months?|years?)', text, re.I)
        return match.group(0) if match else False

    def _find_renewal(self, text):
        match = re.search(r'renew(?:al)?\s*(?:on|date)?[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', text, re.I)
        return False
