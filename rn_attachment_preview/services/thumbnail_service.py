# -*- coding: utf-8 -*-
"""Generate stored preview thumbnails for attachments."""

from __future__ import annotations

import base64
import io
import logging

from odoo import api, models

from ..constants import IMAGE_MIMETYPES, THUMBNAIL_MAX_BYTES, THUMBNAIL_SIZE

_logger = logging.getLogger(__name__)


class RnAttachmentThumbnailService(models.AbstractModel):
    _name = 'rn.attachment.thumbnail.service'
    _description = 'Attachment Thumbnail Service'

    @api.model
    def generate_thumbnail(self, attachment) -> bool:
        attachment.ensure_one()
        raw = attachment.raw or b''
        if not raw or (attachment.file_size or 0) > THUMBNAIL_MAX_BYTES:
            attachment.sudo().write({'rn_thumbnail_state': 'skipped'})
            return False
        mimetype = (attachment.mimetype or '').lower()
        try:
            if mimetype in IMAGE_MIMETYPES:
                thumb = self._thumbnail_image(raw)
            elif mimetype == 'application/pdf':
                thumb = self._thumbnail_pdf_placeholder(attachment.name)
            elif mimetype in {'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}:
                thumb = self._thumbnail_label_placeholder(attachment.name, 'DOCX', '#2563eb')
            elif mimetype in {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}:
                thumb = self._thumbnail_label_placeholder(attachment.name, 'XLSX', '#16a34a')
            elif mimetype in {'application/vnd.openxmlformats-officedocument.presentationml.presentation'}:
                thumb = self._thumbnail_label_placeholder(attachment.name, 'PPTX', '#ea580c')
            else:
                attachment.sudo().write({'rn_thumbnail_state': 'skipped'})
                return False
            if thumb:
                attachment.sudo().write({
                    'rn_preview_thumbnail': base64.b64encode(thumb),
                    'rn_thumbnail_state': 'done',
                })
                return True
        except Exception as exc:  # noqa: BLE001
            _logger.warning('Thumbnail failed for attachment %s: %s', attachment.id, exc)
        attachment.sudo().write({'rn_thumbnail_state': 'failed'})
        return False

    @api.model
    def _thumbnail_image(self, raw: bytes) -> bytes | None:
        from PIL import Image

        image = Image.open(io.BytesIO(raw))
        image.thumbnail(THUMBNAIL_SIZE)
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
        out = io.BytesIO()
        image.save(out, format='PNG')
        return out.getvalue()

    @api.model
    def _thumbnail_pdf_placeholder(self, name: str | None) -> bytes:
        return self._thumbnail_label_placeholder(name, 'PDF', '#dc2626')

    @api.model
    def _thumbnail_label_placeholder(self, name: str | None, label: str, color: str) -> bytes:
        from PIL import Image, ImageDraw, ImageFont

        image = Image.new('RGB', THUMBNAIL_SIZE, color)
        draw = ImageDraw.Draw(image)
        draw.rectangle([(8, 8), (THUMBNAIL_SIZE[0] - 8, THUMBNAIL_SIZE[1] - 8)], outline='#ffffff', width=2)
        draw.text((18, 48), label, fill='#ffffff')
        short_name = (name or '')[:14]
        if short_name:
            draw.text((12, 100), short_name, fill='#f8fafc')
        out = io.BytesIO()
        image.save(out, format='PNG')
        return out.getvalue()

    @api.model
    def cron_generate_batch(self, limit: int | None = None) -> int:
        limit = limit or int(
            self.env['ir.config_parameter'].sudo().get_param(
                'rn_attachment_preview.thumbnail_batch',
                '40',
            )
        )
        attachments = self.env['ir.attachment'].sudo().search([
            ('rn_thumbnail_state', '=', 'pending'),
        ], limit=limit, order='id')
        done = 0
        for attachment in attachments:
            if self.generate_thumbnail(attachment):
                done += 1
        return done
