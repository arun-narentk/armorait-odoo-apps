# -*- coding: utf-8 -*-
{
    'name': 'Credit Control',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Credit limits, risk scoring, and payment reminders',
    'description': """
Smart Credit Shield: production-grade credit control and WhatsApp automation.

**Credit Risk Engine**
- Partner credit risk score (0–100) and level: Low / Medium / High / Critical.
- Weighted scoring: overdue ratio, avg payment delay, unpaid count, total exposure.
- Configurable weights via Settings (Invoicing → Credit Risk) or Technical → Parameters.
- Average payment delay (days) per partner.

**Smart Sale Order Blocking**
- High risk → warning before confirmation.
- Critical risk → block confirmation (manager override via wizard).
- Override wizard: reason, approver, full chatter log.

**WhatsApp Automation**
- Triggers: invoice overdue, risk level change, SO blocked, payment reminder.
- Cron: daily overdue check; WhatsApp message log; attach to chatter.
- Model whatsapp.message.log: sent / failed / delivered.

**Credit Control Dashboard**
- Total exposure, high-risk customers, overdue trend, top 10 risky partners, avg delay KPI.

Requires: Odoo 19, Sales, Accounting, Mail.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'depends': [
        'sale_management',
        'account',
        'mail',
    ],
    'data': [
        'security/credit_shield_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/credit_dashboard_views.xml',
        'views/credit_violation_log_views.xml',
        'views/whatsapp_message_log_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/credit_override_wizard_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 49.99,
    'live_test_url': 'https://www.armorait.com',
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/overview.png',
        'static/description/dashboard.png',
    ],
}
