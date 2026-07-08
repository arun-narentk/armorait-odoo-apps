# -*- coding: utf-8 -*-
"""Alert rules and live alert events."""

from odoo import fields, models


class RnDashboardAlertRule(models.Model):
    """Threshold rule evaluated by alert_service and domain modules."""

    _name = 'rn.dashboard.alert.rule'
    _description = 'Dashboard Alert Rule'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    dashboard_id = fields.Many2one('rn.dashboard', ondelete='cascade', index=True)
    kpi_key = fields.Char(required=True, index=True)
    operator = fields.Selection(
        selection=[
            ('lt', 'Less Than'),
            ('lte', 'Less or Equal'),
            ('gt', 'Greater Than'),
            ('gte', 'Greater or Equal'),
            ('eq', 'Equal'),
        ],
        default='lt',
        required=True,
    )
    threshold = fields.Float(required=True)
    severity = fields.Selection(
        selection=[
            ('info', 'Info'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
        ],
        default='warning',
        required=True,
    )
    channel_email = fields.Boolean(string='Email')
    channel_activity = fields.Boolean(string='Activity', default=True)
    # Future: WhatsApp / SMS / Teams / Slack via companion modules
    message_template = fields.Char(
        default='Alert: %(kpi)s is %(value)s (threshold %(threshold)s)',
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )


class RnDashboardAlert(models.Model):
    """Raised alert instance shown on boards and TV layouts."""

    _name = 'rn.dashboard.alert'
    _description = 'Dashboard Alert'
    _order = 'create_date desc, id desc'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)
    rule_id = fields.Many2one('rn.dashboard.alert.rule', ondelete='set null', index=True)
    dashboard_id = fields.Many2one('rn.dashboard', index=True)
    kpi_key = fields.Char(index=True)
    value = fields.Float()
    threshold = fields.Float()
    severity = fields.Selection(
        selection=[
            ('info', 'Info'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
        ],
        default='warning',
        required=True,
        index=True,
    )
    state = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('ack', 'Acknowledged'),
            ('done', 'Resolved'),
        ],
        default='open',
        tracking=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    def action_acknowledge(self):
        self.write({'state': 'ack'})
        return True

    def action_resolve(self):
        self.write({'state': 'done'})
        return True
