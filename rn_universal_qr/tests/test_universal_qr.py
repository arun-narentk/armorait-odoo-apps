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

# -*- coding: utf-8 -*-
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install', 'rn_universal_qr')
class TestUniversalQr(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'QR Test Partner'})

    def test_qr_generate_on_partner(self):
        self.partner.action_generate_qr()
        self.assertTrue(self.partner.rn_qr_token)
        self.assertTrue(self.partner.rn_qr_image)
        self.assertIn('/rn/qr/', self.partner.rn_qr_url)

    def test_token_resolution(self):
        self.partner.action_generate_qr()
        result = self.env['rn.qr.scan.service'].resolve_token(self.partner.rn_qr_token)
        self.assertTrue(result)
        qr_record, document = result
        self.assertEqual(qr_record.res_model, 'res.partner')
        self.assertEqual(document.id, self.partner.id)
# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, HttpCase


@tagged('post_install', '-at_install', 'rn_universal_qr')
class TestRnUniversalQr(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['rn.qr.service']
        cls.scan_service = cls.env['rn.qr.scan.service']
        cls.partner = cls.env['res.partner'].create({
            'name': 'QRTEST Partner',
            'email': 'qrtest@armorait.com',
        })
        cls.user = cls.env.ref('base.user_admin')

    def test_generate_qr_on_partner(self):
        qr = self.service.get_or_create_qr('res.partner', self.partner.id)
        self.assertTrue(qr.token)
        self.assertTrue(qr.qr_image)
        self.assertEqual(qr.res_model, 'res.partner')
        self.assertEqual(qr.res_id, self.partner.id)
        self.assertIn('/rn/qr/', qr.qr_url)
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.rn_qr_count, 1)
        self.assertTrue(self.partner.rn_qr_active_id)

    def test_regenerate_changes_token(self):
        qr = self.service.get_or_create_qr('res.partner', self.partner.id)
        old_token = qr.token
        new_qr = self.service.regenerate_qr('res.partner', self.partner.id)
        self.assertNotEqual(new_qr.token, old_token)
        self.assertTrue(new_qr.qr_image)

    def test_payload_record_url(self):
        qr = self.service.get_or_create_qr('res.partner', self.partner.id, {
            'payload_type': 'record_url',
        })
        payload = self.service.build_payload(qr)
        self.assertIn(qr.token, payload)

    def test_payload_record_name(self):
        qr = self.service.get_or_create_qr('res.partner', self.partner.id, {
            'payload_type': 'record_name',
        })
        payload = self.service.build_payload(qr)
        self.assertEqual(payload, self.partner.display_name)

    def test_scan_registers_statistics(self):
        qr = self.service.get_or_create_qr('res.partner', self.partner.id)
        self.scan_service.register_scan(
            qr,
            user_agent='Test Agent',
            ip_address='127.0.0.1',
            user=self.user,
        )
        qr.invalidate_recordset()
        self.assertEqual(qr.scan_count, 1)
        self.assertTrue(qr.first_scan)
        self.assertTrue(qr.last_scan)
        self.assertEqual(len(qr.scan_log_ids), 1)

    def test_expiration_policy(self):
        qr = self.service.get_or_create_qr('res.partner', self.partner.id, {
            'expiration_policy': '30',
        })
        self.assertTrue(qr.expires_on)
        qr.write({'expires_on': fields.Datetime.now() - timedelta(days=1)})
        self.assertTrue(qr.is_expired())

    def test_bulk_zip_generation(self):
        partners = self.env['res.partner'].create([
            {'name': 'QR Bulk A'},
            {'name': 'QR Bulk B'},
        ])
        action = self.service.bulk_generate_zip('res.partner', partners.ids)
        self.assertEqual(action['type'], 'ir.actions.act_url')
        self.assertIn('/web/content/', action['url'])

    def test_model_config_values(self):
        config = self.env['rn.qr.model.config'].search([
            ('model_name', '=', 'res.partner'),
        ], limit=1)
        self.assertTrue(config)
        values = config.get_values_for_record()
        self.assertIn('payload_type', values)
        self.assertIn('action_type', values)

    def test_download_png_action(self):
        action = self.service.download_png('res.partner', self.partner.id)
        self.assertEqual(action['type'], 'ir.actions.act_url')
        self.assertIn('download=true', action['url'])

    def test_resolve_open_record_action(self):
        qr = self.service.get_or_create_qr('res.partner', self.partner.id, {
            'action_type': 'open_record',
        })
        action = self.service.resolve_scan_action(qr)
        self.assertEqual(action['type'], 'ir.actions.act_url')
        self.assertIn('res.partner', action['url'])


@tagged('post_install', '-at_install', 'rn_universal_qr')
class TestRnUniversalQrHttp(HttpCase):

    def test_health_route(self):
        response = self.url_open('/rn/qr/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'ok')

    def test_scan_redirect(self):
        partner = self.env['res.partner'].create({'name': 'QR HTTP Partner'})
        qr = self.env['rn.qr.service'].get_or_create_qr('res.partner', partner.id)
        response = self.url_open('/rn/qr/%s' % qr.token, allow_redirects=False)
        self.assertIn(response.status_code, (301, 302, 303))
