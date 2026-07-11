# -*- coding: utf-8 -*-
"""Tests that validate demo data and panel payloads used for live marketplace captures."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_smart_notes')
class TestRnSmartNotesCaptureData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'SMARTNOTE Demo Customer',
            'email': 'demo.capture@armorait.com',
        })
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
        })
        cls.env['rn.smart.note'].create([
            {
                'name': 'VIP Customer',
                'note': '<p>Priority account.</p>',
                'res_model': 'sale.order',
                'res_id': cls.order.id,
                'color': 'green',
                'priority': 'high',
                'icon': 'vip',
                'is_pinned': True,
                'company_id': cls.env.company.id,
            },
            {
                'name': 'Payment Delay',
                'note': '<p>Follow up before delivery.</p>',
                'res_model': 'sale.order',
                'res_id': cls.order.id,
                'color': 'orange',
                'priority': 'critical',
                'icon': 'warning',
                'is_pinned': True,
                'company_id': cls.env.company.id,
            },
        ])

    def test_demo_sale_order_has_pinned_notes(self):
        panel = self.env['rn.smart.note'].get_panel_data('sale.order', self.order.id)
        self.assertGreaterEqual(len(panel['notes']), 2)
        pinned = [n for n in panel['notes'] if n['is_pinned']]
        self.assertGreaterEqual(len(pinned), 2)
        names = {n['name'] for n in panel['notes']}
        self.assertIn('VIP Customer', names)
        self.assertIn('Payment Delay', names)

    def test_panel_includes_quick_templates(self):
        panel = self.env['rn.smart.note'].get_panel_data('sale.order', self.order.id)
        self.assertTrue(panel['templates'])
        self.assertTrue(panel['quick_templates'])

    def test_update_from_panel_returns_card_payload(self):
        note = self.env['rn.smart.note'].search([
            ('res_model', '=', 'sale.order'),
            ('res_id', '=', self.order.id),
        ], limit=1)
        payload = self.env['rn.smart.note'].update_from_panel(note.id, {
            'name': 'Updated VIP note',
            'is_pinned': True,
        })
        self.assertEqual(payload['name'], 'Updated VIP note')
        self.assertTrue(payload['is_pinned'])

    def test_notes_window_action_exists(self):
        action = self.env.ref('rn_smart_notes.action_rn_smart_note', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.smart.note')
        self.assertIn('kanban', action.view_mode)

    def test_templates_window_action_exists(self):
        action = self.env.ref('rn_smart_notes.action_rn_smart_note_template', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.smart.note.template')

    def test_default_templates_loaded(self):
        templates = self.env['rn.smart.note.template'].search([('active', '=', True)])
        self.assertGreaterEqual(len(templates), 3)
        quick = templates.filtered('is_quick')
        self.assertGreaterEqual(len(quick), 2)
