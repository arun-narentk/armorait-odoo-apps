# -*- coding: utf-8 -*-
"""Escalated customer conversations for human follow-up."""

from odoo import fields, models


class RnCustomerEngagementEscalation(models.Model):
    _name = 'rn.customer.engagement.escalation'
    _description = 'Customer Engagement Escalation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, copy=False, default='New')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    conversation_id = fields.Many2one('rn.customer.engagement.conversation', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', ondelete='set null')
    category = fields.Selection([('support', 'Support'), ('billing', 'Billing'), ('delivery', 'Delivery'), ('sales', 'Sales')], default='support', required=True)
    state = fields.Selection([('new', 'New'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')], default='new', required=True)
    summary = fields.Text(required=True)
    assigned_user_id = fields.Many2one('res.users')
