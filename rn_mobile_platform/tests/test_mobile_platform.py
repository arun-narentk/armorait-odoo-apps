# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_mobile_platform')
class TestMobilePlatform(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.app = cls.env['rn.mobile.app'].create({
            'app_scope': 'warehouse',
            'target_model': 'stock.picking',
            'platform_state': 'published',
            'enable_offline': True,
            'enable_barcode': True,
            'enable_camera': True,
            'enable_push': True,
        })
        cls.screen = cls.env['rn.mobile.screen'].create({
            'app_id': cls.app.id,
            'name': 'Delivery Orders',
            'screen_type': 'list',
            'model_name': 'stock.picking',
            'access_role': 'user',
            'offline_enabled': True,
        })
        cls.sync = cls.env['rn.mobile.sync.profile'].create({
            'app_id': cls.app.id,
            'model_name': 'stock.picking',
            'sync_mode': 'delta',
            'offline_limit': 250,
            'conflict_strategy': 'manual_review',
        })
        cls.theme = cls.env['rn.mobile.theme'].create({
            'app_id': cls.app.id,
            'name': 'Warehouse Theme',
            'primary_color': '#0d6efd',
            'secondary_color': '#6c757d',
            'icon_style': 'rounded',
        })
        cls.builder = cls.env['rn.mobile.builder.service']
        cls.dashboard = cls.env['rn.mobile.dashboard.service']

    def test_build_metadata_contains_features(self):
        data = self.builder.build_metadata(self.app)
        self.assertEqual(data['app']['scope'], 'warehouse')
        self.assertTrue(data['app']['features']['offline'])
        self.assertTrue(data['screens'])

    def test_app_counts_related_records(self):
        self.app.invalidate_recordset(['screen_count', 'sync_profile_count'])
        self.assertEqual(self.app.screen_count, 1)
        self.assertEqual(self.app.sync_profile_count, 1)

    def test_dashboard_returns_metrics(self):
        data = self.dashboard.get_dashboard_data()
        self.assertIn('apps', data)
        self.assertIn('recent_apps', data)
        self.assertGreaterEqual(data['offline_enabled_apps'], 1)

    def test_theme_is_linked(self):
        self.assertEqual(self.theme.app_id, self.app)
