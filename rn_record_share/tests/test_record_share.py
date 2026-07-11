# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.rn_record_share import constants as const


@tagged('post_install', '-at_install', 'rn_record_share')
class TestRnRecordShare(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['rn.record.share.service']
        cls.partner = cls.env['res.partner'].create({
            'name': 'ShareCap Azure Technologies',
            'email': 'sharecap@armorait.com',
        })
        cls.product = cls.env['product.template'].create({
            'name': 'ShareCap Laptop',
            'default_code': 'SHARECAP-01',
        })

    def test_internal_url(self):
        url = self.service.get_internal_url('res.partner', self.partner.id)
        self.assertIn(f'/odoo/res.partner/{self.partner.id}', url)

    def test_format_markdown(self):
        text = self.service.format_share_text(self.partner, const.FORMAT_MARKDOWN)
        self.assertIn('ShareCap Azure Technologies', text)
        self.assertIn('](', text)

    def test_format_json(self):
        text = self.service.format_share_text(self.partner, const.FORMAT_JSON)
        self.assertIn('"model": "res.partner"', text)

    def test_copy_logs_history(self):
        action = self.service.copy_link_action(self.partner, const.FORMAT_URL)
        self.assertEqual(action['tag'], 'rn_record_share.copy_clipboard')
        log = self.env['rn.share.log'].search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', self.partner.id),
            ('action_type', '=', 'copy'),
        ], limit=1)
        self.assertTrue(log)

    def test_share_payload(self):
        payload = self.service.get_share_payload('res.partner', self.partner.id)
        self.assertEqual(payload['label'], 'ShareCap Azure Technologies')
        self.assertIn('formats', payload)

    def test_wizard_open(self):
        action = self.env['rn.record.share.wizard'].open_for_record(
            'res.partner', self.partner.id
        )
        self.assertEqual(action['res_model'], 'rn.record.share.wizard')

    def test_email_share_action(self):
        action = self.service.action_email_share('res.partner', self.partner.id)
        self.assertEqual(action['type'], 'ir.actions.act_url')
        self.assertIn('mailto:', action['url'])

    def test_whatsapp_share_action(self):
        action = self.service.action_whatsapp_share('res.partner', self.partner.id)
        self.assertIn('wa.me', action['url'])

    def test_dashboard_stats(self):
        self.service.copy_link_action(self.partner)
        stats = self.service.get_dashboard_stats()
        self.assertGreaterEqual(stats['total_logs'], 1)

    def test_cleanup_old_logs(self):
        self.service.copy_link_action(self.partner)
        log = self.env['rn.share.log'].search([], limit=1)
        self.env.cr.execute(
            "UPDATE rn_share_log SET create_date = NOW() - INTERVAL '120 days' WHERE id = %s",
            [log.id],
        )
        self.env['ir.config_parameter'].sudo().set_param('rn_record_share.log_retention_days', '30')
        self.service.cleanup_old_logs()
        self.assertFalse(log.exists())
