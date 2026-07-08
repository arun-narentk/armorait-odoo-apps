# -*- coding: utf-8 -*-
"""WhatsApp message template model."""

from odoo import fields, models


class RnWhatsappTemplate(models.Model):
    """Stores provider-backed or local WhatsApp message templates."""

    _name = 'rn.whatsapp.template'
    _description = 'WhatsApp Template'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(string='Template Name', required=True, tracking=True)
    account_id = fields.Many2one(
        'rn.whatsapp.account',
        string='Account',
        required=True,
        ondelete='cascade',
    )
    language = fields.Char(default='en')
    body = fields.Text(required=True)
    header = fields.Char()
    footer = fields.Char()
    button_json = fields.Text(string='Buttons', help='JSON definition for template buttons.')
    media_type = fields.Selection(
        selection=[
            ('none', 'None'),
            ('image', 'Image'),
            ('video', 'Video'),
            ('document', 'Document'),
        ],
        default='none',
    )
    variable_ids = fields.Char(string='Variables', help='Comma-separated variable placeholders.')
    approved = fields.Boolean(default=False, tracking=True)
    provider_template_id = fields.Char(string='Provider Template ID', copy=False)
    category = fields.Selection(
        selection=[
            ('marketing', 'Marketing'),
            ('utility', 'Utility'),
            ('authentication', 'Authentication'),
        ],
        default='utility',
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
