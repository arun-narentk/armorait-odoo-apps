# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_bookmarks')
class TestRnBookmarks(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['rn.bookmark.service']
        cls.folder_sales = cls.env['rn.bookmark.folder'].create({
            'name': 'Test Sales Folder',
            'color': 'green',
        })
        cls.partner = cls.env['res.partner'].create({'name': 'BMTEST Partner'})
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
        })

    def test_toggle_record_bookmark(self):
        result = self.service.toggle_record_bookmark(self.partner)
        self.assertTrue(result['bookmarked'])
        self.assertTrue(self.partner.rn_is_bookmarked)
        result = self.service.toggle_record_bookmark(self.partner)
        self.assertFalse(result['bookmarked'])
        self.assertFalse(self.partner.rn_is_bookmarked)

    def test_folder_bookmark_count(self):
        self.service.toggle_record_bookmark(self.sale_order, folder_id=self.folder_sales.id)
        bookmark = self.env['rn.bookmark'].search([
            ('res_model', '=', 'sale.order'),
            ('res_id', '=', self.sale_order.id),
        ], limit=1)
        bookmark.folder_id = self.folder_sales
        self.folder_sales.invalidate_recordset()
        self.assertEqual(self.folder_sales.bookmark_count, 1)

    def test_list_bookmark_open(self):
        bookmark = self.service.create_list_bookmark(
            'BMTEST Draft Sales',
            'sale.order',
            domain=[('state', '=', 'draft')],
            folder_id=self.folder_sales.id,
        )
        action = self.service.open_bookmark(bookmark)
        self.assertEqual(action['res_model'], 'sale.order')
        self.assertEqual(action['view_mode'], 'list,form')

    def test_pin_and_favorite(self):
        self.service.toggle_record_bookmark(self.partner)
        bookmark = self.env['rn.bookmark'].search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', self.partner.id),
        ], limit=1)
        bookmark.action_pin()
        self.assertTrue(bookmark.is_pinned)
        bookmark.action_toggle_favorite()
        self.assertTrue(bookmark.is_favorite)

    def test_move_bookmark(self):
        invoices_folder = self.env['rn.bookmark.folder'].create({
            'name': 'Test Invoices Folder',
            'color': 'blue',
        })
        self.service.toggle_record_bookmark(self.sale_order, folder_id=self.folder_sales.id)
        bookmark = self.env['rn.bookmark'].search([
            ('res_model', '=', 'sale.order'),
            ('res_id', '=', self.sale_order.id),
        ], limit=1)
        self.service.move_bookmark(bookmark.id, folder_id=invoices_folder.id, sequence=1)
        bookmark.invalidate_recordset()
        self.assertEqual(bookmark.folder_id, invoices_folder)

    def test_sidebar_data(self):
        self.service.toggle_record_bookmark(self.partner, folder_id=self.folder_sales.id)
        data = self.service.get_sidebar_data()
        self.assertGreaterEqual(data['stats']['total'], 1)
        self.assertTrue(any(f['id'] == self.folder_sales.id for f in data['folders']))

    def test_dashboard_stats(self):
        self.service.toggle_record_bookmark(self.partner)
        stats = self.service.get_dashboard_stats()
        self.assertGreaterEqual(stats['total'], 1)

    def test_record_smart_button_count(self):
        self.service.toggle_record_bookmark(self.sale_order)
        self.sale_order.invalidate_recordset()
        self.assertEqual(self.sale_order.rn_bookmark_count, 1)
        action = self.sale_order.action_open_rn_bookmarks()
        self.assertEqual(action['res_model'], 'rn.bookmark')

    def test_duplicate_record_bookmark_blocked(self):
        self.service.toggle_record_bookmark(self.partner)
        with self.assertRaises(Exception):
            self.env['rn.bookmark'].create({
                'name': self.partner.display_name,
                'bookmark_type': 'record',
                'res_model': 'res.partner',
                'res_id': self.partner.id,
            })


@tagged('post_install', '-at_install', 'rn_bookmarks')
class TestRnBookmarksHttp(HttpCase):

    def test_health_route(self):
        self.authenticate('admin', 'admin')
        response = self.url_open('/rn/bookmark/health', data='{}', headers={
            'Content-Type': 'application/json',
        })
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload.get('result', {}).get('status'), 'ok')

    def test_sidebar_route(self):
        self.authenticate('admin', 'admin')
        response = self.url_open('/rn/bookmark/sidebar', data='{}', headers={
            'Content-Type': 'application/json',
        })
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('stats', payload.get('result', {}))
