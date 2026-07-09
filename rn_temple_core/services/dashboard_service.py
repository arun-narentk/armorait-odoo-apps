# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleDashboardService(models.AbstractModel):
    _name = 'rn.temple.dashboard.service'
    _description = 'Temple Dashboard Service'

    def get_trustee_dashboard(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        Donation = self.env['rn.temple.donation']
        month_start = today.replace(day=1)
        donations = Donation.search([
            ('company_id', '=', company_id),
            ('state', '=', 'confirmed'),
            ('donation_date', '>=', fields.Datetime.to_datetime(month_start)),
        ])
        festivals = self.env['rn.temple.festival'].search([
            ('company_id', '=', company_id),
            ('state', 'in', ('planned', 'active')),
        ])
        hundi_pending = self.env['rn.temple.hundi.collection'].search_count([
            ('company_id', '=', company_id),
            ('state', 'in', ('draft', 'counted', 'verified')),
        ])
        return {
            'donations_month': sum(donations.mapped('amount')),
            'donation_count_month': len(donations),
            'active_festivals': len(festivals),
            'hundi_pending': hundi_pending,
            'devotee_count': self.env['rn.temple.devotee'].search_count([
                ('company_id', '=', company_id),
                ('active', '=', True),
            ]),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def get_office_dashboard(self, company_id=None):
        company_id = company_id or self.env.company.id
        today_start = fields.Datetime.to_datetime(fields.Date.context_today(self))
        tomorrow_end = today_start + timedelta(days=1)
        bookings = self.env['rn.temple.seva.booking'].search([
            ('company_id', '=', company_id),
            ('booking_date', '>=', today_start),
            ('booking_date', '<', tomorrow_end),
            ('state', 'in', ('draft', 'confirmed')),
        ])
        pending_receipts = self.env['rn.temple.donation'].search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'draft'),
        ])
        upcoming_festivals = self.env['rn.temple.festival'].search_count([
            ('company_id', '=', company_id),
            ('date_start', '>=', fields.Date.context_today(self)),
            ('state', 'in', ('planned', 'active')),
        ])
        return {
            'bookings_today': len(bookings),
            'pending_receipts': pending_receipts,
            'upcoming_festivals': upcoming_festivals,
            'annadhanam_today': self.env['rn.temple.annadhanam'].search_count([
                ('company_id', '=', company_id),
                ('meal_date', '=', fields.Date.context_today(self)),
            ]),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
