# -*- coding: utf-8 -*-

import base64

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_attachment_preview')
class TestRnAttachmentPreview(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['rn.attachment.preview.service']
        cls.partner = cls.env['res.partner'].create({
            'name': 'Preview Test Customer',
            'email': 'preview@test.armora.com',
        })
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
        })
        cls.image_att = cls.env['ir.attachment'].create({
            'name': 'test-image.png',
            'res_model': 'sale.order',
            'res_id': cls.order.id,
            'type': 'binary',
            'mimetype': 'image/png',
            'datas': base64.b64encode(b'fake-png'),
        })
        cls.text_att = cls.env['ir.attachment'].create({
            'name': 'notes.txt',
            'res_model': 'sale.order',
            'res_id': cls.order.id,
            'type': 'binary',
            'mimetype': 'text/plain',
            'datas': base64.b64encode(b'GST Number: 29ABCDE1234F1Z5'),
        })
        cls.env.user.group_ids = [
            (4, cls.env.ref('rn_attachment_preview.group_rn_attachment_preview_user').id),
        ]

    def test_image_attachment_is_previewable(self):
        data = self.service.attachment_to_dict(self.image_att)
        self.assertTrue(data['is_previewable'])
        self.assertEqual(data['preview_type'], 'image')
        self.assertTrue(data['image_url'])

    def test_text_attachment_previewable(self):
        data = self.service.attachment_to_dict(self.text_att)
        self.assertTrue(data['is_previewable'])
        self.assertEqual(data['preview_type'], 'text')

    def test_get_record_attachments(self):
        payload = self.service.get_record_attachments('sale.order', self.order.id)
        self.assertGreaterEqual(len(payload), 2)
        names = {row['name'] for row in payload}
        self.assertIn('test-image.png', names)

    def test_text_preview_content(self):
        preview = self.service.get_text_preview(self.text_att.id)
        self.assertIn('GST Number', preview['text'])

    def test_mixin_attachment_count(self):
        self.order._compute_rn_attachment_count()
        self.assertGreaterEqual(self.order.rn_attachment_count, 2)

    def test_mixin_preview_data(self):
        data = self.order.get_rn_attachment_preview_data()
        self.assertGreaterEqual(len(data), 2)

    def test_attachment_model_preview_flags(self):
        self.image_att._compute_rn_preview_meta()
        self.assertTrue(self.image_att.rn_is_previewable)
        self.assertEqual(self.image_att.rn_preview_type, 'image')

    def test_security_groups_exist(self):
        self.assertTrue(self.env.ref('rn_attachment_preview.group_rn_attachment_preview_user'))
        self.assertTrue(self.env.ref('rn_attachment_preview.group_rn_attachment_preview_manager'))

    def test_gallery_action(self):
        action = self.order.action_open_attachment_gallery()
        self.assertEqual(action['res_model'], 'ir.attachment')
        self.assertIn(('res_model', '=', 'sale.order'), action['domain'])
