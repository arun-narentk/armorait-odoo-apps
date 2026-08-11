# -*- coding: utf-8 -*-
"""Phase 2 backend model tests for Dashboard KPI Studio."""

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_dashboard_kpi')
class TestRnKpiDashboardModels(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Dashboard = cls.env['rn.kpi.dashboard']
        cls.Item = cls.env['rn.kpi.dashboard.item']
        cls.Filter = cls.env['rn.kpi.dashboard.filter']
        cls.users_model = cls.env.ref('base.model_res_users')

    def _create_dashboard(self, **vals):
        values = {
            'name': 'Test Board',
            'theme': 'light',
        }
        values.update(vals)
        return self.Dashboard.create(values)

    def _create_tile(self, dashboard, **vals):
        values = {
            'dashboard_id': dashboard.id,
            'name': 'User Count',
            'item_type': 'tile',
            'model_id': self.users_model.id,
            'aggregation': 'count',
        }
        values.update(vals)
        return self.Item.create(values)

    def test_create_dashboard_and_item(self):
        dashboard = self._create_dashboard()
        item = self._create_tile(dashboard)
        self.assertEqual(dashboard.item_ids, item)
        self.assertEqual(item.chart_type, 'tile')
        self.assertTrue(dashboard.company_ids)
        action = dashboard.action_open_dashboard()
        self.assertEqual(action['type'], 'ir.actions.client')
        self.assertEqual(action['tag'], 'rn_dashboard_kpi.dashboard')
        self.assertEqual(action['params']['dashboard_id'], dashboard.id)

    def test_bookmark_unique_per_user(self):
        dashboard = self._create_dashboard(name='Bookmarked')
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

    def test_toggle_favorite(self):
        dashboard = self._create_dashboard()
        self.assertFalse(dashboard.is_favorite)
        dashboard.action_toggle_favorite()
        self.assertTrue(dashboard.is_favorite)
        self.assertTrue(dashboard.bookmark_ids.filtered(lambda b: b.user_id == self.env.user))
        dashboard.action_toggle_favorite()
        self.assertFalse(dashboard.is_favorite)

    def test_duplicate_dashboard_copies_items_and_filters(self):
        dashboard = self._create_dashboard()
        self._create_tile(dashboard)
        self.Filter.create({
            'dashboard_id': dashboard.id,
            'name': 'This Month',
            'filter_type': 'date',
            'date_filter_type': 'this_month',
            'field_name': 'create_date',
        })
        action = dashboard.action_duplicate()
        new_dashboard = self.Dashboard.browse(action['res_id'])
        self.assertNotEqual(new_dashboard.id, dashboard.id)
        self.assertIn('(copy)', new_dashboard.name)
        self.assertEqual(len(new_dashboard.item_ids), 1)
        self.assertEqual(len(new_dashboard.filter_ids), 1)
        self.assertFalse(new_dashboard.action_id)
        self.assertFalse(new_dashboard.menu_id)

    def test_export_definition_uses_technical_names(self):
        dashboard = self._create_dashboard(description='Export me')
        self._create_tile(dashboard, measure=False, group_by='login')
        definition = dashboard.get_dashboard_definition()
        self.assertEqual(definition['module'], 'rn_dashboard_kpi')
        self.assertEqual(definition['dashboard']['name'], dashboard.name)
        self.assertEqual(definition['items'][0]['model'], 'res.users')
        self.assertNotIn('id', definition['items'][0])
        export_action = dashboard.action_export()
        self.assertEqual(export_action['type'], 'ir.actions.act_url')
        self.assertIn('/web/content/', export_action['url'])

    def test_item_rejects_invalid_domain(self):
        dashboard = self._create_dashboard()
        with self.assertRaises(ValidationError):
            self._create_tile(dashboard, domain='not-a-domain')

    def test_item_rejects_unknown_field(self):
        dashboard = self._create_dashboard()
        with self.assertRaises(ValidationError):
            self._create_tile(dashboard, measure='not_a_real_field', aggregation='sum')

    def test_item_requires_measure_for_sum(self):
        dashboard = self._create_dashboard()
        with self.assertRaises(ValidationError):
            self._create_tile(dashboard, aggregation='sum', measure=False)

    def test_item_layout_min_size(self):
        dashboard = self._create_dashboard()
        with self.assertRaises(ValidationError):
            self._create_tile(dashboard, layout_width=1, min_width=2)

    def test_company_consistency(self):
        other = self.env['res.company'].create({'name': 'Other Co KPI'})
        dashboard = self._create_dashboard()
        with self.assertRaises(ValidationError):
            dashboard.write({
                'company_ids': [(6, 0, [other.id])],
            })

    def test_get_data_stub_payload(self):
        dashboard = self._create_dashboard()
        item = self._create_tile(dashboard)
        payload = item.get_data()
        self.assertEqual(payload['labels'], [])
        self.assertEqual(payload['total'], 0)
        self.assertTrue(payload['warnings'])
        self.assertEqual(payload['metadata']['model'], 'res.users')

    def test_duplicate_item(self):
        dashboard = self._create_dashboard()
        item = self._create_tile(dashboard)
        clone = item.duplicate_item()
        self.assertNotEqual(clone.id, item.id)
        self.assertEqual(clone.dashboard_id, dashboard)
        self.assertIn('(copy)', clone.name)

    def test_create_menu(self):
        dashboard = self._create_dashboard(name='Menu Board')
        dashboard.action_create_menu()
        self.assertTrue(dashboard.action_id)
        self.assertTrue(dashboard.menu_id)
        self.assertEqual(dashboard.action_id.tag, 'rn_dashboard_kpi.dashboard')
        self.assertEqual(dashboard.menu_id.name, 'Menu Board')

    def test_get_data_count(self):
        dashboard = self._create_dashboard()
        item = self._create_tile(dashboard)
        payload = item.get_data()
        self.assertFalse(payload.get('warnings'))
        self.assertGreaterEqual(payload['total'], 1)
        self.assertEqual(payload['metadata']['model'], 'res.users')
        self.assertEqual(payload['labels'], [item.name])
