# -*- coding: utf-8 -*-
{
    'name': 'Payroll Portal',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Employee self-service for payslips, leave, and HR documents',
    'description': """
Payroll Portal Pro: executive-style payroll self-service for employees.

**Dashboard**
- KPI cards: Gross Pay, Take Home, Deductions (for selected month)
- Financial year filter (India-friendly FY dropdown)
- Card-based monthly payslip grid with circular progress (Net vs Gross)

**Payslip detail**
- Dedicated page /my/payroll/<id>: Earnings, Deductions, Employer contribution, Tax
- Modern layout; PDF download

**Tax summary**
- YTD: Taxable Income, Tax Paid, Estimated Tax Due (from salary rule category TAX)

**Security**
- Only the logged-in employee sees their data (employee_id.user_id = current user)
- No ID tampering; access validated in controller

Requires: Odoo 19, HR, Portal, Website. For payslip data, also install **HR Payroll** (Odoo Enterprise or community) and the **Payroll Portal Pro (Payroll)** extension module.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'depends': [
        'hr',
        'portal',
        'website',
    ],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'rn_payroll_portal_pro/static/src/css/portal_payroll.css',
        ],
    },
            'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/screenshot_form.png',
        'static/description/screenshot_list.png',
        'static/description/screenshot_dashboard.png',
        'static/description/screenshot_back.png',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 49.99,
    'live_test_url': 'https://www.armorait.com',
}
