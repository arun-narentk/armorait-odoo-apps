# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnInventoryForecastSkeleton(TransactionCase):
    """Phase 1 tests for RN Inventory Forecast."""

    def test_groups_exist(self):
        group = self.env.ref('rn_inventory_forecast.group_rn_inv_forecast_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_dashboard_payload(self):
        data = self.env['rn.inv.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('inventory_value', data['cards'])

    def test_forecast_run_empty_history(self):
        today = fields.Date.context_today(self)
        run = self.env['rn.inv.forecast.run'].create({
            'name': 'Test Run',
            'period_type': 'weekly',
            'date_from': today - timedelta(days=30),
            'date_to': today,
            'horizon_days': 14,
        })
        run.action_generate()
        self.assertEqual(run.state, 'done')

    def test_abc_service_runs(self):
        today = fields.Date.context_today(self)
        result = self.env['rn.inv.abc.service'].run_analysis(
            today - timedelta(days=30), today
        )
        self.assertTrue(result is not None)
