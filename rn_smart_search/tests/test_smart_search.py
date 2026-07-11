# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from psycopg2 import IntegrityError


@tagged('post_install', '-at_install', 'rn_smart_search')
class TestRnSmartSearch(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['rn.smart.search.service']
        cls.partner = cls.env['res.partner'].create({'name': 'Smart Search Partner'})
        cls.env['ir.config_parameter'].sudo().set_param('rn_smart_search.remember_viewed', 'True')
        cls.env['ir.config_parameter'].sudo().set_param('rn_smart_search.remember_searches', 'True')
        cls.env['ir.config_parameter'].sudo().set_param('rn_smart_search.max_history', '100')
        cls.env['ir.config_parameter'].sudo().set_param('rn_smart_search.auto_clean_days', '90')

    def test_log_view_creates_entry(self):
        entry = self.service.log_view('res.partner', self.partner.id, self.partner.name)
        self.assertTrue(entry)
        self.assertEqual(entry.history_type, 'view')
        self.assertEqual(entry.model, 'res.partner')
        self.assertEqual(entry.record_id, self.partner.id)
        self.assertEqual(entry.label, self.partner.name)

    def test_log_view_increments_open_count(self):
        first = self.service.log_view('res.partner', self.partner.id)
        second = self.service.log_view('res.partner', self.partner.id)
        self.assertEqual(first.id, second.id)
        self.assertEqual(second.open_count, 2)

    def test_log_search_creates_entry(self):
        entry = self.service.log_search('Azure Interior', 'res.partner')
        self.assertTrue(entry)
        self.assertEqual(entry.history_type, 'search')
        self.assertEqual(entry.search_query, 'azure interior')

    def test_entry_key_unique_constraint(self):
        self.service.log_view('res.partner', self.partner.id)
        with mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError):
            self.env['rn.search.history'].create({
                'user_id': self.env.user.id,
                'history_type': 'view',
                'model': 'res.partner',
                'record_id': self.partner.id,
                'label': 'Duplicate',
                'entry_key': f'view:res.partner:{self.partner.id}',
            })

    def test_model_label_computed(self):
        entry = self.service.log_view('res.partner', self.partner.id)
        self.assertTrue(entry.model_label)

    def test_get_workspace_data(self):
        self.service.log_view('res.partner', self.partner.id)
        self.service.log_search('demo query', 'res.partner')
        payload = self.service.get_workspace_data()
        self.assertIn('favorites', payload)
        self.assertIn('recent_views', payload)
        self.assertIn('recent_searches', payload)
        self.assertTrue(payload['recent_views'])
        self.assertTrue(payload['recent_searches'])

    def test_get_command_items(self):
        self.service.log_view('res.partner', self.partner.id, 'Command Partner')
        items = self.service.get_command_items('Command')
        self.assertTrue(any(item['name'] == 'Command Partner' for item in items))

    def test_open_history_record(self):
        entry = self.service.log_view('res.partner', self.partner.id)
        action = self.service.open_history_record(entry.id)
        self.assertEqual(action['res_model'], 'res.partner')
        self.assertEqual(action['res_id'], self.partner.id)
        entry.invalidate_recordset()
        self.assertEqual(entry.open_count, 2)

    def test_remember_viewed_disabled(self):
        self.env['ir.config_parameter'].sudo().set_param('rn_smart_search.remember_viewed', 'False')
        before = self.env['rn.search.history'].search_count([])
        self.service.log_view('res.partner', self.partner.id)
        after = self.env['rn.search.history'].search_count([])
        self.assertEqual(before, after)

    def test_cleanup_stale_history(self):
        entry = self.service.log_search('old query', 'res.partner')
        entry.write({
            'last_opened': fields.Datetime.now() - timedelta(days=120),
            'is_favorite': False,
        })
        removed = self.service.cleanup_stale_history()
        self.assertGreaterEqual(removed, 1)
        self.assertFalse(entry.exists())
