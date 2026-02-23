# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Odoo Integration',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Send Sale Orders, Purchase Orders, Invoices & Delivery via WhatsApp',
    'description': """
WhatsApp Odoo Integration (Deep Integration)
============================================

One-on-one communication via WhatsApp from Odoo, with automation and logging.

**Send from documents**
* Sale Orders, Purchase Orders, Invoices, Delivery Orders — one-click Send via WhatsApp with pre-filled message and optional PDF link.

**Two-way message logging**
* Every WhatsApp send is logged in the document's chatter (outbound log). Full history in one place.

**Automation**
* Unpaid invoice follow-up: automatic reminders for overdue customer invoices (configurable days after due).
* Payment reminder: reminders for partially paid invoices.
* Sales follow-up sequence: automatic follow-up for quotations sent but not confirmed (configurable days).
* Delivery status alert: when a delivery order is validated, create a WhatsApp reminder to notify the contact.

**Process reminders**
* Accounting &gt; WhatsApp Reminders: list of pending reminders; open document or Send via WhatsApp. When sent, logged in chatter.

Uses the contact's Phone or Mobile. No API required — opens wa.me. Optional document links use Odoo portal.
    """,
    'author': 'ARMORAIT',
    'website': 'https://www.armorait.com',
    'depends': ['account', 'sale_management', 'purchase', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/whatsapp_cron.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/stock_picking_views.xml',
        'views/whatsapp_reminder_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'images': ['static/description/icon.svg'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
