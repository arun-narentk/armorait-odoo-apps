# -*- coding: utf-8 -*-
"""Branding and theme settings for mobile apps."""

from odoo import fields, models


class RnMobileTheme(models.Model):
    _name = 'rn.mobile.theme'
    _description = 'Mobile Theme'
    _order = 'name'

    name = fields.Char(required=True)
    app_id = fields.Many2one('rn.mobile.app', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='app_id.company_id', store=True, readonly=True)
    primary_color = fields.Char(default='#0d6efd')
    secondary_color = fields.Char(default='#6c757d')
    logo = fields.Binary()
    splash_title = fields.Char(default='ARMORA Mobile')
    icon_style = fields.Selection([('rounded', 'Rounded'), ('flat', 'Flat'), ('outlined', 'Outlined')], default='rounded', required=True)
