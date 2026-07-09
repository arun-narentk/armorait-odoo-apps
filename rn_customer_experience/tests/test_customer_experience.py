# -*- coding: utf-8 -*-

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install', 'rn_customer_experience')
class TestCustomerExperience(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Portal Customer',
            'email': 'portal.customer@example.com',
        })
        cls.dashboard_service = cls.env['rn.customer.experience.dashboard.service']
        cls.assistant_service = cls.env['rn.customer.experience.assistant.service']
        cls.analytics_service = cls.env['rn.customer.experience.analytics.service']

    def test_dashboard_returns_summary(self):
        data = self.dashboard_service.get_partner_dashboard(self.partner)
        self.assertIn('summary', data)
        self.assertIn('orders', data)
        self.assertIn('invoices', data)
        self.assertIn('downloads', data)

    def test_ticket_sequence_on_create(self):
        ticket = self.env['rn.customer.experience.ticket'].create({
            'name': 'Machine not starting',
            'partner_id': self.partner.id,
            'description': 'Unit fails on power up.',
            'category': 'service',
        })
        self.assertNotEqual(ticket.reference, 'New')
        self.assertEqual(ticket.state, 'new')

    def test_assistant_invoice_query(self):
        result = self.assistant_service.answer_query(self.partner, 'Show my invoices')
        self.assertIn('invoice', result['answer'].lower())
        self.assertEqual(result['action']['url'], '/my/experience/invoices')

    def test_analytics_track_event(self):
        event = self.analytics_service.track_event(
            'dashboard',
            partner=self.partner,
            description='Test dashboard view',
        )
        self.assertEqual(event.event_type, 'dashboard')
        self.assertEqual(event.partner_id, self.partner)

    def test_admin_dashboard_metrics(self):
        self.analytics_service.track_event('login', partner=self.partner)
        metrics = self.analytics_service.get_admin_dashboard()
        self.assertIn('portal_logins', metrics)
        self.assertIn('self_service_rate', metrics)
