# -*- coding: utf-8 -*-
"""Extract searchable OCR text from attachments."""

from __future__ import annotations

import io
import logging

from odoo import api, models

from ..constants import IMAGE_MIMETYPES, OCR_MAX_BYTES, OFFICE_MIMETYPES, TEXT_MIMETYPES

_logger = logging.getLogger(__name__)


class RnAttachmentOcrService(models.AbstractModel):
    _name = 'rn.attachment.ocr.service'
    _description = 'Attachment OCR Service'

    @api.model
    def extract_text(self, attachment) -> str:
        attachment.ensure_one()
        raw = attachment.raw or b''
        if not raw or (attachment.file_size or 0) > OCR_MAX_BYTES:
            return ''
        mimetype = (attachment.mimetype or '').lower()
        if mimetype in TEXT_MIMETYPES:
            return raw.decode('utf-8', errors='replace')[:50000]
        if mimetype == 'application/pdf':
            return self._extract_pdf_text(raw)
        if mimetype in IMAGE_MIMETYPES:
            return self._extract_image_placeholder(attachment.name)
        if mimetype in OFFICE_MIMETYPES:
            return self.env['rn.attachment.office.service'].extract_plain_text(raw, mimetype)
        return ''

    @api.model
    def _extract_pdf_text(self, raw: bytes) -> str:
        try:
            from pdfminer.high_level import extract_text
            return (extract_text(io.BytesIO(raw)) or '')[:50000]
        except Exception as exc:  # noqa: BLE001
            _logger.warning('PDF OCR failed: %s', exc)
            return ''

    @api.model
    def _extract_image_placeholder(self, name: str | None) -> str:
        return f'Image attachment {name or ""}'.strip()

    @api.model
    def process_attachment(self, attachment) -> bool:
        attachment.ensure_one()
        text = self.extract_text(attachment)
        if text:
            attachment.sudo().write({
                'rn_ocr_text': text,
                'rn_ocr_state': 'done',
            })
            return True
        attachment.sudo().write({'rn_ocr_state': 'skipped'})
        return False

    @api.model
    def cron_extract_batch(self, limit: int | None = None) -> int:
        limit = limit or int(
            self.env['ir.config_parameter'].sudo().get_param(
                'rn_attachment_preview.ocr_batch',
                '40',
            )
        )
        attachments = self.env['ir.attachment'].sudo().search([
            ('rn_ocr_state', '=', 'pending'),
        ], limit=limit, order='id')
        done = 0
        for attachment in attachments:
            if self.process_attachment(attachment):
                done += 1
        return done

    @api.model
    def search_attachments(self, query: str, limit: int = 20) -> list[dict]:
        query = (query or '').strip()
        if len(query) < 2:
            return []
        attachments = self.env['ir.attachment'].search([
            ('rn_ocr_text', 'ilike', query),
        ], limit=limit, order='id desc')
        attachments.check_access('read')
        service = self.env['rn.attachment.preview.service']
        return [service.attachment_to_dict(att) for att in attachments]
