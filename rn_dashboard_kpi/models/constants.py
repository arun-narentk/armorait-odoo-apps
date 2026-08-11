# -*- coding: utf-8 -*-
"""Shared selections and visualization catalog for Dashboard KPI Studio."""

ITEM_TYPE_SELECTION = [
    ('tile', 'KPI Tile'),
    ('line', 'Line Chart'),
    ('bar', 'Bar Chart'),
    ('horizontal_bar', 'Horizontal Bar'),
    ('area', 'Area Chart'),
    ('pie', 'Pie Chart'),
    ('doughnut', 'Doughnut Chart'),
    ('polar', 'Polar Area'),
    ('radar', 'Radar Chart'),
    ('scatter', 'Scatter Chart'),
    ('funnel', 'Funnel Chart'),
    ('radial', 'Radial Chart'),
    ('bullet', 'Bullet Chart'),
    ('map', 'Map'),
    ('list', 'List / Table'),
    ('todo', 'To-do'),
]

# Chart-family types that share dimension/measure configuration.
CHART_ITEM_TYPES = {
    'line', 'bar', 'horizontal_bar', 'area', 'pie', 'doughnut', 'polar',
    'radar', 'scatter', 'funnel', 'radial', 'bullet',
}

AGGREGATION_SELECTION = [
    ('count', 'Count'),
    ('sum', 'Sum'),
    ('avg', 'Average'),
    ('min', 'Minimum'),
    ('max', 'Maximum'),
]

DATE_GRANULARITY_SELECTION = [
    ('day', 'Day'),
    ('week', 'Week'),
    ('month', 'Month'),
    ('quarter', 'Quarter'),
    ('year', 'Year'),
]

DATE_FILTER_TYPE_SELECTION = [
    ('today', 'Today'),
    ('yesterday', 'Yesterday'),
    ('this_week', 'This Week'),
    ('last_week', 'Last Week'),
    ('this_month', 'This Month'),
    ('last_month', 'Last Month'),
    ('this_quarter', 'This Quarter'),
    ('last_quarter', 'Last Quarter'),
    ('this_year', 'This Year'),
    ('last_year', 'Last Year'),
    ('last_7_days', 'Last 7 Days'),
    ('last_30_days', 'Last 30 Days'),
    ('last_90_days', 'Last 90 Days'),
    ('last_365_days', 'Last 365 Days'),
    ('custom', 'Custom Range'),
]

THEME_SELECTION = [
    ('light', 'Light'),
    ('dark', 'Dark'),
    ('professional', 'Professional'),
    ('minimal', 'Minimal'),
    ('executive', 'Executive'),
    ('custom', 'Custom'),
]

LAYOUT_MODE_SELECTION = [
    ('grid', 'Grid'),
    ('fixed', 'Fixed'),
]

BACKGROUND_TYPE_SELECTION = [
    ('none', 'None'),
    ('color', 'Color'),
    ('image', 'Image'),
]

FILTER_TYPE_SELECTION = [
    ('date', 'Date'),
    ('selection', 'Selection'),
    ('many2one', 'Many2one'),
    ('many2many', 'Many2many'),
    ('boolean', 'Boolean'),
    ('numeric', 'Numeric'),
    ('text', 'Text'),
    ('domain', 'Domain'),
    ('company', 'Company'),
    ('user', 'Current User'),
]

DATA_SOURCE_TYPE_SELECTION = [
    ('odoo', 'Odoo Model'),
    ('csv', 'CSV File'),
    ('xlsx', 'Excel File'),
]

NUMBER_FORMAT_SELECTION = [
    ('number', 'Number'),
    ('integer', 'Integer'),
    ('float', 'Decimal'),
    ('monetary', 'Monetary'),
    ('percentage', 'Percentage'),
]

SORT_ORDER_SELECTION = [
    ('asc', 'Ascending'),
    ('desc', 'Descending'),
]

COLOR_PALETTE_SELECTION = [
    ('default', 'Default'),
    ('cool', 'Cool'),
    ('warm', 'Warm'),
    ('contrast', 'High Contrast'),
    ('pastel', 'Pastel'),
    ('custom', 'Custom'),
]

DEFINITION_VERSION = 1

EMPTY_DATA_PAYLOAD = {
    'labels': [],
    'datasets': [],
    'records': [],
    'metadata': {},
    'total': 0,
    'warnings': [],
}
