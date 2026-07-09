# -*- coding: utf-8 -*-
"""Portal usage analytics events."""

from odoo import fields, models


class RnCustomerExperienceAnalytics(models.Model):
    _name = 'rn.customer.experience.analytics'
    _description = 'Experience Analytics Event'
    _order = 'create_date desc'

    partner_id = fields.Many2one('res.partner', index=True)
    user_id = fields.Many2one('res.users', index=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    event_type = fields.Selection(
        selection=[
            ('login', 'Portal Login'),
            ('dashboard', 'Dashboard View'),
            ('invoice_view', 'Invoice View'),
            ('payment', 'Payment Action'),
            ('download', 'Download'),
            ('ticket_create', 'Ticket Created'),
            ('ai_query', 'AI Assistant Query'),
            ('quotation_accept', 'Quotation Accepted'),
        ],
        required=True,
        index=True,
    )
    description = fields.Char()
    metadata = fields.Text()
