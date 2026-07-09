# -*- coding: utf-8 -*-
"""Dashboard metrics for cloud platform operations."""

from odoo import models


class RnCloudDashboardService(models.AbstractModel):
    _name = 'rn.cloud.dashboard.service'
    _description = 'Cloud Dashboard Service'

    def get_dashboard_data(self):
        instances = self.env['rn.cloud.instance'].search([], limit=10)
        recs = self.env['rn.cloud.recommendation'].search([], order='create_date desc', limit=10)
        return {
            'providers': self.env['rn.cloud.provider'].search_count([]),
            'instances': self.env['rn.cloud.instance'].search_count([]),
            'running_instances': self.env['rn.cloud.instance'].search_count([('status', '=', 'running')]),
            'backups': self.env['rn.cloud.backup'].search_count([]),
            'open_recommendations': self.env['rn.cloud.recommendation'].search_count([('state', '=', 'open')]),
            'monitored_instances': self.env['rn.cloud.monitoring']._read_group([('id', '!=', 0)], ['instance_id'], ['__count']).__len__(),
            'recent_instances': [{'id': i.id, 'name': i.name, 'customer_name': i.customer_name, 'status': i.status, 'domain_name': i.domain_name} for i in instances],
            'recent_recommendations': [{'id': r.id, 'title': r.title, 'severity': r.severity, 'category': r.category, 'recommendation': r.recommendation} for r in recs],
        }
