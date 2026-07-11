# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_name_assistant')
class TestRnNameAssistant(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['rn.name.generator.service']
        cls.category = cls.env['product.category'].create({'name': 'Business Laptop'})
        cls.product = cls.env['product.template'].create({
            'name': 'Laptop',
            'rn_brand': 'Dell',
            'rn_series': 'Latitude',
            'rn_model_number': '7440',
            'categ_id': cls.category.id,
        })
        cls.furniture = cls.env['product.template'].create({
            'name': 'Table',
            'rn_brand': 'IKEA',
            'rn_material': 'Oak',
            'rn_size': '120 cm',
            'categ_id': cls.env['product.category'].create({'name': 'Dining Table'}).id,
        })
        cls.partner = cls.env['res.partner'].create({'name': 'ABC'})
        cls.lead = cls.env['crm.lead'].create({'name': 'Hospital'})
        cls.project = cls.env['project.project'].create({'name': 'Website'})
        cls.task = cls.env['project.task'].create({
            'name': 'Review docs',
            'project_id': cls.project.id,
        })

    def test_product_name_generation(self):
        suggestions = self.service.generate_for_record('product.template', self.product.id)
        self.assertTrue(suggestions)
        names = [row['name'] for row in suggestions]
        self.assertTrue(any('Dell' in name and '7440' in name for name in names))

    def test_furniture_template(self):
        suggestions = self.service.generate_for_record('product.template', self.furniture.id)
        names = [row['name'] for row in suggestions]
        self.assertTrue(any('IKEA' in name and 'Oak' in name for name in names))

    def test_contact_heuristics(self):
        suggestions = self.service.generate_for_record('res.partner', self.partner.id)
        names = [row['name'] for row in suggestions]
        self.assertIn('ABC Technologies Private Limited', names)
        self.assertIn('ABC Engineering', names)

    def test_lead_heuristics(self):
        suggestions = self.service.generate_for_record('crm.lead', self.lead.id)
        names = [row['name'] for row in suggestions]
        self.assertIn('Hospital ERP Implementation', names)

    def test_project_heuristics(self):
        suggestions = self.service.generate_for_record('project.project', self.project.id)
        names = [row['name'] for row in suggestions]
        self.assertIn('Corporate Website Redesign', names)

    def test_apply_selected_name(self):
        self.service.apply_selected_name(
            'product.template',
            self.product.id,
            'Dell Latitude 7440 Business Laptop',
        )
        self.assertEqual(self.product.name, 'Dell Latitude 7440 Business Laptop')

    def test_wizard_open_and_apply(self):
        action = self.product.action_suggest_name()
        wizard = self.env['rn.name.generator.wizard'].browse(action['res_id'])
        self.assertTrue(wizard.line_ids)
        wizard.action_use_selected()
        self.assertNotEqual(self.product.name, 'Laptop')

    def test_batch_generate(self):
        wizard = self.env['rn.name.batch.wizard'].create({
            'res_model': 'product.template',
            'res_ids': f'{self.product.id},{self.furniture.id}',
            'max_suggestions': 2,
        })
        wizard.action_generate()
        self.assertEqual(len(wizard.result_ids), 2)
        self.assertTrue(wizard.result_ids[0].suggested_name)

    def test_preview_name(self):
        preview = self.service.preview_name(
            'product.template',
            {
                'Brand': 'Dell',
                'Series': 'Latitude',
                'Model': '7440',
                'Category': 'Business Laptop',
            },
            '{Brand} {Series} {Model} {Category}',
        )
        self.assertEqual(preview, 'Dell Latitude 7440 Business Laptop')

    def test_security_groups_exist(self):
        group = self.env.ref(
            'rn_name_assistant.group_rn_name_assistant_manager',
            raise_if_not_found=False,
        )
        self.assertTrue(group)
