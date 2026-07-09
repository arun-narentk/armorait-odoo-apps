# -*- coding: utf-8 -*-
"""Connector registry for triggers and actions."""

from odoo import fields, models


class RnWorkflowConnector(models.Model):
    """Registered integration connector (Odoo, email, webhook, WhatsApp, etc.)."""

    _name = 'rn.workflow.connector'
    _description = 'Workflow Connector'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    connector_type = fields.Selection(
        [
            ('odoo', 'Odoo Model'),
            ('email', 'Email'),
            ('webhook', 'Webhook'),
            ('whatsapp', 'WhatsApp'),
            ('sms', 'SMS'),
            ('slack', 'Slack'),
            ('teams', 'Microsoft Teams'),
            ('ai', 'AI Service'),
            ('mes', 'Manufacturing MES'),
            ('ocr', 'Invoice OCR'),
        ],
        required=True,
        default='odoo',
    )
    description = fields.Text()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    is_external = fields.Boolean(default=False)
    config_schema = fields.Text(string='Config Schema JSON')
