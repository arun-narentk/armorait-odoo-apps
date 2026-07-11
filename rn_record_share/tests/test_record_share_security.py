# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_record_share')
class TestRnRecordShareSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = cls.env['res.users'].create({
            'name': 'Share User A',
            'login': 'share_user_a',
            'email': 'share_user_a@armorait.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('rn_record_share.group_rn_record_share_user').id,
            ])],
        })
        cls.user_b = cls.env['res.users'].create({
            'name': 'Share User B',
            'login': 'share_user_b',
            'email': 'share_user_b@armorait.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('rn_record_share.group_rn_record_share_user').id,
            ])],
        })
        cls.partner = cls.env['res.partner'].create({'name': 'Secure Partner'})

    def test_user_cannot_read_other_share_logs(self):
        log = self.env['rn.share.log'].with_user(self.user_a).create({
            'user_id': self.user_a.id,
            'res_model': 'res.partner',
            'res_id': self.partner.id,
            'label': 'Secure Partner',
            'action_type': 'copy',
            'format_type': 'url',
            'shared_url': 'https://example.com',
        })
        with self.assertRaises(AccessError):
            self.env['rn.share.log'].with_user(self.user_b).browse(log.id).read(['label'])

    def test_mixin_actions_callable(self):
        action = self.partner.with_user(self.user_a).action_copy_record_link()
        self.assertEqual(action['tag'], 'rn_record_share.copy_clipboard')
        wizard_action = self.partner.with_user(self.user_a).action_open_record_share()
        self.assertEqual(wizard_action['res_model'], 'rn.record.share.wizard')
