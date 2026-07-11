# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnTimelineExport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Export Partner'})

    def _assert_report_action(self, action):
        if action.get('type') == 'ir.actions.act_window':
            report = action.get('context', {}).get('report_action', {})
            self.assertEqual(report.get('type'), 'ir.actions.report')
            self.assertIn('report_name', report)
            return
        self.assertEqual(action.get('type'), 'ir.actions.report')
        self.assertIn('report_name', action)

    def test_sale_order_pdf_action(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        self._assert_report_action(order.action_export_timeline_pdf())

    def test_purchase_order_pdf_action(self):
        vendor = self.env['res.partner'].create({'name': 'Export Vendor', 'supplier_rank': 1})
        po = self.env['purchase.order'].create({'partner_id': vendor.id})
        self._assert_report_action(self.env['rn.timeline.service'].export_timeline_pdf_action(po))

    def test_crm_lead_pdf_action(self):
        lead = self.env['crm.lead'].create({'name': 'Export CRM Lead'})
        self._assert_report_action(self.env['rn.timeline.service'].export_timeline_pdf_action(lead))

    def test_demo_timeline_events_on_sale_order(self):
        demo_order = self.env.ref('sale.sale_order_1', raise_if_not_found=False)
        if not demo_order:
            self.skipTest('sale demo order not loaded')
        events = self.env['rn.timeline.event'].search([
            ('model', '=', 'sale.order'),
            ('record_id', '=', demo_order.id),
        ])
        labels = events.mapped('name')
        self.assertIn('Payment Registered', labels)
        self.assertIn('Delivered', labels)
