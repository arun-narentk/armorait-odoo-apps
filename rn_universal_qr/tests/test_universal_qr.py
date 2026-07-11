# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_universal_qr')
class TestUniversalQr(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Universal QR Test Partner'})

    def test_generate_qr(self):
        self.partner.action_generate_qr()
        self.assertTrue(self.partner.rn_qr_token)
        self.assertTrue(self.partner.rn_qr_image)
        self.assertIn('/rn/qr/', self.partner.rn_qr_url)

    def test_token_resolution(self):
        self.partner.action_generate_qr()
        resolved = self.env['rn.qr.scan.service'].resolve_token(self.partner.rn_qr_token)
        self.assertTrue(resolved)
        qr_record, document = resolved
        self.assertEqual(qr_record.res_model, 'res.partner')
        self.assertEqual(document.id, self.partner.id)
