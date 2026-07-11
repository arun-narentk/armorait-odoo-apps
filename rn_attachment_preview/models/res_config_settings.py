# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_attachment_thumbnail_batch = fields.Integer(
        string='Thumbnail Cron Batch',
        config_parameter='rn_attachment_preview.thumbnail_batch',
        default=40,
    )
    rn_attachment_ocr_batch = fields.Integer(
        string='OCR Cron Batch',
        config_parameter='rn_attachment_preview.ocr_batch',
        default=40,
    )
    rn_attachment_enable_ocr_search = fields.Boolean(
        string='Enable OCR Search',
        config_parameter='rn_attachment_preview.enable_ocr_search',
        default=True,
    )
