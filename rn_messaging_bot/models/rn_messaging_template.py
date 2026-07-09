# -*- coding: utf-8 -*-
"""Reusable outbound message templates with simple variables."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RnMessagingTemplate(models.Model):
    _name = 'rn.messaging.template'
    _description = 'Messaging Template'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
    connector_id = fields.Many2one(
        'rn.messaging.connector',
        string='Connector',
        domain="[('company_id', '=', company_id)]",
    )
    channel_type = fields.Selection(
        selection=[
            ('whatsapp', 'WhatsApp'),
            ('instagram', 'Instagram DM'),
            ('facebook', 'Facebook Messenger'),
            ('livechat', 'Website Live Chat'),
        ],
    )
    body = fields.Text(
        required=True,
        help='Use placeholders such as {{partner_name}}, {{phone}}, {{company}}.',
    )
    external_template_name = fields.Char(
        string='Provider Template Name',
        help='Optional approved template name for WhatsApp Cloud API.',
    )
    description = fields.Text()

    @api.constrains('body')
    def _check_body_not_empty(self):
        for template in self:
            if not (template.body or '').strip():
                raise ValidationError('Template body cannot be empty.')

    def render_body(self, partner=None, conversation=None, extra_values=None):
        self.ensure_one()
        return self.env['rn.messaging.template.service'].render(
            self,
            partner=partner,
            conversation=conversation,
            extra_values=extra_values or {},
        )
