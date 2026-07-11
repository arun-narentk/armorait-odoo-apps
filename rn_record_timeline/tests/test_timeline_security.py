# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnTimelineSecurity(TransactionCase):

    def test_security_groups_exist(self):
        user_group = self.env.ref('rn_record_timeline.group_rn_timeline_user', raise_if_not_found=False)
        manager_group = self.env.ref('rn_record_timeline.group_rn_timeline_manager', raise_if_not_found=False)
        self.assertTrue(user_group)
        self.assertTrue(manager_group)
        self.assertIn(user_group, manager_group.implied_ids)

    def test_user_can_read_events_not_create(self):
        user = self.env['res.users'].create({
            'name': 'Timeline User',
            'login': 'timeline_user_test',
            'groups_id': [(6, 0, [self.env.ref('rn_record_timeline.group_rn_timeline_user').id])],
        })
        partner = self.env['res.partner'].create({'name': 'Security Partner'})
        order = self.env['sale.order'].create({'partner_id': partner.id})
        events = self.env['rn.timeline.event'].with_user(user).search([
            ('model', '=', 'sale.order'),
            ('record_id', '=', order.id),
        ])
        self.assertTrue(events)
        with self.assertRaises(AccessError):
            self.env['rn.timeline.event'].with_user(user).create({
                'name': 'Blocked',
                'model': 'sale.order',
                'record_id': order.id,
                'event_type': 'other',
            })
