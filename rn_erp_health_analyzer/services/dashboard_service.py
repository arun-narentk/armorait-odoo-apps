# -*- coding: utf-8 -*-
"""Executive dashboard metrics for ERP health."""

from odoo import models


class RnErpHealthDashboardService(models.AbstractModel):
    _name = 'rn.erp.health.dashboard.service'
    _description = 'ERP Health Dashboard Service'

    def get_dashboard_data(self):
        scans = self.env['rn.erp.health.scan'].search([], order='create_date desc', limit=12)
        findings = self.env['rn.erp.health.finding'].search([], order='create_date desc', limit=20)
        latest_score = scans[:1].overall_score if scans else 0
        return {
            'latest_score': latest_score,
            'scan_count': self.env['rn.erp.health.scan'].search_count([]),
            'open_findings': self.env['rn.erp.health.finding'].search_count([('state', '=', 'open')]),
            'critical_findings': self.env['rn.erp.health.finding'].search_count([('severity', '=', 'critical'), ('state', '=', 'open')]),
            'high_findings': self.env['rn.erp.health.finding'].search_count([('severity', '=', 'high'), ('state', '=', 'open')]),
            'targets': self.env['rn.erp.health.target'].search_count([('active', '=', True)]),
            'recent_scans': [{
                'id': scan.id,
                'name': scan.name,
                'score': scan.overall_score,
                'risk_level': scan.risk_level,
                'target': scan.target_id.name,
            } for scan in scans],
            'recent_findings': [{
                'id': finding.id,
                'name': finding.name,
                'severity': finding.severity,
                'category': finding.category,
                'recommendation': finding.recommendation,
            } for finding in findings],
        }
