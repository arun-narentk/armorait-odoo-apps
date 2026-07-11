# -*- coding: utf-8 -*-
"""Constants for rn_domain_builder."""

SUPPORTED_MODELS = [
    ('sale.order', 'Sale Orders'),
    ('account.move', 'Invoices'),
    ('product.template', 'Products'),
    ('crm.lead', 'CRM Opportunities'),
    ('res.partner', 'Contacts'),
    ('hr.employee', 'Employees'),
    ('purchase.order', 'Purchase Orders'),
    ('stock.picking', 'Stock Transfers'),
    ('project.project', 'Projects'),
]

OPERATOR_ALIASES = {
    '=': {'equals', 'equal', 'is', 'eq'},
    '!=': {'not equals', 'not equal', 'is not', 'neq'},
    '>': {'greater than', 'above', 'more than', 'over', 'gt'},
    '>=': {'greater or equal', 'at least', 'gte'},
    '<': {'less than', 'below', 'under', 'lt'},
    '<=': {'less or equal', 'at most', 'lte'},
    'ilike': {'contains', 'containing', 'like', 'including'},
    'in': {'between', 'among'},
}

DATE_EXPRESSIONS = {
    'today': 'today',
    'yesterday': 'yesterday',
    'last week': 'last_week',
    'last month': 'last_month',
    'this week': 'this_week',
    'this month': 'this_month',
    'this year': 'this_year',
    'next month': 'next_month',
}

LOGICAL_ALIASES = {
    'and': '&',
    'or': '|',
    'not': '!',
}

SUGGESTION_CHIPS = [
    'confirmed',
    'draft',
    'paid',
    'overdue',
    'lost',
    'this month',
    'greater than',
    'less than',
    'contains',
    'vip',
]
