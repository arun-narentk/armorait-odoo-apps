# -*- coding: utf-8 -*-
"""Tests that validate demo data used for marketplace captures."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_attachment_preview')
class TestRnAttachmentPreviewCaptureData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['rn.attachment.preview.service']
        cls.order = cls.env.ref('rn_attachment_preview.demo_rn_preview_sale_order', raise_if_not_found=False)
        cls.env.user.group_ids = [
            (4, cls.env.ref('rn_attachment_preview.group_rn_attachment_preview_manager').id),
        ]

    def test_demo_sale_order_has_attachments(self):
        if not self.order:
            self.skipTest('Demo sale order not loaded')
        payload = self.service.get_record_attachments('sale.order', self.order.id)
        self.assertGreaterEqual(len(payload), 2)
        types = {row['preview_type'] for row in payload}
        self.assertIn('image', types)
        self.assertIn('text', types)

    def test_demo_image_previewable(self):
        if not self.order:
            self.skipTest('Demo sale order not loaded')
        image = self.env.ref('rn_attachment_preview.demo_rn_preview_image', raise_if_not_found=False)
        self.assertTrue(image)
        data = self.service.attachment_to_dict(image)
        self.assertTrue(data['hover_preview'])

    def test_sale_order_form_view_exists(self):
        view = self.env.ref('rn_attachment_preview.view_order_form_attachment_preview', raise_if_not_found=False)
        self.assertTrue(view)
        self.assertEqual(view.model, 'sale.order')

    def test_gallery_action_from_demo_order(self):
        if not self.order:
            self.skipTest('Demo sale order not loaded')
        action = self.order.action_open_attachment_gallery()
        self.assertEqual(action['view_mode'], 'kanban,list,form')

    def test_default_demo_partner(self):
        partner = self.env.ref('rn_attachment_preview.demo_rn_preview_partner', raise_if_not_found=False)
        self.assertTrue(partner)
        self.assertEqual(partner.email, 'preview.demo@armorait.com')
