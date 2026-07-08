# -*- coding: utf-8 -*-

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install', 'ai_employee')
class TestAiEmployeeIntent(TransactionCase):

    def test_detect_overdue_invoices(self):
        Intent = self.env['ai.employee.intent']
        tool_name, args = Intent.detect('Show overdue invoices')
        self.assertEqual(tool_name, 'overdue_invoices')

    def test_detect_today_sales(self):
        Intent = self.env['ai.employee.intent']
        tool_name, _args = Intent.detect('Show today sales')
        self.assertEqual(tool_name, 'today_sales')

    def test_unknown_intent(self):
        Intent = self.env['ai.employee.intent']
        tool_name, _args = Intent.detect('xyzzy random phrase')
        self.assertFalse(tool_name)
