# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_smart_search')
class TestRnSmartSearchSecurity(TransactionCase):

    def test_security_groups_exist(self):
        user_group = self.env.ref('rn_smart_search.group_rn_smart_search_user', raise_if_not_found=False)
        manager_group = self.env.ref('rn_smart_search.group_rn_smart_search_manager', raise_if_not_found=False)
        self.assertTrue(user_group)
        self.assertTrue(manager_group)
        self.assertIn(user_group, manager_group.implied_ids)

    def test_user_can_only_see_own_history(self):
        partner = self.env['res.partner'].create({'name': 'Security Partner'})
        suffix = fields.Datetime.now().strftime('%H%M%S%f')
        other_user = self.env['res.users'].create({
            'name': 'Smart Search Other User',
            'login': f'smart_search_other_{suffix}',
            'group_ids': [(6, 0, [self.env.ref('rn_smart_search.group_rn_smart_search_user').id])],
        })
        entry = self.env['rn.search.history'].create({
            'user_id': self.env.user.id,
            'history_type': 'view',
            'model': 'res.partner',
            'record_id': partner.id,
            'label': partner.name,
            'entry_key': f'view:res.partner:{partner.id}:admin',
        })
        visible = self.env['rn.search.history'].with_user(other_user).search([
            ('id', '=', entry.id),
        ])
        self.assertFalse(visible)
        with self.assertRaises(AccessError):
            self.env['rn.search.history'].with_user(other_user).browse(entry.id).read(['label'])
