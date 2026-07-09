# -*- coding: utf-8 -*-
"""Offline sync profiles for mobile apps."""

from odoo import fields, models


class RnMobileSyncProfile(models.Model):
    _name = 'rn.mobile.sync.profile'
    _description = 'Mobile Sync Profile'
    _order = 'priority, id'

    priority = fields.Integer(default=10)
    app_id = fields.Many2one('rn.mobile.app', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='app_id.company_id', store=True, readonly=True)
    model_name = fields.Char(required=True)
    sync_mode = fields.Selection([('full', 'Full Sync'), ('delta', 'Delta Sync'), ('manual', 'Manual Sync')], default='delta', required=True)
    offline_limit = fields.Integer(default=500)
    conflict_strategy = fields.Selection([('server_wins', 'Server Wins'), ('device_wins', 'Device Wins'), ('manual_review', 'Manual Review')], default='manual_review', required=True)
