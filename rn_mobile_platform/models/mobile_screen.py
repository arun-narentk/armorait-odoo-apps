# -*- coding: utf-8 -*-
"""Screen metadata for generated business apps."""

from odoo import fields, models


class RnMobileScreen(models.Model):
    _name = 'rn.mobile.screen'
    _description = 'Mobile Screen'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    app_id = fields.Many2one('rn.mobile.app', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='app_id.company_id', store=True, readonly=True)
    name = fields.Char(required=True)
    screen_type = fields.Selection(
        [('list', 'List'), ('form', 'Form'), ('dashboard', 'Dashboard'), ('cards', 'Cards'), ('barcode', 'Barcode'), ('camera', 'Camera'), ('map', 'Map'), ('signature', 'Signature')],
        required=True, default='list',
    )
    model_name = fields.Char(required=True)
    access_role = fields.Selection([('user', 'User'), ('manager', 'Manager'), ('customer', 'Customer')], default='user', required=True)
    offline_enabled = fields.Boolean(default=True)
