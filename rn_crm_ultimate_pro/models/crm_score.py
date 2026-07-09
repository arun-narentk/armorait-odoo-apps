# -*- coding: utf-8 -*-
"""Lead scoring rules and score history."""

from odoo import fields, models


class RnCrmScoreRule(models.Model):
    """Configurable rule that adds or subtracts lead score points."""

    _name = 'rn.crm.score.rule'
    _description = 'CRM Lead Score Rule'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    rule_type = fields.Selection(
        selection=[
            ('phone', 'Phone Available'),
            ('email', 'Email Available'),
            ('website', 'Website Available'),
            ('revenue', 'Expected Revenue'),
            ('country', 'Country'),
            ('source', 'Lead Source'),
            ('tag', 'Tags'),
            ('activity', 'Activity Completed'),
            ('meeting', 'Meetings'),
            ('quotation', 'Quotation Sent'),
            ('sale', 'Sale Confirmed'),
            ('reply', 'Customer Reply'),
            ('late_response', 'Late Response'),
            ('negative', 'Negative Score'),
            ('custom', 'Custom Domain'),
        ],
        required=True,
    )
    points = fields.Integer(default=5, help='Positive or negative score impact.')
    domain = fields.Char(help='Optional domain to restrict when the rule applies.')
    max_points = fields.Integer(default=100)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class RnCrmScoreHistory(models.Model):
    """Audit trail of score changes on a lead/opportunity."""

    _name = 'rn.crm.score.history'
    _description = 'CRM Lead Score History'
    _order = 'create_date desc'

    lead_id = fields.Many2one('crm.lead', required=True, ondelete='cascade', index=True)
    score = fields.Integer()
    previous_score = fields.Integer()
    rule_id = fields.Many2one('rn.crm.score.rule', ondelete='set null')
    note = fields.Char()
    company_id = fields.Many2one(related='lead_id.company_id', store=True)
