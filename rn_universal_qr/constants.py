# -*- coding: utf-8 -*-
QR_PAYLOAD_TYPES = [
    ('record_url', 'Secure Record URL'),
    ('internal_url', 'Internal URL'),
    ('public_url', 'Public URL'),
    ('record_name', 'Record Name'),
    ('barcode', 'Barcode'),
    ('custom_text', 'Custom Text'),
]
QR_ACTION_TYPES = [
    ('open_record', 'Open Odoo Record'),
    ('portal_page', 'Open Portal Page'),
    ('download_pdf', 'Download Document PDF'),
    ('custom_url', 'Open Custom URL'),
    ('server_action', 'Run Server Action'),
]
QR_SIZES = [('100', '100 x 100'), ('200', '200 x 200'), ('300', '300 x 300'), ('500', '500 x 500')]
QR_COLORS = [('black', 'Black'), ('blue', 'Blue'), ('company', 'Company Color'), ('green', 'Green'), ('custom', 'Custom')]
QR_EXPIRATION = [('never', 'Never'), ('30', '30 Days'), ('90', '90 Days'), ('365', '365 Days')]
QR_ECC_LEVELS = [('L', 'Low (7%)'), ('M', 'Medium (15%)'), ('Q', 'Quartile (25%)'), ('H', 'High (30%)')]
QR_COLOR_HEX = {'black': '#000000', 'blue': '#2563EB', 'green': '#16A34A'}
DEFAULT_QR_SIZE = '200'
DEFAULT_QR_COLOR = 'black'
DEFAULT_PAYLOAD_TYPE = 'record_url'
DEFAULT_ACTION_TYPE = 'open_record'
DEFAULT_ECC_LEVEL = 'M'
