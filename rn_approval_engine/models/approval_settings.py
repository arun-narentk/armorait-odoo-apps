# -*- coding: utf-8 -*-
"""Company approval settings."""

from odoo import fields, models


class RnApprovalSettings(models.Model):
    """Per-company approval engine configuration."""

    _name = 'rn.approval.settings'
    _description = 'Approval Settings'
    _inherit = ['mail.thread']

    name = fields.Char(default='Approval Settings', required=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    enable_email_notify = fields.Boolean(default=True, string='Email Notifications')
    enable_whatsapp_notify = fields.Boolean(
        default=False,
        string='WhatsApp Notifications',
        help='Requires rn_whatsapp_connector companion module.',
    )
    enable_ai_risk = fields.Boolean(default=True, string='AI Risk Hints')
    default_sla_hours = fields.Integer(default=24)
    reminder_hours = fields.Integer(default=8, string='Reminder Before SLA (hours)')
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one approval settings record per company.',
    )
