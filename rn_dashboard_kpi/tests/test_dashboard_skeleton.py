# -*- coding: utf-8 -*-
"""Phase 1 install and skeleton smoke tests."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_dashboard_kpi')
class TestRnKpiDashboardSkeleton(TransactionCase):

    def test_create_dashboard_and_item(self):
        dashboard = self.env['rn.kpi.dashboard'].create({
            'name': 'Skeleton Board',
            'theme': 'light',
        })
        item = self.env['rn.kpi.dashboard.item'].create({
            'dashboard_id': dashboard.id,
            'name': 'User Count',
            'item_type': 'tile',
            'model_id': self.env.ref('base.model_res_users').id,
            'aggregation': 'count',
        })
        self.assertEqual(dashboard.item_ids, item)
        action = dashboard.action_open_dashboard()
        self.assertEqual(action['type'], 'ir.actions.client')
        self.assertEqual(action['tag'], 'rn_dashboard_kpi.dashboard')
        self.assertEqual(action['params']['dashboard_id'], dashboard.id)

    def test_bookmark_unique_per_user(self):
        dashboard = self.env['rn.kpi.dashboard'].create({'name': 'Bookmarked'})
        Bookmark = self.env['rn.kpi.dashboard.bookmark']
        Bookmark.create({
            'dashboard_id': dashboard.id,
            'user_id': self.env.user.id,
        })
        with self.assertRaises(Exception):
            Bookmark.create({
                'dashboard_id': dashboard.id,
                'user_id': self.env.user.id,
            })
