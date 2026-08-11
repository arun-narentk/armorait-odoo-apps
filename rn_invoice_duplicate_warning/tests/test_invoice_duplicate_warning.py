# -*- coding: utf-8 -*-
"""Tests for Invoice Duplicate Number Warning."""

from odoo import fields
from odoo.addons.rn_invoice_duplicate_warning.models.constants import (
    CTX_SKIP_CHECK,
    PARAM_BLOCK,
    PARAM_CASE_INSENSITIVE,
    PARAM_ENABLE,
)
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_invoice_duplicate_warning')
class TestInvoiceDuplicateWarning(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ICP = cls.env['ir.config_parameter'].sudo()
        ICP.set_param(PARAM_ENABLE, 'True')
        ICP.set_param(PARAM_BLOCK, 'False')
        ICP.set_param(PARAM_CASE_INSENSITIVE, 'True')

        cls.company = cls.env.company
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'Vendor A DupWarn',
            'company_id': False,
        })
        cls.partner_b = cls.env['res.partner'].create({
            'name': 'Vendor B DupWarn',
            'company_id': False,
        })
        cls.expense_account = cls.env['account.account'].search([
            ('account_type', '=', 'expense'),
            ('company_ids', 'in', cls.company.id),
        ], limit=1)
        if not cls.expense_account:
            cls.expense_account = cls.env['account.account'].search([
                ('account_type', '=', 'expense'),
            ], limit=1)
        cls.purchase_journal = cls.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', cls.company.id),
        ], limit=1)

    def _set_params(self, enable='True', block='False', case_insensitive='True'):
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param(PARAM_ENABLE, enable)
        ICP.set_param(PARAM_BLOCK, block)
        ICP.set_param(PARAM_CASE_INSENSITIVE, case_insensitive)

    def _make_bill(self, ref, partner=None, post=False, company=None, move_type='in_invoice'):
        company = company or self.company
        partner = partner or self.partner_a
        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase' if move_type.startswith('in_') else 'sale'),
            ('company_id', '=', company.id),
        ], limit=1)
        account = self.env['account.account'].search([
            ('account_type', '=', 'expense' if move_type.startswith('in_') else 'income'),
            ('company_ids', 'in', company.id),
        ], limit=1) or self.expense_account

        self.assertTrue(journal, 'Purchase/sale journal is required for tests')
        self.assertTrue(account, 'Expense/income account is required for tests')

        bill = self.env['account.move'].with_company(company).create({
            'move_type': move_type,
            'partner_id': partner.id,
            'company_id': company.id,
            'journal_id': journal.id,
            'invoice_date': fields.Date.from_string('2026-01-15'),
            'ref': ref,
            'invoice_line_ids': [(0, 0, {
                'name': 'DupWarn line',
                'quantity': 1,
                'price_unit': 100.0,
                'account_id': account.id,
            })],
        })
        if post:
            bill.with_context(**{CTX_SKIP_CHECK: True}).action_post()
        return bill

    def test_no_duplicate_posts_successfully(self):
        bill = self._make_bill('UNIQUE-REF-001')
        result = bill.action_post()
        self.assertFalse(result)
        self.assertEqual(bill.state, 'posted')

    def test_same_vendor_same_ref_detected(self):
        first = self._make_bill('DUP-100', post=True)
        second = self._make_bill('DUP-100')
        duplicates = second._rn_find_duplicate_vendor_bills()
        self.assertIn(first, duplicates)
        action = second.action_post()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'rn.invoice.duplicate.warning.wizard')
        self.assertEqual(second.state, 'draft')

    def test_different_vendor_same_ref_allowed(self):
        self._make_bill('VENDOR-SHARED', partner=self.partner_a, post=True)
        second = self._make_bill('VENDOR-SHARED', partner=self.partner_b)
        self.assertFalse(second._rn_find_duplicate_vendor_bills())
        second.action_post()
        self.assertEqual(second.state, 'posted')

    def test_different_company_same_ref_allowed(self):
        other_company = self.env['res.company'].search([
            ('id', '!=', self.company.id),
        ], limit=1)
        if not other_company:
            self.skipTest('Need a second company already present in the database')
        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', other_company.id),
        ], limit=1)
        if not journal:
            self.skipTest('Second company has no purchase journal')
        self._make_bill('CO-SHARED', post=True, company=self.company)
        second = self._make_bill('CO-SHARED', company=other_company)
        self.assertFalse(second._rn_find_duplicate_vendor_bills())

    def test_empty_ref_skipped(self):
        self._make_bill(False, post=True)
        second = self._make_bill(False)
        self.assertFalse(second._rn_find_duplicate_vendor_bills())
        second.action_post()
        self.assertEqual(second.state, 'posted')

    def test_whitespace_normalized(self):
        first = self._make_bill('INV-1001', post=True)
        second = self._make_bill('  INV-1001  ')
        self.assertIn(first, second._rn_find_duplicate_vendor_bills())

    def test_case_insensitive_when_enabled(self):
        first = self._make_bill('INV-CASE', post=True)
        second = self._make_bill('inv-case')
        self.assertIn(first, second._rn_find_duplicate_vendor_bills())

    def test_case_sensitive_when_disabled(self):
        self._set_params(case_insensitive='False')
        self._make_bill('INV-CASE-2', post=True)
        second = self._make_bill('inv-case-2')
        self.assertFalse(second._rn_find_duplicate_vendor_bills())

    def test_existing_draft_detected(self):
        first = self._make_bill('DRAFT-DUP')
        second = self._make_bill('DRAFT-DUP')
        duplicates = second._rn_find_duplicate_vendor_bills()
        self.assertIn(first, duplicates)
        self.assertEqual(first.state, 'draft')

    def test_block_mode_prevents_continue(self):
        self._set_params(block='True')
        self._make_bill('BLOCK-100', post=True)
        second = self._make_bill('BLOCK-100')
        action = second.action_post()
        wizard = self.env['rn.invoice.duplicate.warning.wizard'].browse(action['res_id'])
        self.assertTrue(wizard.block_mode)
        wizard.action_continue_anyway()
        self.assertEqual(second.state, 'draft')

    def test_warning_mode_continue_posts(self):
        self._set_params(block='False')
        self._make_bill('WARN-100', post=True)
        second = self._make_bill('WARN-100')
        action = second.action_post()
        wizard = self.env['rn.invoice.duplicate.warning.wizard'].browse(action['res_id'])
        self.assertFalse(wizard.block_mode)
        wizard.action_continue_anyway()
        self.assertEqual(second.state, 'posted')

    def test_customer_invoice_unaffected(self):
        first = self._make_bill('CUST-REF', move_type='out_invoice', post=True)
        second = self._make_bill('CUST-REF', move_type='out_invoice')
        self.assertFalse(second._rn_find_duplicate_vendor_bills())
        second.action_post()
        self.assertEqual(second.state, 'posted')
        self.assertEqual(first.move_type, 'out_invoice')

    def test_vendor_credit_note_excluded(self):
        bill = self._make_bill('CN-REF', post=True)
        refund = self._make_bill('CN-REF', move_type='in_refund')
        self.assertFalse(refund._rn_find_duplicate_vendor_bills())
        self.assertNotIn(bill, refund._rn_find_duplicate_vendor_bills())

    def test_current_record_excluded(self):
        bill = self._make_bill('SELF-REF', post=True)
        self.assertFalse(bill._rn_find_duplicate_vendor_bills())

    def test_disabled_feature_posts_without_wizard(self):
        self._set_params(enable='False')
        self._make_bill('OFF-100', post=True)
        second = self._make_bill('OFF-100')
        result = second.action_post()
        self.assertFalse(result)
        self.assertEqual(second.state, 'posted')

    def test_skip_context_bypasses_check(self):
        self._make_bill('SKIP-100', post=True)
        second = self._make_bill('SKIP-100')
        second.with_context(**{CTX_SKIP_CHECK: True}).action_post()
        self.assertEqual(second.state, 'posted')

    def test_commercial_partner_shared_contacts(self):
        parent = self.partner_a
        contact = self.env['res.partner'].create({
            'name': 'Vendor Contact DupWarn',
            'parent_id': parent.id,
            'type': 'invoice',
        })
        self._make_bill('COMM-100', partner=parent, post=True)
        second = self._make_bill('COMM-100', partner=contact)
        self.assertTrue(second._rn_find_duplicate_vendor_bills())
