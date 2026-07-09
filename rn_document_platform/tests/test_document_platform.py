# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnDocumentPlatform(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env['rn.doc.platform.settings'].create({
            'name': 'Test Doc Platform',
            'company_id': cls.env.company.id,
            'signature_credit_balance': 10,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Sign Test Customer',
            'email': 'signer@example.com',
        })

    def test_security_groups(self):
        self.assertTrue(self.env.ref('rn_document_platform.group_rn_doc_platform_user', raise_if_not_found=False))

    def test_sign_request_flow(self):
        attachment = self.env['ir.attachment'].create({
            'name': 'contract.pdf',
            'type': 'binary',
            'datas': b'%PDF-1.4 demo contract with auto-renew clause and penalty terms',
            'mimetype': 'application/pdf',
        })
        request = self.env['rn.doc.sign.request'].create({
            'attachment_id': attachment.id,
            'company_id': self.env.company.id,
        })
        self.env['rn.doc.sign.signer'].create({
            'request_id': request.id,
            'name': 'Jane Signer',
            'email': 'jane@example.com',
            'sequence': 10,
        })
        self.env['rn.doc.sign.service'].send_request(request)
        self.assertEqual(request.state, 'sent')
        self.assertTrue(request.document_hash)
        signer = request.signer_ids[:1]
        self.env['rn.doc.sign.service'].complete_signer(signer)
        self.assertEqual(request.state, 'completed')

    def test_ai_analysis(self):
        attachment = self.env['ir.attachment'].create({
            'name': 'risk.txt',
            'type': 'binary',
            'datas': b'Contract with unlimited liability and auto-renew every 12 months',
            'mimetype': 'text/plain',
        })
        request = self.env['rn.doc.sign.request'].create({
            'attachment_id': attachment.id,
            'company_id': self.env.company.id,
        })
        analysis = self.env['rn.doc.ai.analysis.service'].analyze_request(request)
        self.assertTrue(analysis.risk_flags)
        self.assertIn(analysis.risk_level, ('medium', 'high'))

    def test_dashboard(self):
        data = self.env['rn.doc.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
