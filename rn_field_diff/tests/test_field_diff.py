# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnFieldDiff(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'FIELDDIFF Partner A',
            'email': 'fielddiff.test.a@armorait.com',
        })
        cls.partner_b = cls.env['res.partner'].create({
            'name': 'FIELDDIFF Partner B',
            'email': 'fielddiff.test.b@armorait.com',
        })
        cls.product = cls.env['product.product'].search([('sale_ok', '=', True)], limit=1)
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner_a.id,
            'order_line': [(0, 0, {'product_id': cls.product.id, 'product_uom_qty': 1})],
        })
        cls.env.flush_all()
        cls.cr.flush()

    def _flush_tracking(self):
        self.env.flush_all()
        self.cr.flush()

    def test_partner_change_creates_field_diff(self):
        self.order.write({'partner_id': self.partner_b.id})
        self._flush_tracking()
        diffs = self.env['rn.field.diff'].search([
            ('model', '=', 'sale.order'),
            ('res_id', '=', self.order.id),
            ('field_name', '=', 'partner_id'),
        ])
        self.assertTrue(diffs)
        diff = diffs[0]
        self.assertIn('FIELDDIFF Partner A', diff.old_value_display)
        self.assertIn('FIELDDIFF Partner B', diff.new_value_display)
        self.assertEqual(diff.change_category, 'modified')

    def test_numeric_revenue_diff_on_crm_lead(self):
        lead = self.env['crm.lead'].create({
            'name': 'FIELDDIFF Lead',
            'type': 'opportunity',
            'expected_revenue': 1000.0,
        })
        lead.write({'expected_revenue': 1800.0})
        self._flush_tracking()
        diff = self.env['rn.field.diff'].search([
            ('model', '=', 'crm.lead'),
            ('res_id', '=', lead.id),
            ('field_name', '=', 'expected_revenue'),
        ], limit=1)
        self.assertTrue(diff)
        self.assertEqual(diff.filter_category, 'numeric')
        self.assertIn('800', diff.difference_display.replace(',', ''))

    def test_field_diff_count_on_sale_order(self):
        self.order.write({'partner_id': self.partner_b.id})
        self._flush_tracking()
        self.order.invalidate_recordset(['field_diff_count'])
        self.assertGreaterEqual(self.order.field_diff_count, 1)

    def test_history_action_domain(self):
        self.order.write({'partner_id': self.partner_b.id})
        self._flush_tracking()
        action = self.order.action_view_field_diff_history()
        self.assertEqual(action['res_model'], 'rn.field.diff')
        self.assertIn(('model', '=', 'sale.order'), action['domain'])
        self.assertIn(('res_id', '=', self.order.id), action['domain'])

    def test_diff_summary_service(self):
        self.order.write({'partner_id': self.partner_b.id})
        self._flush_tracking()
        summary = self.env['rn.field.diff.service'].get_summary('sale.order', self.order.id)
        self.assertGreaterEqual(summary['total'], 1)

    def test_web_payload_shape(self):
        self.order.write({'partner_id': self.partner_b.id})
        self._flush_tracking()
        payload = self.env['rn.field.diff.service'].get_diffs_for_web('sale.order', self.order.id)
        self.assertTrue(payload)
        self.assertIn('old_value', payload[0])
        self.assertIn('new_value', payload[0])
        self.assertIn('color_class', payload[0])

    def test_csv_export(self):
        self.order.write({'partner_id': self.partner_b.id})
        self._flush_tracking()
        diffs = self.env['rn.field.diff'].search([
            ('model', '=', 'sale.order'),
            ('res_id', '=', self.order.id),
        ])
        content = self.env['rn.field.diff.service'].export_csv(diffs.ids)
        self.assertIn(b'Before', content)
        self.assertIn(b'FIELDDIFF', content)

    def test_security_groups_exist(self):
        group = self.env.ref('rn_field_diff.group_rn_field_diff_manager', raise_if_not_found=False)
        self.assertTrue(group)
