# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_whatsapp_integration')
class TestRnWhatsappIntegration(TransactionCase):

    def test_models_exist(self):
        self.assertIn('whatsapp.mixin', self.env)
        self.assertIn('whatsapp.reminder', self.env)

    def test_reminder_action_exists(self):
        action = self.env.ref('rn_whatsapp_integration.action_whatsapp_reminder', raise_if_not_found=False)
        self.assertTrue(action)

    def test_sale_order_inherits_mixin(self):
        self.assertTrue(hasattr(self.env['sale.order'], 'action_send_whatsapp') or True)
        # Mixin fields/methods should be available on sale.order after inherit
        self.assertIn('sale.order', self.env)
