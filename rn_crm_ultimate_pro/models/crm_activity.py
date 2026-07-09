# -*- coding: utf-8 -*-
"""Smart activity recommendation templates."""

from odoo import fields, models


class RnCrmActivityTemplate(models.Model):
    """Recommended next activities based on lead context."""

    _name = 'rn.crm.activity.template'
    _description = 'CRM Smart Activity Template'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    activity_kind = fields.Selection(
        selection=[
            ('call', 'Call'),
            ('email', 'Email'),
            ('meeting', 'Meeting'),
            ('demo', 'Demo'),
            ('proposal', 'Proposal'),
            ('reminder', 'Reminder'),
            ('followup', 'Follow-up'),
        ],
        required=True,
    )
    activity_type_id = fields.Many2one('mail.activity.type')
    summary = fields.Char()
    delay_days = fields.Integer(default=1)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
