# -*- coding: utf-8 -*-
"""Dashboard metrics for the mobile platform."""

from odoo import models


class RnMobileDashboardService(models.AbstractModel):
    _name = 'rn.mobile.dashboard.service'
    _description = 'Mobile Dashboard Service'

    def get_dashboard_data(self):
        apps = self.env['rn.mobile.app'].search([], limit=10)
        return {
            'apps': self.env['rn.mobile.app'].search_count([]),
            'published_apps': self.env['rn.mobile.app'].search_count([('platform_state', '=', 'published')]),
            'offline_enabled_apps': self.env['rn.mobile.app'].search_count([('enable_offline', '=', True)]),
            'barcode_apps': self.env['rn.mobile.app'].search_count([('enable_barcode', '=', True)]),
            'push_enabled_apps': self.env['rn.mobile.app'].search_count([('enable_push', '=', True)]),
            'recent_apps': [{
                'id': app.id,
                'name': app.name,
                'scope': app.app_scope,
                'state': app.platform_state,
                'model': app.target_model,
            } for app in apps],
        }
