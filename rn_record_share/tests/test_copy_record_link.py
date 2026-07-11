# -*- coding: utf-8 -*-
"""End-to-end tests for Copy Record Link / Record Share."""

from pathlib import Path
from unittest.mock import patch

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.rn_record_share import constants as const


@tagged('post_install', '-at_install', 'rn_record_share')
class TestCopyRecordLink(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['rn.record.share.service']
        cls.share_user = cls.env['res.users'].search([
            ('login', '=', 'copy_link_user'),
        ], limit=1)
        if not cls.share_user:
            cls.share_user = cls.env['res.users'].create({
                'name': 'Copy Link User',
                'login': 'copy_link_user',
                'email': 'copy_link_user@armorait.com',
                'group_ids': [(6, 0, [
                    cls.env.ref('base.group_user').id,
                    cls.env.ref('rn_record_share.group_rn_record_share_user').id,
                    cls.env.ref('sales_team.group_sale_salesman').id,
                    cls.env.ref('account.group_account_invoice').id,
                    cls.env.ref('project.group_project_user').id,
                ])],
            })
        else:
            cls.share_user.write({
                'group_ids': [(4, gid) for gid in [
                    cls.env.ref('rn_record_share.group_rn_record_share_user').id,
                    cls.env.ref('sales_team.group_sale_salesman').id,
                    cls.env.ref('account.group_account_invoice').id,
                    cls.env.ref('project.group_project_user').id,
                ]],
            })
        cls.company_b = cls.env['res.company'].create({'name': 'CopyLink Company B'})
        cls.share_user.write({'company_ids': [(4, cls.company_b.id)]})
        cls.partner = cls.env['res.partner'].create({
            'name': 'CopyLink Azure Interior',
            'email': 'copylink@armorait.com',
        })
        cls.product = cls.env['product.product'].search([('sale_ok', '=', True)], limit=1)
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {'product_id': cls.product.id, 'product_uom_qty': 1})],
        })
        cls.invoice = cls.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': cls.partner.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'CopyLink Service',
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })
        cls.project = cls.env['project.project'].create({'name': 'CopyLink Project'})
        cls.task = cls.env['project.task'].create({
            'name': 'CopyLink Task',
            'project_id': cls.project.id,
        })

    def test_module_installed(self):
        module = self.env['ir.module.module'].search([('name', '=', 'rn_record_share')], limit=1)
        self.assertEqual(module.state, 'installed')

    def test_backend_assets_registered(self):
        manifest_path = Path(__file__).resolve().parents[1] / '__manifest__.py'
        content = manifest_path.read_text(encoding='utf-8')
        self.assertIn('record_share_clipboard.js', content)
        self.assertIn('record_share_hotkey.js', content)

    def test_form_view_copy_button_present(self):
        view = self.env.ref('rn_record_share.view_order_form_record_share')
        arch = view.arch
        self.assertIn('action_copy_record_link', arch)
        self.assertIn('oe_stat_button', arch)
        self.assertIn('Copy Link', arch)

    def test_url_generation_for_models(self):
        cases = [
            ('sale.order', self.order.id),
            ('account.move', self.invoice.id),
            ('res.partner', self.partner.id),
            ('project.project', self.project.id),
            ('project.task', self.task.id),
        ]
        for model, res_id in cases:
            url = self.service.get_internal_url(model, res_id)
            self.assertIn(f'/odoo/{model}/{res_id}', url)

    def test_clipboard_client_action_payload(self):
        action = self.service.copy_link_action(self.partner, const.FORMAT_URL)
        self.assertEqual(action['type'], 'ir.actions.client')
        self.assertEqual(action['tag'], 'rn_record_share.copy_clipboard')
        self.assertIn('/odoo/res.partner/', action['params']['text'])
        self.assertIn('Link copied', action['params']['message'])

    def test_labeled_url_format(self):
        text = self.service.format_share_text(self.order, const.FORMAT_LABELED_URL)
        self.assertIn(' - ', text)
        self.assertIn(f'/odoo/sale.order/{self.order.id}', text)

    def test_access_rights_enforced(self):
        record = self.partner
        with patch.object(type(record), 'has_access', return_value=False):
            with self.assertRaises(AccessError):
                self.service.check_record_access(record)

    def test_multi_company_url(self):
        order_b = self.env['sale.order'].with_company(self.company_b).create({
            'partner_id': self.partner.id,
            'company_id': self.company_b.id,
            'order_line': [(0, 0, {'product_id': self.product.id, 'product_uom_qty': 1})],
        })
        url = self.service.get_internal_url('sale.order', order_b.id)
        self.assertIn(f'/odoo/sale.order/{order_b.id}', url)
        action = order_b.with_company(self.company_b).action_copy_record_link()
        self.assertEqual(action['tag'], 'rn_record_share.copy_clipboard')
        self.assertIn(f'/odoo/sale.order/{order_b.id}', action['params']['text'])

    def test_multiple_models_copy_action(self):
        records = [
            self.order,
            self.invoice,
            self.partner,
            self.project,
            self.task,
        ]
        for record in records:
            action = record.action_copy_record_link()
            self.assertEqual(action['tag'], 'rn_record_share.copy_clipboard')
            self.assertIn(f'/odoo/{record._name}/{record.id}', action['params']['text'])

    def test_mobile_friendly_button_classes(self):
        view = self.env.ref('rn_record_share.view_partner_form_record_share')
        self.assertIn('oe_stat_button', view.arch)
        self.assertIn('o_stat_info', view.arch)

    def test_module_uninstall_metadata(self):
        module = self.env['ir.module.module'].search([('name', '=', 'rn_record_share')], limit=1)
        self.assertFalse(module.dependencies_id.filtered(lambda dep: dep.state != 'installed'))
