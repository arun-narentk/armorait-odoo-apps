# -*- coding: utf-8 -*-
"""Branding and portal experience configuration per company."""

from odoo import fields, models


class RnCustomerExperienceConfig(models.Model):
    _name = 'rn.customer.experience.config'
    _description = 'Customer Experience Config'
    _rec_name = 'name'

    name = fields.Char(default='Experience Portal', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    portal_title = fields.Char(default='My Experience')
    welcome_message = fields.Html()
    logo = fields.Binary(string='Portal Logo')
    primary_color = fields.Char(default='#0d6efd')
    secondary_color = fields.Char(default='#6c757d')
    custom_domain = fields.Char(help='Optional white-label domain for the portal.')
    login_background = fields.Binary(string='Login Background')
    enable_orders = fields.Boolean(default=True)
    enable_invoices = fields.Boolean(default=True)
    enable_payments = fields.Boolean(default=True)
    enable_downloads = fields.Boolean(default=True)
    enable_tickets = fields.Boolean(default=True)
    enable_warranty = fields.Boolean(default=True)
    enable_amc = fields.Boolean(default=True)
    enable_ai_assistant = fields.Boolean(default=True)
    page_ids = fields.One2many('rn.customer.experience.page', 'config_id')

    def get_portal_values(self):
        self.ensure_one()
        return {
            'portal_title': self.portal_title,
            'welcome_message': self.welcome_message or '',
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'enable_orders': self.enable_orders,
            'enable_invoices': self.enable_invoices,
            'enable_payments': self.enable_payments,
            'enable_downloads': self.enable_downloads,
            'enable_tickets': self.enable_tickets,
            'enable_warranty': self.enable_warranty,
            'enable_amc': self.enable_amc,
            'enable_ai_assistant': self.enable_ai_assistant,
        }
