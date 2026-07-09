# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnAiDocumentGenerator(TransactionCase):

    def test_groups_exist(self):
        group = self.env.ref('rn_ai_document_generator.group_rn_ai_doc_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_placeholder_render(self):
        html = self.env['rn.ai.document.placeholder.service'].render(
            'Hello {{customer_name}} from {{company_name}}',
            {'customer_name': 'Ada', 'company_name': 'ARMORA'},
        )
        self.assertEqual(html, 'Hello Ada from ARMORA')

    def test_generate_document_flow(self):
        doc_type = self.env['rn.ai.document.type'].create({
            'name': 'Test Type',
            'code': 'test_type',
            'category': 'sales',
        })
        template = self.env['rn.ai.document.template'].create({
            'name': 'Test TPL',
            'type_id': doc_type.id,
            'body_html': '<p>{{customer_name}} {{ai_introduction}}</p>',
            'style': 'formal',
            'language': 'en',
        })
        partner = self.env['res.partner'].create({'name': 'Demo Customer'})
        document = self.env['rn.ai.document'].create({
            'type_id': doc_type.id,
            'template_id': template.id,
            'partner_id': partner.id,
            'subject': 'Test Doc',
        })
        self.env['rn.ai.document.render.service'].generate_documents(document)
        self.assertEqual(document.state, 'generated')
        self.assertIn('Demo Customer', document.body_html or '')
        self.assertTrue(document.version_ids)

    def test_dashboard(self):
        data = self.env['rn.ai.document.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
