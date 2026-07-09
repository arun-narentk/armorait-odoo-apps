# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnGstProSkeleton(TransactionCase):
    """Phase 1 tests for GST Pro skeleton."""

    def test_groups_exist(self):
        group = self.env.ref('rn_l10n_in_gst_pro.group_rn_gst_accountant', raise_if_not_found=False)
        self.assertTrue(group)

    def test_period_and_return_create(self):
        period = self.env['rn.gst.period'].create({
            'name': 'Test Month',
            'code': 'TEST01',
            'financial_year': '2025-26',
            'date_start': '2025-07-01',
            'date_end': '2025-07-31',
        })
        gst_return = self.env['rn.gst.return'].create({
            'return_type': 'gstr1',
            'period_id': period.id,
        })
        self.assertTrue(gst_return.name)
        gst_return.action_compute()
        self.assertEqual(gst_return.state, 'computed')

    def test_gstin_pattern(self):
        service = self.env['rn.gst.validation.service']
        self.assertTrue(service.is_valid_gstin('29AABCU9603R1ZM'))
        self.assertFalse(service.is_valid_gstin('INVALID'))
