# -*- coding: utf-8 -*-
"""Constants for Record Share."""

DEFAULT_LOG_RETENTION_DAYS = 90
DEFAULT_LINK_FORMAT = 'url'

FORMAT_URL = 'url'
FORMAT_MARKDOWN = 'markdown'
FORMAT_HTML = 'html'
FORMAT_NAME = 'name'
FORMAT_JSON = 'json'
FORMAT_LABELED_URL = 'labeled_url'

COPY_FORMATS = (
    (FORMAT_URL, 'URL'),
    (FORMAT_LABELED_URL, 'Name and URL'),
    (FORMAT_MARKDOWN, 'Markdown'),
    (FORMAT_HTML, 'HTML'),
    (FORMAT_NAME, 'Record Name'),
    (FORMAT_JSON, 'JSON'),
)

ACTION_COPY = 'copy'
ACTION_SHARE = 'share'
ACTION_EMAIL = 'email'
ACTION_WHATSAPP = 'whatsapp'
ACTION_QR = 'qr'
ACTION_OPEN = 'open'
