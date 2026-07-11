# -*- coding: utf-8 -*-
"""Constants for Name Assistant."""

SUPPORTED_MODELS = (
    'product.template',
    'res.partner',
    'crm.lead',
    'project.project',
    'project.task',
)

PRODUCT_NAMING_FIELDS = (
    'rn_brand',
    'rn_series',
    'rn_model_number',
    'rn_color',
    'rn_capacity',
    'rn_material',
    'rn_variant_label',
    'rn_size',
)

PLACEHOLDER_ALIASES = {
    'brand': 'rn_brand',
    'series': 'rn_series',
    'model': 'rn_model_number',
    'color': 'rn_color',
    'capacity': 'rn_capacity',
    'material': 'rn_material',
    'variant': 'rn_variant_label',
    'size': 'rn_size',
    'category': 'category',
    'name': 'name',
}

CATEGORY_SYNONYMS = {
    'laptop': ('notebook', 'portable computer'),
    'notebook': ('laptop',),
    'table': ('desk',),
    'phone': ('smartphone', 'mobile'),
}

CONTACT_SUFFIXES = (
    'Technologies Pvt Ltd',
    'Engineering',
    'Industrial Solutions',
    'Traders',
    'Global Services',
)

PROJECT_SUFFIXES = (
    'Redesign',
    'Development',
    'Migration Project',
    'Enhancement Initiative',
    'Implementation',
)

LEAD_SUFFIXES = (
    'ERP Implementation',
    'Software Deployment',
    'Digital Transformation',
    'Automation Project',
    'Consulting Engagement',
)

TASK_SUFFIXES = (
    'Review',
    'Planning',
    'Follow-up',
    'Documentation',
    'Quality Check',
)

DEFAULT_MAX_SUGGESTIONS = 5
