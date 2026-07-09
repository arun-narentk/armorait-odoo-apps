# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnDashboardCoreSkeleton(TransactionCase):
    """Phase 1 tests for ARMORA Dashboard Core."""

    def test_groups_exist(self):
        group = self.env.ref('rn_dashboard_core.group_rn_dashboard_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_dashboard_payload(self):
        data = self.env['rn.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('charts', data)
        self.assertIn('dashboard', data)

    def test_filter_and_chart_services(self):
        date_from, date_to = self.env['rn.dashboard.filter.service'].resolve_dates('today')
        self.assertEqual(date_from, date_to)
        chart = self.env['rn.dashboard.chart.service'].build_pareto(
            ['A', 'B', 'C'], [50, 30, 20], title='Test'
        )
        self.assertEqual(chart['type'], 'pareto')
        self.assertEqual(len(chart['labels']), 3)

    def test_alert_evaluation(self):
        rule = self.env['rn.dashboard.alert.rule'].create({
            'name': 'Test Low Efficiency',
            'kpi_key': 'generic.efficiency_pct',
            'operator': 'lt',
            'threshold': 70,
            'severity': 'critical',
        })
        alerts = self.env['rn.dashboard.alert.service'].evaluate_rules({
            'generic.efficiency_pct': 50,
        })
        self.assertTrue(alerts)
        self.assertEqual(alerts[:1].severity, 'critical')
        self.assertTrue(rule.exists())
