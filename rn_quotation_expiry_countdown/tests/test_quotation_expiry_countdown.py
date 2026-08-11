# -*- coding: utf-8 -*-
"""Tests for Quotation Expiry Countdown."""

from datetime import timedelta

from odoo import fields
from odoo.fields import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_quotation_expiry_countdown')
class TestQuotationExpiryCountdown(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Expiry Countdown Customer',
            'company_id': False,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Expiry Countdown Product',
            'list_price': 50.0,
            'type': 'consu',
            'sale_ok': True,
            'taxes_id': [Command.clear()],
        })
        cls.today = fields.Date.context_today(cls.env.user)

    def _create_quotation(self, validity_date=None, confirm=False, cancel=False):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'validity_date': validity_date,
            'order_line': [
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1.0,
                    'price_unit': 50.0,
                }),
            ],
        })
        if validity_date is not None:
            order.validity_date = validity_date
        if confirm:
            order.action_confirm()
        if cancel:
            if order.state in ('draft', 'sent', 'sale'):
                order._action_cancel()
        return order

    def test_01_future_quotation(self):
        order = self._create_quotation(self.today + timedelta(days=5))
        self.assertEqual(order.quotation_expiry_countdown, 'Expires in 5 days')
        self.assertEqual(order.quotation_expiry_urgency, 'ok')

    def test_02_expired_quotation(self):
        order = self._create_quotation(self.today - timedelta(days=2))
        self.assertEqual(order.quotation_expiry_countdown, 'Expired 2 days ago')
        self.assertEqual(order.quotation_expiry_urgency, 'expired')

    def test_03_expires_today(self):
        order = self._create_quotation(self.today)
        self.assertEqual(order.quotation_expiry_countdown, 'Expires today')
        self.assertEqual(order.quotation_expiry_urgency, 'warning')

    def test_04_no_validity_date(self):
        order = self._create_quotation(validity_date=False)
        order.validity_date = False
        order.invalidate_recordset(['quotation_expiry_countdown', 'quotation_expiry_urgency'])
        order._compute_quotation_expiry_countdown()
        self.assertFalse(order.quotation_expiry_countdown)
        self.assertEqual(order.quotation_expiry_urgency, 'none')

    def test_05_confirmed_sale_order(self):
        order = self._create_quotation(self.today + timedelta(days=3), confirm=True)
        self.assertEqual(order.state, 'sale')
        self.assertFalse(order.quotation_expiry_countdown)
        self.assertEqual(order.quotation_expiry_urgency, 'none')

    def test_06_cancelled_sale_order(self):
        order = self._create_quotation(self.today + timedelta(days=3), cancel=True)
        self.assertEqual(order.state, 'cancel')
        self.assertFalse(order.quotation_expiry_countdown)
        self.assertEqual(order.quotation_expiry_urgency, 'none')

    def test_07_expires_in_one_day(self):
        order = self._create_quotation(self.today + timedelta(days=1))
        text = order.quotation_expiry_countdown
        self.assertTrue(
            text.startswith('Expires in 1 day') or text.startswith('Expires in'),
            msg=text,
        )
        self.assertIn(order.quotation_expiry_urgency, ('ok', 'warning'))

    def test_08_search_filters(self):
        future = self._create_quotation(self.today + timedelta(days=10))
        today_q = self._create_quotation(self.today)
        expired = self._create_quotation(self.today - timedelta(days=1))

        SaleOrder = self.env['sale.order']
        expiring_today = SaleOrder.search([
            ('state', 'in', ('draft', 'sent')),
            ('validity_date', '=', self.today),
            ('id', 'in', (future | today_q | expired).ids),
        ])
        self.assertIn(today_q, expiring_today)
        self.assertNotIn(future, expiring_today)
        self.assertNotIn(expired, expiring_today)

        expired_qs = SaleOrder.search([
            ('state', 'in', ('draft', 'sent')),
            ('validity_date', '<', self.today),
            ('id', 'in', (future | today_q | expired).ids),
        ])
        self.assertIn(expired, expired_qs)
        self.assertNotIn(today_q, expired_qs)

        within_24h = SaleOrder.search([
            ('state', 'in', ('draft', 'sent')),
            ('validity_date', '>=', self.today),
            ('validity_date', '<=', self.today + timedelta(days=1)),
            ('id', 'in', (future | today_q | expired).ids),
        ])
        self.assertIn(today_q, within_24h)
        self.assertNotIn(future, within_24h)
        self.assertNotIn(expired, within_24h)

    def test_09_expired_one_day_ago(self):
        order = self._create_quotation(self.today - timedelta(days=1))
        self.assertEqual(order.quotation_expiry_countdown, 'Expired 1 day ago')
        self.assertEqual(order.quotation_expiry_urgency, 'expired')
