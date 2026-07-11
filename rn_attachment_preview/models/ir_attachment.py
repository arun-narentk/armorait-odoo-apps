# -*- coding: utf-8 -*-

from odoo import api, fields, models

from ..constants import OCR_MIMETYPES, OFFICE_MIMETYPES, THUMBNAIL_MIMETYPES


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    rn_preview_type = fields.Char(compute='_compute_rn_preview_meta', string='Preview Type')
    rn_is_previewable = fields.Boolean(compute='_compute_rn_preview_meta', string='Previewable')
    rn_preview_thumbnail = fields.Binary(string='Preview Thumbnail', attachment=True)
    rn_thumbnail_state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('failed', 'Failed'),
            ('skipped', 'Skipped'),
        ],
        string='Thumbnail State',
        default='pending',
        index=True,
    )
    rn_ocr_text = fields.Text(string='Searchable Text')
    rn_ocr_state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('failed', 'Failed'),
            ('skipped', 'Skipped'),
        ],
        string='OCR State',
        default='pending',
        index=True,
    )
    rn_office_preview_html = fields.Html(string='Office Preview HTML', sanitize=False)
    rn_annotation_count = fields.Integer(compute='_compute_rn_annotation_count')
    rn_has_thumbnail = fields.Boolean(compute='_compute_rn_has_thumbnail')

    @api.depends('mimetype')
    def _compute_rn_preview_meta(self):
        service = self.env['rn.attachment.preview.service']
        for attachment in self:
            attachment.rn_preview_type = service.classify_mimetype(attachment.mimetype)
            attachment.rn_is_previewable = service.is_previewable(attachment)

    @api.depends('rn_preview_thumbnail')
    def _compute_rn_has_thumbnail(self):
        for attachment in self:
            attachment.rn_has_thumbnail = bool(attachment.rn_preview_thumbnail)

    def _compute_rn_annotation_count(self):
        if not self.ids:
            for attachment in self:
                attachment.rn_annotation_count = 0
            return
        grouped = self.env['rn.attachment.annotation'].read_group(
            [('attachment_id', 'in', self.ids)],
            ['attachment_id'],
            ['attachment_id'],
        )
        counts = {row['attachment_id'][0]: row['attachment_id_count'] for row in grouped}
        for attachment in self:
            attachment.rn_annotation_count = counts.get(attachment.id, 0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._apply_rn_processing_defaults(vals)
        attachments = super().create(vals_list)
        attachments._queue_rn_office_preview()
        return attachments

    def write(self, vals):
        content_changed = bool({'datas', 'raw', 'mimetype'} & set(vals))
        if {'datas', 'raw', 'mimetype', 'name'} & set(vals):
            if len(self) == 1:
                self._apply_rn_processing_defaults(vals, incoming=vals, record=self)
                result = super().write(vals)
            else:
                for attachment in self:
                    patch = dict(vals)
                    attachment._apply_rn_processing_defaults(patch, incoming=vals, record=attachment)
                    super(IrAttachment, attachment).write(patch)
                result = True
        else:
            result = super().write(vals)
        if content_changed:
            self._queue_rn_office_preview()
        return result

    def _apply_rn_processing_defaults(self, vals, incoming=None, record=None):
        incoming = incoming or {}
        mimetype = (incoming.get('mimetype') or vals.get('mimetype') or '')
        if record and not mimetype:
            mimetype = record.mimetype or ''
        mimetype = mimetype.lower()
        if not mimetype:
            name = incoming.get('name') or vals.get('name') or (record.name if record else None)
            if name:
                guess_vals = {'name': name}
                mimetype = (self._compute_mimetype(guess_vals) or '').lower()
        if mimetype in THUMBNAIL_MIMETYPES:
            vals['rn_thumbnail_state'] = 'pending'
            vals.pop('rn_preview_thumbnail', None)
        else:
            vals['rn_thumbnail_state'] = 'skipped'
        if mimetype in OCR_MIMETYPES:
            vals['rn_ocr_state'] = 'pending'
            vals.pop('rn_ocr_text', None)
        else:
            vals['rn_ocr_state'] = 'skipped'

    def _queue_rn_office_preview(self):
        office_attachments = self.filtered(
            lambda att: (att.mimetype or '').lower() in OFFICE_MIMETYPES and att.raw
        )
        for attachment in office_attachments:
            self.env['rn.attachment.office.service'].process_attachment(attachment)

    def get_rn_preview_data(self):
        self.ensure_one()
        return self.env['rn.attachment.preview.service'].attachment_to_dict(self)
