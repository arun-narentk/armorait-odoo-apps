# -*- coding: utf-8 -*-

import odoo
from odoo.modules.registry import Registry
from odoo.tests import HttpCase, TransactionCase, tagged


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
        cls.product = cls.env['product.template'].create({
            'name': 'QRTEST Product',
            'list_price': 25.0,
        })

    def test_generate_qr_on_partner(self):
        self.partner.action_generate_qr()
        self.assertTrue(self.partner.rn_qr_token)
        self.assertTrue(self.partner.rn_qr_image)
        self.assertIn('/rn/qr/', self.partner.rn_qr_url)
        qr_record = self.env['rn.qr.record'].search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', self.partner.id),
        ], limit=1)
        self.assertTrue(qr_record)
        self.assertEqual(qr_record.token, self.partner.rn_qr_token)

    def test_generate_qr_on_product(self):
        product = self.env['product.product'].search([('product_tmpl_id', '=', self.product.id)], limit=1)
        product.action_generate_qr()
        self.assertTrue(product.rn_qr_token)
        self.assertTrue(product.rn_qr_image)

    def test_token_resolution(self):
        self.partner.action_generate_qr()
        resolved = self.scan_service.resolve_token(self.partner.rn_qr_token)
        self.assertTrue(resolved)
        qr_record, document = resolved
        self.assertEqual(qr_record.res_model, 'res.partner')
        self.assertEqual(document.id, self.partner.id)

    def test_scan_logging(self):
        self.partner.action_generate_qr()
        qr_record = self.env['rn.qr.record'].search([
            ('token', '=', self.partner.rn_qr_token),
        ], limit=1)
        self.scan_service.log_scan(
            qr_record,
            source='web',
            user_agent='Test Browser',
            ip_address='127.0.0.1',
        )
        qr_record = self.env['rn.qr.record'].browse(qr_record.id)
        self.assertEqual(qr_record.scan_count, 1)
        self.assertTrue(qr_record.last_scanned_at)

    def test_svg_generation(self):
        self.partner.action_generate_qr()
        svg, url = self.service.generate_svg(self.partner.rn_qr_token)
        self.assertIn('<svg', svg)
        self.assertIn('/rn/qr/', url)

    def test_bulk_zip_export(self):
        partners = self.env['res.partner'].create([
            {'name': 'QR Bulk A'},
            {'name': 'QR Bulk B'},
        ])
        payload = self.service.export_bulk_zip(partners, filename='qrtest.zip')
        self.assertEqual(payload['filename'], 'qrtest.zip')
        self.assertTrue(payload['content'])

    def test_bulk_wizard(self):
        wizard = self.env['rn.qr.bulk.generate.wizard'].create({
            'model_id': self.env.ref('base.model_res_partner').id,
            'limit': 5,
        })
        wizard.action_generate()
        self.assertTrue(wizard.zip_file)

    def test_model_config_dynamic_view(self):
        config = self.env['rn.qr.model.config'].create({
            'model_id': self.env.ref('base.model_res_partner').id,
            'show_on_form': True,
        })
        config.action_generate_form_view()
        self.assertTrue(config.generated_view_id)
        self.assertEqual(config.generated_view_id.model, 'res.partner')

    def test_template_data_loaded(self):
        template = self.env.ref('rn_universal_qr.rn_qr_template_warehouse', raise_if_not_found=False)
        self.assertTrue(template)
        self.assertEqual(template.template_type, 'warehouse')


@tagged('post_install', '-at_install', 'rn_universal_qr')
class TestRnUniversalQrHttp(HttpCase):

    def test_health_route(self):
        self.authenticate('admin', 'admin')
        response = self.url_open('/rn/qr/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'ok')

    def test_scan_redirect(self):
        self.authenticate('admin', 'admin')
        partner = self.env['res.partner'].create({'name': 'QR HTTP Partner'})
        partner.action_generate_qr()
        token = partner.rn_qr_token
        response = self.url_open('/rn/qr/%s' % token, allow_redirects=False)
        self.assertIn(response.status_code, (301, 302, 303))
        with Registry(self.env.cr.dbname).cursor() as cr:
            env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
            log_count = env['rn.qr.scan.log'].search_count([('token', '=', token)])
        self.assertGreaterEqual(log_count, 1)
