# -*- coding: utf-8 -*-
"""PDF annotation business logic."""

from __future__ import annotations

from odoo import _, api, models
from odoo.exceptions import AccessError, UserError


class RnAttachmentAnnotationService(models.AbstractModel):
    _name = 'rn.attachment.annotation.service'
    _description = 'Attachment Annotation Service'

    @api.model
    def list_for_attachment(self, attachment_id: int) -> list[dict]:
        attachment = self.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            raise UserError(_('Attachment not found.'))
        attachment.check_access('read')
        annotations = self.env['rn.attachment.annotation'].search([
            ('attachment_id', '=', attachment_id),
        ], order='page_number, id')
        annotations.check_access('read')
        return [row.to_panel_dict() for row in annotations]

    @api.model
    def create_annotation(self, attachment_id: int, values: dict) -> dict:
        attachment = self.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            raise UserError(_('Attachment not found.'))
        attachment.check_access('read')
        if (attachment.mimetype or '').lower() != 'application/pdf':
            raise UserError(_('Annotations are supported on PDF files only.'))
        note = (values.get('note') or '').strip()
        if not note:
            raise UserError(_('Annotation note is required.'))
        annotation = self.env['rn.attachment.annotation'].create({
            'attachment_id': attachment_id,
            'page_number': int(values.get('page_number') or 1),
            'pos_x': float(values.get('pos_x') or 10.0),
            'pos_y': float(values.get('pos_y') or 10.0),
            'note': note,
            'color': values.get('color') or '#facc15',
        })
        return annotation.to_panel_dict()

    @api.model
    def delete_annotation(self, annotation_id: int) -> bool:
        annotation = self.env['rn.attachment.annotation'].browse(annotation_id)
        if not annotation.exists():
            raise UserError(_('Annotation not found.'))
        if annotation.user_id != self.env.user and not self.env.user.has_group(
            'rn_attachment_preview.group_rn_attachment_preview_manager'
        ):
            raise AccessError(_('You can only delete your own annotations.'))
        annotation.unlink()
        return True
