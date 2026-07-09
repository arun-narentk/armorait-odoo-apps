# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnAiInvoiceOcr(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Demo Supplier OCR',
            'supplier_rank': 1,
            'vat': '29AAAAA0000A1Z5',
        })
        cls.settings = cls.env['rn.ai.invoice.ocr.settings'].create({
            'name': 'Test OCR Settings',
            'company_id': cls.env.company.id,
            'credit_balance': 10,
        })

    def test_security_groups_exist(self):
        group = self.env.ref('rn_ai_invoice_ocr.group_rn_invoice_ocr_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_extraction_service_parses_gstin(self):
        text = (
            'ABC Industries Pvt Ltd\n'
            'GSTIN: 29ABCDE1234F1Z5\n'
            'Invoice No: INV-100\n'
            'Date: 01/07/2026\n'
            'Total: 1180.00\n'
        )
        data = self.env['rn.ai.invoice.extraction.service'].parse_invoice_text(text)
        self.assertEqual(data.get('gstin'), '29ABCDE1234F1Z5')
        self.assertEqual(data.get('invoice_number'), 'INV-100')

    def test_vendor_match_fuzzy(self):
        partner, confidence = self.env['rn.ai.invoice.vendor.match.service'].match_vendor(
            'Demo Supplier OCR',
            '29AAAAA0000A1Z5',
            company_id=self.env.company.id,
        )
        self.assertEqual(partner, self.partner)
        self.assertGreaterEqual(confidence, 80.0)

    def test_duplicate_detection(self):
        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        self.assertTrue(journal)
        move = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.partner.id,
            'journal_id': journal.id,
            'ref': 'INV-DUP-1',
        })
        dup = self.env['rn.ai.invoice.duplicate.service'].find_duplicate(
            self.partner.id,
            'INV-DUP-1',
            company_id=self.env.company.id,
        )
        self.assertEqual(dup.id, move.id)

    def test_dashboard_payload(self):
        data = self.env['rn.ai.invoice.ocr.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('total_scans', data['cards'])

    def test_create_vendor_bill_from_scan(self):
        attachment = self.env['ir.attachment'].create({
            'name': 'invoice.txt',
            'type': 'binary',
            'datas': b'demo',
            'mimetype': 'text/plain',
        })
        scan = self.env['rn.ai.invoice.scan'].create({
            'attachment_id': attachment.id,
            'partner_id': self.partner.id,
            'invoice_number': 'INV-BILL-1',
            'invoice_date': '2026-07-01',
            'amount_total': 500.0,
            'state': 'approved',
        })
        self.env['rn.ai.invoice.scan.line'].create({
            'scan_id': scan.id,
            'description': 'Consulting',
            'quantity': 1,
            'price_unit': 500.0,
        })
        move = self.env['rn.ai.invoice.bill.service'].create_vendor_bill(scan)
        self.assertEqual(move.move_type, 'in_invoice')
        self.assertEqual(move.partner_id, self.partner)
        self.assertEqual(move.ref, 'INV-BILL-1')
