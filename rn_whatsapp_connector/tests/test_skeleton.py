# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnWhatsappConnectorSkeleton(TransactionCase):
    """Phase 1 tests for module skeleton and security."""

    def test_account_creation(self):
        """Ensure a WhatsApp account can be created with required fields."""
        account = self.env['rn.whatsapp.account'].create({
            'name': 'Test Account',
            'provider': 'meta_cloud',
            'phone_number': '+15551234567',
        })
        self.assertEqual(account.status, 'draft')

    def test_message_uuid_unique(self):
        """Ensure messages receive a UUID on create."""
        account = self.env['rn.whatsapp.account'].create({
            'name': 'Msg Account',
            'provider': 'meta_cloud',
        })
        message = self.env['rn.whatsapp.message'].create({
            'account_id': account.id,
            'phone': '+15550001111',
            'body': 'Hello',
        })
        self.assertTrue(message.uuid)

    def test_security_groups_exist(self):
        """Verify security groups are installed."""
        group = self.env.ref('rn_whatsapp_connector.group_rn_whatsapp_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_message_service_build(self):
        """Message service should create draft outbound messages."""
        account = self.env['rn.whatsapp.account'].create({
            'name': 'Service Account',
            'provider': 'meta_cloud',
        })
        message = self.env['rn.whatsapp.message.service'].build_text_message(
            account, '+15550002222', 'Test body'
        )
        self.assertEqual(message.status, 'draft')
        self.assertEqual(message.direction, 'outbound')
