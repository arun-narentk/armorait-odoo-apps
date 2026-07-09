# -*- coding: utf-8 -*-
"""Metadata-driven mobile app definitions."""

from odoo import api, fields, models


class RnMobileApp(models.Model):
    _name = 'rn.mobile.app'
    _description = 'Mobile App Definition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    app_scope = fields.Selection(
        [('warehouse', 'Warehouse'), ('sales', 'Sales'), ('service', 'Field Service'), ('customer', 'Customer'), ('manager', 'Manager')],
        required=True, default='warehouse', tracking=True,
    )
    target_model = fields.Char(required=True, default='stock.picking')
    platform_state = fields.Selection([('draft', 'Draft'), ('ready', 'Ready'), ('published', 'Published')], default='draft', required=True)
    android_bundle = fields.Char()
    ios_bundle = fields.Char()
    enable_offline = fields.Boolean(default=True)
    enable_barcode = fields.Boolean(default=True)
    enable_camera = fields.Boolean(default=False)
    enable_gps = fields.Boolean(default=False)
    enable_push = fields.Boolean(default=True)
    enable_signature = fields.Boolean(default=False)
    screen_ids = fields.One2many('rn.mobile.screen', 'app_id')
    sync_profile_ids = fields.One2many('rn.mobile.sync.profile', 'app_id')
    theme_ids = fields.One2many('rn.mobile.theme', 'app_id')
    screen_count = fields.Integer(compute='_compute_counts')
    sync_profile_count = fields.Integer(compute='_compute_counts')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rn.mobile.app') or 'New'
        return super().create(vals_list)

    def _compute_counts(self):
        screen_group = self.env['rn.mobile.screen']._read_group([('app_id', 'in', self.ids)], ['app_id'], ['__count'])
        screen_counts = {app.id: count for app, count in screen_group}
        sync_group = self.env['rn.mobile.sync.profile']._read_group([('app_id', 'in', self.ids)], ['app_id'], ['__count'])
        sync_counts = {app.id: count for app, count in sync_group}
        for record in self:
            record.screen_count = screen_counts.get(record.id, 0)
            record.sync_profile_count = sync_counts.get(record.id, 0)
