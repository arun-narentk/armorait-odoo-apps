# -*- coding: utf-8 -*-
"""
Portal controller for payroll: dashboard and payslip detail.
Only the logged-in employee sees their own data (employee_id.user_id = request.env.user).
When hr_payroll is not installed, shows a message to install it and the Payroll extension.
"""

from datetime import date
from collections import defaultdict

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied, MissingError
from odoo.tools.misc import format_amount


def _payslip_available(env):
    """True if hr.payslip model is available (hr_payroll or equivalent installed)."""
    return bool(env['ir.model'].sudo().search([('model', '=', 'hr.payslip')], limit=1))


class PayrollPortal(http.Controller):

    def _get_employee(self):
        """Return the employee linked to the current user; None if not an employee."""
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([
            ('user_id', '=', user.id),
        ], limit=1)
        return employee

    def _get_payslip_check_access(self, payslip_id):
        """Load payslip and ensure current user is the employee. Raise AccessDenied or MissingError."""
        if not _payslip_available(request.env):
            raise MissingError('Payslip module not available.')
        payslip = request.env['hr.payslip'].sudo().browse(payslip_id).exists()
        if not payslip:
            raise MissingError('Payslip not found.')
        employee = self._get_employee()
        if not employee or payslip.employee_id.id != employee.id:
            raise AccessDenied('You do not have access to this payslip.')
        return payslip

    @http.route(['/my/payroll', '/my/payroll/page/<int:page>'], type='http', auth='user', website=True)
    def portal_payroll_dashboard(self, page=1, fy_start=None, fy_end=None, month=None, year=None, **kw):
        """
        Payroll portal dashboard: KPI cards, financial year filter, card-based payslip list.
        Only shows data for the current user's employee. If hr.payslip is not available, shows install message.
        """
        employee = self._get_employee()
        if not employee:
            return request.redirect('/my')
        if not _payslip_available(request.env):
            return request.render('rn_payroll_portal_pro.portal_payroll_no_payroll', {
                'page_name': 'payroll',
                'employee': employee,
            })
        Payroll = request.env['hr.payslip'].sudo()
        financial_years = Payroll._get_financial_years()
        # Parse FY filter (date range)
        date_start = date_end = None
        if fy_start:
            try:
                date_start = date.fromisoformat(fy_start)
                # India FY: April–March (end = start + 1 year - 1 day)
                from datetime import timedelta
                date_end = date(date_start.year + 1, date_start.month, date_start.day) - timedelta(days=1)
            except (TypeError, ValueError):
                pass
        if not date_start or not date_end:
            # Default: current FY (India April–March)
            today = date.today()
            if today.month >= 4:
                date_start = date(today.year, 4, 1)
                date_end = date(today.year + 1, 3, 31)
            else:
                date_start = date(today.year - 1, 4, 1)
                date_end = date(today.year, 3, 31)
        domain = [
            ('employee_id', '=', employee.id),
            ('state', 'in', ('done', 'paid')),
            ('date_from', '>=', date_start),
            ('date_to', '<=', date_end),
        ]
        payslips = Payroll.search(domain, order='date_from desc')
        # Group by month for card layout
        by_month = defaultdict(list)
        for slip in payslips:
            key = (slip.date_from.month, slip.date_from.year)
            by_month[key].append(slip)
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        months_list = []
        for (mo, yr), slips in sorted(by_month.items(), key=lambda x: (x[0][1], x[0][0]), reverse=True):
            first = slips[0]
            totals = first._portal_totals_by_category()
            gross = totals.get('gross', 0)
            net = totals.get('net', 0)
            deductions = totals.get('deductions', 0)
            net_pct = (net / gross * 100) if gross else 0
            months_list.append({
                'month_name': month_names[mo],
                'year': yr,
                'month_key': (mo, yr),
                'payslips': slips,
                'gross': gross,
                'net': net,
                'deductions': deductions,
                'net_pct': round(net_pct, 0),
            })
        # Selected month for KPI cards (first month in list or from query)
        selected_month_gross = selected_month_net = selected_month_ded = 0.0
        if month and year:
            try:
                m, y = int(month), int(year)
                for mdata in months_list:
                    if mdata['month_key'] == (m, y):
                        selected_month_gross = mdata['gross']
                        selected_month_net = mdata['net']
                        selected_month_ded = mdata['deductions']
                        break
            except (TypeError, ValueError):
                pass
        if not selected_month_gross and months_list:
            selected_month_gross = months_list[0]['gross']
            selected_month_net = months_list[0]['net']
            selected_month_ded = months_list[0]['deductions']
        # YTD tax summary
        ytd = Payroll._portal_ytd_tax_totals(employee.id, date_start, date_end)
        values = {
            'employee': employee,
            'payslips': payslips,
            'months_list': months_list,
            'financial_years': financial_years,
            'date_start': date_start,
            'date_end': date_end,
            'selected_month_gross': selected_month_gross,
            'selected_month_net': selected_month_net,
            'selected_month_ded': selected_month_ded,
            'ytd_taxable_income': ytd['taxable_income'],
            'ytd_tax_paid': ytd['tax_paid'],
            'currency': employee.company_id.currency_id or request.env.company.currency_id,
            'page_name': 'payroll',
            'format_value': lambda v, c: format_amount(request.env, v, c) if c else str(v),
        }
        return request.render('rn_payroll_portal_pro.portal_payroll_dashboard', values)

    @http.route('/my/payroll/<int:payslip_id>', type='http', auth='user', website=True)
    def portal_payroll_detail(self, payslip_id, report_type='html', download=False, **kw):
        """
        Single payslip detail: earnings, deductions, tax. PDF download optional.
        """
        if not _payslip_available(request.env):
            return request.redirect('/my/payroll')
        payslip = self._get_payslip_check_access(payslip_id)
        totals = payslip._portal_totals_by_category()
        # Group lines by category for display
        earnings = []
        deductions = []
        tax_lines = []
        for line in payslip.line_ids:
            if not line.category_id:
                continue
            code = (line.category_id.code or '').upper()
            if code in payslip.PORTAL_EARNING_CODES or (code and code not in ('DED', 'NET', 'TAX')):
                earnings.append(line)
            elif code == payslip.PORTAL_DEDUCTION_CODE:
                deductions.append(line)
            elif code == payslip.PORTAL_TAX_CODE:
                tax_lines.append(line)
        values = {
            'payslip': payslip,
            'totals': totals,
            'earnings': earnings,
            'deductions': deductions,
            'tax_lines': tax_lines,
            'currency': payslip.company_id.currency_id or request.env.company.currency_id,
            'page_name': 'payroll',
            'format_value': lambda v, c: format_amount(request.env, v, c) if c else str(v),
        }
        return request.render('rn_payroll_portal_pro.portal_payroll_detail', values)
