# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_filter_manager')
class TestRnFilterManager(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['rn.filter.service']
        cls.folder_sales = cls.env['rn.filter.folder'].create({
            'name': 'Test Sales Folder',
            'color': 'green',
        })
        cls.filter_rec = cls.env['ir.filters'].create({
            'name': 'FILTTEST Confirmed Orders',
            'model_id': 'sale.order',
            'domain': "[('state', '=', 'sale')]",
            'context': '{}',
            'sort': '[]',
            'rn_folder_id': cls.folder_sales.id,
            'rn_is_favorite': True,
            'rn_share_type': 'private',
            'user_ids': [(6, 0, [cls.env.user.id])],
        })

    def test_folder_filter_count(self):
        self.assertEqual(self.folder_sales.filter_count, 1)

    def test_pin_and_favorite(self):
        self.filter_rec.action_pin()
        self.assertTrue(self.filter_rec.rn_is_pinned)
        self.filter_rec.action_mark_favorite()
        self.assertTrue(self.filter_rec.rn_is_favorite)

    def test_usage_logging(self):
        self.service.log_filter_usage(self.filter_rec, source='manager')
        history = self.env['rn.filter.history'].search([
            ('filter_id', '=', self.filter_rec.id),
            ('user_id', '=', self.env.user.id),
        ], limit=1)
        self.assertTrue(history)
        self.filter_rec.invalidate_recordset()
        self.assertGreaterEqual(self.filter_rec.rn_usage_count, 1)

    def test_duplicate_detection(self):
        duplicate = self.env['ir.filters'].create({
            'name': 'FILTTEST Confirmed Orders Copy',
            'model_id': 'sale.order',
            'domain': "[('state', '=', 'sale')]",
            'context': '{}',
            'sort': '[]',
            'user_ids': [(6, 0, [self.env.user.id])],
        })
        duplicates = self.service.find_duplicates(self.filter_rec)
        self.assertIn(duplicate, duplicates)

    def test_export_import(self):
        payload = self.service.export_filters(self.filter_rec)
        self.assertIn('filters', payload)
        self.assertEqual(payload['filters'][0]['name'], self.filter_rec.name)
        imported = self.service.import_filters(payload, mode='merge')
        self.assertTrue(imported)

    def test_pin_suggestions(self):
        for _ in range(6):
            self.service.log_filter_usage(self.filter_rec, source='manager')
        suggestions = self.service.suggest_pin()
        self.assertTrue(any(item['filter_id'] == self.filter_rec.id for item in suggestions))

    def test_folder_open_action(self):
        action = self.folder_sales.action_open_filters()
        self.assertEqual(action['res_model'], 'ir.filters')


@tagged('post_install', '-at_install', 'rn_filter_manager')
class TestRnFilterManagerHttp(HttpCase):

    def test_health_route(self):
        self.authenticate('admin', 'admin')
        response = self.url_open('/rn/filter/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'ok')

    def test_suggestions_route(self):
        self.authenticate('admin', 'admin')
        response = self.url_open('/rn/filter/suggestions')
        self.assertEqual(response.status_code, 200)
        self.assertIn('suggestions', response.json())
