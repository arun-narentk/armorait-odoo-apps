# -*- coding: utf-8 -*-

import base64

from odoo.tests import tagged, TransactionCase


SAMPLE_INVOICE_TEXT = """
ABC Industries Pvt Ltd
GSTIN: 27AABCU9603R1ZM
Tax Invoice
Invoice No: INV-2026-1042
Date: 15-03-2026
Item A 2 x 1500.00 3000.00
Grand Total: 3540.00
"""


@tagged('post_install', '-at_install', 'rn_document_idp')
class TestDocumentIdp(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Document = cls.env['rn.document.idp.document']
        cls.Pipeline = cls.env['rn.document.idp.pipeline.service']
        cls.partner = cls.env['res.partner'].create({
            'name': 'ABC Industries Pvt Ltd',
            'vat': '27AABCU9603R1ZM',
        })
        attachment = cls.env['ir.attachment'].create({
            'name': 'sample_invoice.txt',
            'datas': base64.b64encode(SAMPLE_INVOICE_TEXT.encode('utf-8')),
            'mimetype': 'text/plain',
        })
        cls.document = cls.Document.create({
            'name': 'Test Invoice',
            'attachment_id': attachment.id,
        })

    def test_classification_detects_vendor_invoice(self):
        doc_type, confidence = self.env['rn.document.idp.classification.service'].classify(
            SAMPLE_INVOICE_TEXT
        )
        self.assertEqual(doc_type, 'vendor_invoice')
        self.assertGreater(confidence, 50)

    def test_pipeline_processes_document(self):
        self.document.action_process()
        self.assertEqual(self.document.document_type, 'vendor_invoice')
        self.assertTrue(self.document.document_number)
        self.assertTrue(self.document.validation_ids)
        self.assertGreater(self.document.overall_confidence, 0)

    def test_post_vendor_bill(self):
        self.document.action_process()
        self.document.write({
            'partner_id': self.partner.id,
            'state': 'approved',
        })
        self.document.action_post_to_erp()
        self.assertEqual(self.document.state, 'posted')
        self.assertTrue(self.document.move_id)
        self.assertEqual(self.document.move_id.move_type, 'in_invoice')

    def test_conversational_search_pending(self):
        self.document.action_process()
        results = self.env['rn.document.idp.search.service'].search_documents(
            'Which documents are pending validation?'
        )
        self.assertTrue(results)
