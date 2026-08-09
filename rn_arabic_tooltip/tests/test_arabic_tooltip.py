# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_arabic_tooltip')
class TestRnArabicTooltip(TransactionCase):

    def test_model_exists(self):
        self.assertIn('rn.arabic.tooltip', self.env)

    def test_fallback_translation(self):
        service = self.env['rn.arabic.tooltip']
        result = service.get_arabic_label_translations(['Amount', 'Customer', 'UnknownLabelXYZ'])
        self.assertEqual(result.get('Amount'), 'المبلغ')
        self.assertEqual(result.get('Customer'), 'العميل')
        self.assertNotIn('UnknownLabelXYZ', result)
