# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_ai_biz_promotion')
class TestAiBizPromotion(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Promotion = cls.env['ai.biz.promotion']
        cls.Benefit = cls.env['ai.biz.benefit']
        cls.promotion = cls.Promotion.create({
            'name': 'Test Promotion',
            'title': 'GST SAVINGS FOR YOUR BUSINESS TRAVELS',
            'subtitle': 'AI BIZ',
            'description': '<p>Registered businesses can save more.</p>',
            'footer_text': '<p>Explore the dedicated platform.</p>',
            'button_text': 'Explore AI BIZ',
            'button_url': '/contactus',
            'sequence': 1,
            'active': True,
            'benefit_ids': [
                (0, 0, {
                    'sequence': 10,
                    'title': 'Claim GST Credit',
                    'description': 'Save with valid GST invoices.',
                }),
                (0, 0, {
                    'sequence': 20,
                    'title': 'Corporate-Ready Fares',
                    'description': 'Business travel made simpler.',
                }),
            ],
        })

    def test_models_exist(self):
        self.assertIn('ai.biz.promotion', self.env)
        self.assertIn('ai.biz.benefit', self.env)
        self.assertIn('ai.biz.promotion.service', self.env)

    def test_active_promotion_service_order(self):
        self.Promotion.create({
            'name': 'Later Promotion',
            'title': 'Later Title',
            'sequence': 50,
            'active': True,
        })
        active = self.env['ai.biz.promotion.service'].get_active_promotion()
        self.assertTrue(active)
        self.assertEqual(active.id, self.promotion.id)

    def test_benefit_sequence_and_count(self):
        self.assertEqual(self.promotion.benefit_count, 2)
        titles = self.promotion.benefit_ids.mapped('title')
        self.assertEqual(titles[0], 'Claim GST Credit')
        self.assertEqual(titles[1], 'Corporate-Ready Fares')

    def test_open_website_action(self):
        action = self.promotion.action_open_website()
        self.assertEqual(action['type'], 'ir.actions.act_url')
        self.assertEqual(action['url'], '/ai-biz')
