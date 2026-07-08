# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnBiSalesDashboardSkeleton(TransactionCase):
    """Phase 1 tests for BI Sales Dashboard."""

    def test_groups_exist(self):
        group = self.env.ref('rn_bi_sales_dashboard.group_rn_bi_sales_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_dashboard_payload(self):
        data = self.env['rn.bi.dashboard.service'].get_dashboard_data({'date_preset': 'this_month'})
        self.assertIn('cards', data)
        self.assertIn('total_revenue', data['cards'])
        self.assertIn('charts', data)
        self.assertIn('forecast', data)

    def test_cache_roundtrip(self):
        Cache = self.env['rn.bi.cache.service']
        Cache.clear()
        Cache.set('bi_sales:test', {'ok': True}, ttl=60)
        self.assertEqual(Cache.get('bi_sales:test'), {'ok': True})
        Cache.clear('bi_sales:')
        self.assertIsNone(Cache.get('bi_sales:test'))

    def test_target_lookup(self):
        date_start, date_end = self.env['rn.bi.dashboard.service']._resolve_dates('this_month')
        target = self.env['rn.bi.sales.target'].create({
            'name': 'Test Target',
            'period_type': 'month',
            'date_start': date_start,
            'date_end': date_end,
            'target_amount': 5000,
            'state': 'open',
        })
        info = self.env['rn.bi.target.service'].get_current_target()
        self.assertEqual(info.get('id'), target.id)
        self.assertIn('achievement_pct', info)
