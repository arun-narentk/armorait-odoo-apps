# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnRestaurantCore(TransactionCase):

    def test_groups_exist(self):
        group = self.env.ref('rn_restaurant_core.group_rn_restaurant_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_dashboard_payload(self):
        data = self.env['rn.restaurant.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('branches', data['cards'])

    def test_setup_and_pricing(self):
        wizard = self.env['rn.restaurant.setup.wizard'].create({
            'name': 'Test Bakery',
            'cuisine_type': 'bakery',
            'branch_name': 'Counter 1',
            'table_count': 3,
            'create_defaults': True,
        })
        action = wizard.action_setup()
        restaurant = self.env['rn.restaurant'].browse(action['res_id'])
        self.assertTrue(restaurant.payment_method_ids)
        self.assertTrue(restaurant.tax_ids)
        self.assertEqual(len(restaurant.branch_ids.table_ids), 3)
        category = self.env['rn.restaurant.menu.category'].create({
            'name': 'Breads',
            'restaurant_id': restaurant.id,
        })
        item = self.env['rn.restaurant.menu.item'].create({
            'name': 'Croissant',
            'restaurant_id': restaurant.id,
            'category_id': category.id,
            'list_price': 50,
            'tax_ids': [(6, 0, restaurant.tax_ids.ids)],
        })
        price = self.env['rn.restaurant.menu.service'].compute_price_with_tax(item, qty=2)
        self.assertGreater(price['total'], price['untaxed'])
