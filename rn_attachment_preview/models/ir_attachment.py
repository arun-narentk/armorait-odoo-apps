# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    rn_preview_type = fields.Char(compute='_compute_rn_preview_meta', string='Preview Type')
    rn_is_previewable = fields.Boolean(compute='_compute_rn_preview_meta', string='Previewable')

    @api.depends('mimetype')
    def _compute_rn_preview_meta(self):
        service = self.env['rn.attachment.preview.service']
        for attachment in self:
            attachment.rn_preview_type = service.classify_mimetype(attachment.mimetype)
            attachment.rn_is_previewable = service.is_previewable(attachment)

    def get_rn_preview_data(self):
        self.ensure_one()
        return self.env['rn.attachment.preview.service'].attachment_to_dict(self)
