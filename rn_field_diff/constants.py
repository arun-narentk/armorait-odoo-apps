# -*- coding: utf-8 -*-

FIELD_TYPE_SELECTION = [
    ('integer', 'Integer'),
    ('float', 'Float'),
    ('monetary', 'Monetary'),
    ('char', 'Text'),
    ('text', 'Long Text'),
    ('boolean', 'Boolean'),
    ('selection', 'Selection'),
    ('date', 'Date'),
    ('datetime', 'Datetime'),
    ('many2one', 'Many2one'),
    ('many2many', 'Many2many'),
    ('one2many', 'One2many'),
    ('other', 'Other'),
]

CHANGE_CATEGORY_SELECTION = [
    ('modified', 'Modified'),
    ('added', 'Added'),
    ('removed', 'Removed'),
]

COLOR_CLASS_SELECTION = [
    ('blue', 'Modified'),
    ('green', 'Added'),
    ('red', 'Removed'),
    ('gray', 'Unchanged'),
]

FILTER_CATEGORY_SELECTION = [
    ('numeric', 'Numeric'),
    ('date', 'Date'),
    ('text', 'Text'),
    ('relational', 'Relational'),
    ('boolean', 'Boolean'),
    ('other', 'Other'),
]
