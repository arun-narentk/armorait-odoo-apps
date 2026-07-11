# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.rn_name_assistant.services.name_utils import (
    apply_template,
    cleanup_name,
    expand_abbreviations,
    score_name,
    title_case_smart,
)


@tagged('post_install', '-at_install', 'rn_name_assistant')
class TestRnNameUtils(TransactionCase):

    def test_apply_template_skips_empty_placeholders(self):
        result = apply_template('{Brand} {Series} {Model}', {'brand': 'Dell', 'model': '7440'})
        self.assertEqual(result, 'Dell 7440')

    def test_cleanup_removes_duplicate_words(self):
        self.assertEqual(cleanup_name('Dell Dell Laptop Laptop'), 'Dell Laptop')

    def test_title_case_smart_handles_iphone(self):
        self.assertEqual(title_case_smart('iphone 15 pro max'), 'iPhone 15 Pro Max')

    def test_expand_abbreviations(self):
        mapping = {'ltd': 'Limited', 'pvt': 'Private'}
        self.assertEqual(expand_abbreviations('ABC Pvt Ltd', mapping), 'ABC Private Limited')

    def test_score_name_prefers_richer_names(self):
        short = score_name('Laptop', seed='Laptop', field_count=1)
        long = score_name('Dell Latitude 7440 Business Laptop', seed='Laptop', field_count=4)
        self.assertGreater(long, short)
