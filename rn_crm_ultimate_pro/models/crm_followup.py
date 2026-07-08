# -*- coding: utf-8 -*-
"""Follow-up automation rules."""

from odoo import fields, models


class RnCrmFollowupRule(models.Model):
    """Defines automated follow-up / escalation behaviour."""

    _name = 'rn.crm.followup.rule'
    _description = 'CRM Follow-up Rule'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    trigger = fields.Selection(
        selection=[
            ('no_activity', 'No Activity'),
            ('missed_activity', 'Missed Activity'),
            ('stage_aging', 'Stage Aging'),
            ('lead_aging', 'Lead Aging'),
            ('inactive', 'Inactive Lead'),
        ],
        required=True,
    )
    delay_days = fields.Integer(default=3)
    escalate_to_manager = fields.Boolean()
    create_activity_type_id = fields.Many2one('mail.activity.type', string='Activity Type')
    notify_salesperson = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
