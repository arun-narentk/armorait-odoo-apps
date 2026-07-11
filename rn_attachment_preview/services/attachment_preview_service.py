# -*- coding: utf-8 -*-
"""Attachment preview helpers and RPC payloads."""

from __future__ import annotations

from odoo import _, api, models
from odoo.exceptions import AccessError, UserError

from ..constants import (
    AUDIO_MIMETYPES,
    HOVER_PREVIEW_MAX_BYTES,
    IMAGE_MIMETYPES,
    OFFICE_MIMETYPES,
    PREVIEWABLE_MIMETYPES,
    TEXT_MIMETYPES,
    VIDEO_MIMETYPES,
)


class RnAttachmentPreviewService(models.AbstractModel):
    _name = 'rn.attachment.preview.service'
    _description = 'Attachment Preview Service'

    @api.model
    def classify_mimetype(self, mimetype: str | None) -> str:
        mimetype = (mimetype or '').lower()
        if mimetype == 'application/pdf':
            return 'pdf'
        if mimetype in IMAGE_MIMETYPES:
            return 'image'
        if mimetype in VIDEO_MIMETYPES:
            return 'video'
        if mimetype in AUDIO_MIMETYPES:
            return 'audio'
        if mimetype in TEXT_MIMETYPES:
            return 'text'
        if mimetype in OFFICE_MIMETYPES:
            return 'office'
        return 'other'

    @api.model
    def is_previewable(self, attachment) -> bool:
        mimetype = (attachment.mimetype or '').lower()
        return mimetype in PREVIEWABLE_MIMETYPES or mimetype in OFFICE_MIMETYPES

    @api.model
    def attachment_to_dict(self, attachment) -> dict:
        attachment.ensure_one()
        attachment.check_access('read')
        mimetype = attachment.mimetype or ''
        preview_type = self.classify_mimetype(mimetype)
        file_size = attachment.file_size or 0
        ocr_text = attachment.rn_ocr_text or ''
        return {
            'id': attachment.id,
            'name': attachment.name,
            'mimetype': mimetype,
            'file_size': file_size,
            'file_size_label': self._format_size(file_size),
            'preview_type': preview_type,
            'is_previewable': self.is_previewable(attachment),
            'hover_preview': file_size <= HOVER_PREVIEW_MAX_BYTES and preview_type in ('image', 'pdf'),
            'image_url': f'/web/image/{attachment.id}' if preview_type == 'image' else False,
            'thumbnail_url': (
                f'/web/image/ir.attachment/{attachment.id}/rn_preview_thumbnail'
                if attachment.rn_has_thumbnail else False
            ),
            'content_url': f'/web/content/{attachment.id}',
            'download_url': f'/web/content/{attachment.id}?download=true',
            'create_uid_name': attachment.create_uid.name,
            'create_date': attachment.create_date.isoformat() if attachment.create_date else False,
            'thumbnail_state': attachment.rn_thumbnail_state,
            'ocr_state': attachment.rn_ocr_state,
            'ocr_snippet': ocr_text[:160] if ocr_text else False,
            'office_preview_ready': bool(attachment.rn_office_preview_html),
            'annotation_count': attachment.rn_annotation_count,
        }

    @api.model
    def _format_size(self, size: int) -> str:
        if size < 1024:
            return f'{size} B'
        if size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        return f'{size / (1024 * 1024):.1f} MB'

    @api.model
    def get_record_attachments(self, res_model: str, res_id: int) -> list[dict]:
        if res_model not in self.env:
            raise UserError(_('Unsupported model: %s') % res_model)
        record = self.env[res_model].browse(res_id)
        if not record.exists():
            raise UserError(_('Record not found.'))
        record.check_access('read')
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', res_model),
            ('res_id', '=', res_id),
        ], order='id desc')
        attachments.check_access('read')
        return [self.attachment_to_dict(att) for att in attachments]

    @api.model
    def get_preview_payload(self, attachment_id: int) -> dict:
        attachment = self.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            raise UserError(_('Attachment not found.'))
        return self.attachment_to_dict(attachment)

    @api.model
    def get_text_preview(self, attachment_id: int, max_chars: int = 4000) -> dict:
        attachment = self.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            raise UserError(_('Attachment not found.'))
        attachment.check_access('read')
        preview_type = self.classify_mimetype(attachment.mimetype)
        if preview_type != 'text':
            raise AccessError(_('Text preview is not available for this file type.'))
        raw = attachment.raw or b''
        text = raw.decode('utf-8', errors='replace')
        truncated = len(text) > max_chars
        if truncated:
            text = text[:max_chars]
        return {
            'attachment_id': attachment.id,
            'name': attachment.name,
            'mimetype': attachment.mimetype,
            'text': text,
            'truncated': truncated,
        }

    @api.model
    def get_office_preview(self, attachment_id: int) -> dict:
        attachment = self.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            raise UserError(_('Attachment not found.'))
        attachment.check_access('read')
        if self.classify_mimetype(attachment.mimetype) != 'office':
            raise AccessError(_('Office preview is not available for this file type.'))
        if not attachment.rn_office_preview_html:
            self.env['rn.attachment.office.service'].process_attachment(attachment)
        return {
            'attachment_id': attachment.id,
            'name': attachment.name,
            'mimetype': attachment.mimetype,
            'html': attachment.rn_office_preview_html or '',
        }

    @api.model
    def search_by_ocr(self, query: str, limit: int = 20) -> list[dict]:
        return self.env['rn.attachment.ocr.service'].search_attachments(query, limit=limit)

    @api.model
    def get_pdf_annotations(self, attachment_id: int) -> list[dict]:
        return self.env['rn.attachment.annotation.service'].list_for_attachment(attachment_id)

    @api.model
    def create_pdf_annotation(self, attachment_id: int, values: dict) -> dict:
        return self.env['rn.attachment.annotation.service'].create_annotation(attachment_id, values)

    @api.model
    def delete_pdf_annotation(self, annotation_id: int) -> bool:
        return self.env['rn.attachment.annotation.service'].delete_annotation(annotation_id)
