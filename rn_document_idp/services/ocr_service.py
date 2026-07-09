# -*- coding: utf-8 -*-
"""PDF and image text extraction."""

import base64
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnDocumentIdpOcrService(models.AbstractModel):
    _name = 'rn.document.idp.ocr.service'
    _description = 'IDP OCR Service'

    def extract_text(self, attachment):
        data = base64.b64decode(attachment.datas or b'')
        mimetype = (attachment.mimetype or '').lower()
        if 'pdf' in mimetype:
            return self._extract_pdf_text(data)
        if mimetype.startswith('image/'):
            return self._extract_image_placeholder(attachment.name)
        return data.decode('utf-8', errors='ignore')[:50000]

    def _extract_pdf_text(self, data):
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(data))
            return '\n'.join(page.extract_text() or '' for page in reader.pages)
        except ImportError:
            try:
                from PyPDF2 import PdfReader
                import io
                reader = PdfReader(io.BytesIO(data))
                return '\n'.join(page.extract_text() or '' for page in reader.pages)
            except Exception as exc:
                _logger.warning('PDF extract failed: %s', exc)
                return ''
        except Exception as exc:
            _logger.warning('PDF extract failed: %s', exc)
            return ''

    def _extract_image_placeholder(self, filename):
        return (
            f'Image file {filename or "upload"}. '
            'Enable LLM OCR companion or Tesseract for image extraction.'
        )
