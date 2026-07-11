# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_smart_notes')
class TestRnSmartNotes(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.user
        cls.manager = cls.env.ref('base.user_admin')
        cls.partner = cls.env['res.partner'].create({
            'name': 'SMARTNOTE Test Partner',
        })
        cls.template = cls.env['rn.smart.note.template'].create({
            'name': 'Test VIP Template',
            'description': '<p>VIP handling required.</p>',
            'color': 'green',
            'priority': 'high',
            'icon': 'vip',
            'is_quick': True,
        })
        cls.service = cls.env['rn.smart.note.service']

    def test_add_note_on_partner(self):
        payload = self.service.add_note('res.partner', self.partner.id, {
            'name': 'Payment delay warning',
            'note': '<p>Customer often delays payment.</p>',
            'color': 'orange',
            'priority': 'critical',
            'icon': 'warning',
            'is_pinned': True,
        })
        self.assertEqual(payload['name'], 'Payment delay warning')
        note = self.env['rn.smart.note'].browse(payload['id'])
        self.assertTrue(note.exists())
        self.assertEqual(note.res_model, 'res.partner')
        self.assertEqual(note.res_id, self.partner.id)
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.smart_note_count, 1)
        self.assertEqual(self.partner.smart_note_pinned_count, 1)

    def test_template_quick_add(self):
        payload = self.service.add_note('res.partner', self.partner.id, {
            'template_id': self.template.id,
        })
        note = self.env['rn.smart.note'].browse(payload['id'])
        self.assertEqual(note.name, 'Test VIP Template')
        self.assertEqual(note.icon, 'vip')
        self.assertEqual(note.template_id, self.template)

    def test_pin_and_panel_data(self):
        note = self.env['rn.smart.note'].create({
            'name': 'Call before delivery',
            'note': '<p>Call warehouse before dispatch.</p>',
            'res_model': 'res.partner',
            'res_id': self.partner.id,
            'color': 'blue',
            'priority': 'high',
            'icon': 'call',
            'company_id': self.env.company.id,
        })
        panel = self.env['rn.smart.note'].get_panel_data('res.partner', self.partner.id)
        self.assertEqual(len(panel['notes']), 1)
        self.assertEqual(panel['notes'][0]['id'], note.id)
        note.action_toggle_pin()
        panel = self.env['rn.smart.note'].get_panel_data('res.partner', self.partner.id)
        self.assertTrue(panel['notes'][0]['is_pinned'])

    def test_private_note_visibility(self):
        private_note = self.env['rn.smart.note'].create({
            'name': 'Private note',
            'res_model': 'res.partner',
            'res_id': self.partner.id,
            'visibility': 'only_me',
            'user_id': self.user.id,
            'company_id': self.env.company.id,
        })
        other_user = self.env['res.users'].create({
            'name': 'Other Smart Notes User',
            'login': 'smartnotes_other@test.armora',
            'email': 'smartnotes_other@test.armora',
            'group_ids': [(4, self.env.ref('rn_smart_notes.group_rn_smart_notes_user').id)],
        })
        visible = self.env['rn.smart.note'].with_user(other_user).search([
            ('id', '=', private_note.id),
        ])
        self.assertFalse(visible)
        own_visible = self.env['rn.smart.note'].with_user(self.user).search([
            ('id', '=', private_note.id),
        ])
        self.assertTrue(own_visible)

    def test_reminder_creates_activity(self):
        reminder_dt = fields.Datetime.now() + timedelta(days=1)
        note = self.env['rn.smart.note'].create({
            'name': 'Call customer tomorrow',
            'res_model': 'res.partner',
            'res_id': self.partner.id,
            'reminder_date': reminder_dt,
            'company_id': self.env.company.id,
        })
        self.assertTrue(note.reminder_activity_id)
        self.assertEqual(note.reminder_activity_id.summary, 'Call customer tomorrow')

    def test_mention_notification(self):
        colleague = self.env['res.users'].create({
            'name': 'Mention Colleague',
            'login': 'smartnotes_mention@test.armora',
            'email': 'smartnotes_mention@test.armora',
            'group_ids': [(4, self.env.ref('rn_smart_notes.group_rn_smart_notes_user').id)],
        })
        note = self.env['rn.smart.note'].create({
            'name': 'Mention test',
            'res_model': 'res.partner',
            'res_id': self.partner.id,
            'mention_user_ids': [(6, 0, colleague.ids)],
            'company_id': self.env.company.id,
        })
        self.assertTrue(note.mention_user_ids)
        self.service.notify_mentions(note)

    def test_search_note_content(self):
        self.env['rn.smart.note'].create({
            'name': 'Late payment customer',
            'res_model': 'res.partner',
            'res_id': self.partner.id,
            'company_id': self.env.company.id,
        })
        results = self.service.search_note_content('late')
        self.assertTrue(results)
        self.assertIn('Late payment customer', results.mapped('name'))

    def test_delete_from_panel_permissions(self):
        note = self.env['rn.smart.note'].create({
            'name': 'Delete me',
            'res_model': 'res.partner',
            'res_id': self.partner.id,
            'user_id': self.user.id,
            'company_id': self.env.company.id,
        })
        self.env['rn.smart.note'].delete_from_panel(note.id)
        self.assertFalse(note.exists())

    def test_sale_order_mixin_action(self):
        if 'sale.order' not in self.env:
            self.skipTest('sale.order not available')
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        order._add_note({'name': 'VIP order', 'icon': 'vip'})
        action = order.action_view_smart_notes()
        self.assertEqual(action['res_model'], 'rn.smart.note')
        self.assertIn(('res_model', '=', 'sale.order'), action['domain'])
