# -*- coding: utf-8 -*-

import base64
import io
import zipfile

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


def _build_min_docx(text: str) -> bytes:
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body><w:p><w:r><w:t>'
        f'{text}'
        '</w:t></w:r></w:p></w:body></w:document>'
    ).encode('utf-8')
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('word/document.xml', document_xml)
    return buffer.getvalue()


@tagged('post_install', '-at_install', 'rn_attachment_preview')
class TestRnAttachmentPreviewV2(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.preview_service = cls.env['rn.attachment.preview.service']
        cls.thumbnail_service = cls.env['rn.attachment.thumbnail.service']
        cls.ocr_service = cls.env['rn.attachment.ocr.service']
        cls.office_service = cls.env['rn.attachment.office.service']
        cls.annotation_service = cls.env['rn.attachment.annotation.service']
        cls.partner = cls.env['res.partner'].create({'name': 'V2 Preview Customer'})
        cls.order = cls.env['sale.order'].create({'partner_id': cls.partner.id})
        cls.text_att = cls.env['ir.attachment'].create({
            'name': 'contract-notes.txt',
            'res_model': 'sale.order',
            'res_id': cls.order.id,
            'type': 'binary',
            'mimetype': 'text/plain',
            'datas': base64.b64encode(b'Unique OCR phrase ZEBRA-77881 for search'),
        })
        cls.docx_att = cls.env['ir.attachment'].create({
            'name': 'scope.docx',
            'res_model': 'sale.order',
            'res_id': cls.order.id,
            'type': 'binary',
            'mimetype': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'datas': base64.b64encode(_build_min_docx('Office preview paragraph ZEBRA-77881')),
        })
        cls.pdf_att = cls.env['ir.attachment'].create({
            'name': 'quote.pdf',
            'res_model': 'sale.order',
            'res_id': cls.order.id,
            'type': 'binary',
            'mimetype': 'application/pdf',
            'datas': base64.b64encode(b'%PDF-1.4 fake pdf placeholder'),
        })

    def test_attachment_states_default_pending(self):
        self.assertEqual(self.text_att.rn_ocr_state, 'pending')
        self.assertEqual(self.text_att.rn_thumbnail_state, 'skipped')

    def test_ocr_extract_and_search(self):
        self.ocr_service.process_attachment(self.text_att)
        self.assertEqual(self.text_att.rn_ocr_state, 'done')
        self.assertIn('ZEBRA-77881', self.text_att.rn_ocr_text)
        results = self.ocr_service.search_attachments('ZEBRA-77881')
        self.assertTrue(any(row['id'] == self.text_att.id for row in results))

    def test_office_preview_generation(self):
        self.office_service.process_attachment(self.docx_att)
        self.assertIn('Office preview paragraph', self.docx_att.rn_office_preview_html)
        payload = self.preview_service.get_office_preview(self.docx_att.id)
        self.assertIn('Word Preview', payload['html'])

    def test_office_attachment_previewable(self):
        data = self.preview_service.attachment_to_dict(self.docx_att)
        self.assertTrue(data['is_previewable'])
        self.assertEqual(data['preview_type'], 'office')

    def test_thumbnail_generation_for_docx(self):
        self.thumbnail_service.generate_thumbnail(self.docx_att)
        self.assertEqual(self.docx_att.rn_thumbnail_state, 'done')
        self.assertTrue(self.docx_att.rn_preview_thumbnail)

    def test_pdf_annotation_lifecycle(self):
        created = self.annotation_service.create_annotation(self.pdf_att.id, {
            'note': 'Approve total on page 2',
            'page_number': 2,
        })
        self.assertEqual(created['page_number'], 2)
        rows = self.annotation_service.list_for_attachment(self.pdf_att.id)
        self.assertEqual(len(rows), 1)
        payload = self.preview_service.attachment_to_dict(self.pdf_att)
        self.assertEqual(payload['annotation_count'], 1)
        self.annotation_service.delete_annotation(created['id'])
        self.assertEqual(len(self.annotation_service.list_for_attachment(self.pdf_att.id)), 0)

    def test_pdf_annotation_rejects_non_pdf(self):
        with self.assertRaises(Exception):
            self.annotation_service.create_annotation(self.text_att.id, {'note': 'Nope'})

    def test_thumbnail_cron_batch(self):
        pending = self.env['ir.attachment'].search_count([('rn_thumbnail_state', '=', 'pending')])
        processed = self.thumbnail_service.cron_generate_batch(limit=5)
        self.assertGreaterEqual(pending, 0)
        self.assertGreaterEqual(processed, 0)

    def test_ocr_cron_batch(self):
        processed = self.ocr_service.cron_extract_batch(limit=5)
        self.assertGreaterEqual(processed, 0)

    def test_search_wizard_action(self):
        self.ocr_service.process_attachment(self.text_att)
        wizard = self.env['rn.attachment.search.wizard'].create({'query': 'ZEBRA-77881'})
        action = wizard.action_search()
        self.assertEqual(action['res_model'], 'ir.attachment')
