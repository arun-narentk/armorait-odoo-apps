# -*- coding: utf-8 -*-
"""Evaluate alert rules against KPI maps."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnDashboardAlertService(models.AbstractModel):
    """Raise and list dashboard alerts."""

    _name = 'rn.dashboard.alert.service'
    _description = 'Dashboard Alert Service'

    def _compare(self, operator, value, threshold):
        if operator == 'lt':
            return value < threshold
        if operator == 'lte':
            return value <= threshold
        if operator == 'gt':
            return value > threshold
        if operator == 'gte':
            return value >= threshold
        return value == threshold

    def evaluate_rules(self, kpi_map, dashboard=None, company_id=None):
        """kpi_map: dict key -> numeric value. Returns created alert records."""
        company_id = company_id or self.env.company.id
        domain = [('active', '=', True), ('company_id', '=', company_id)]
        if dashboard:
            domain = ['|', ('dashboard_id', '=', False), ('dashboard_id', '=', dashboard.id)] + domain
        rules = self.env['rn.dashboard.alert.rule'].search(domain)
        created = self.env['rn.dashboard.alert']
        for rule in rules:
            if rule.kpi_key not in kpi_map:
                continue
            value = float(kpi_map.get(rule.kpi_key) or 0.0)
            if not self._compare(rule.operator, value, rule.threshold):
                continue
            message = (rule.message_template or 'Alert: %(kpi)s') % {
                'kpi': rule.kpi_key,
                'value': value,
                'threshold': rule.threshold,
            }
            alert = self.env['rn.dashboard.alert'].create({
                'name': message,
                'rule_id': rule.id,
                'dashboard_id': dashboard.id if dashboard else False,
                'kpi_key': rule.kpi_key,
                'value': value,
                'threshold': rule.threshold,
                'severity': rule.severity,
                'company_id': company_id,
            })
            created |= alert
            if rule.channel_activity and dashboard:
                dashboard.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=message[:100],
                    note=message,
                )
        _logger.info('Raised %s dashboard alerts', len(created))
        return created

    def open_alerts(self, company_id=None, limit=20):
        company_id = company_id or self.env.company.id
        return self.env['rn.dashboard.alert'].search([
            ('company_id', '=', company_id),
            ('state', '=', 'open'),
        ], limit=limit)
