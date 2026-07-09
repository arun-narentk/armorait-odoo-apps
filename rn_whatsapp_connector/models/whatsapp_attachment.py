# -*- coding: utf-8 -*-
"""WhatsApp attachment model."""

from odoo import fields, models


class RnWhatsappAttachment(models.Model):
    """Binary attachment linked to a WhatsApp message."""

    _name = 'rn.whatsapp.attachment'
    _description = 'WhatsApp Attachment'
    _order = 'id desc'

    name = fields.Char(required=True)
    message_id = fields.Many2one(
        'rn.whatsapp.message',
        string='Message',
        required=True,
        ondelete='cascade',
    )
    attachment_type = fields.Selection(
        selection=[
            ('file', 'File'),
            ('image', 'Image'),
            ('video', 'Video'),
            ('pdf', 'PDF'),
            ('audio', 'Audio'),
            ('document', 'Document'),
        ],
        default='file',
        required=True,
    )
    datas = fields.Binary(required=True, attachment=True)
    mimetype = fields.Char(string='Mime Type')
    file_size = fields.Integer(string='Size')
    company_id = fields.Many2one(
        'res.company',
        related='message_id.company_id',
        store=True,
    )
