# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_jewellery_core')
class TestRnJewelleryCore(TransactionCase):

    def test_groups_exist(self):
        sales = self.env.ref('rn_jewellery_core.group_rn_jewellery_sales', raise_if_not_found=False)
        manager = self.env.ref('rn_jewellery_core.group_rn_jewellery_manager', raise_if_not_found=False)
        self.assertTrue(sales)
        self.assertTrue(manager)

    def test_metal_purity_and_rate(self):
        purity = self.env['rn.jewellery.metal.purity'].create({
            'name': '22K Gold',
            'metal_type': 'gold',
            'karat': '22K',
            'purity_factor': 0.916,
        })
        self.assertTrue(purity.id)
        rate = self.env['rn.jewellery.metal.rate'].create({
            'metal_type': 'gold',
            'rate_per_gram': 6500.0,
        })
        self.assertTrue(rate.id)
        self.assertEqual(rate.get_latest_rate('gold'), 6500.0)

    def test_karigar_and_job_card(self):
        karigar = self.env['rn.jewellery.karigar'].create({
            'name': 'Test Karigar',
        })
        self.assertTrue(karigar.id)
        job = self.env['rn.jewellery.job.card'].create({
            'karigar_id': karigar.id,
        })
        self.assertTrue(job.id)
