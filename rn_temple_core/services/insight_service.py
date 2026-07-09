# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleInsightService(models.AbstractModel):
    _name = 'rn.temple.insight.service'
    _description = 'Temple AI Insight Service'

    def answer_devotee_question(self, question, company_id=None):
        q = (question or '').lower()
        company_id = company_id or self.env.company.id
        if 'seva' in q and ('tomorrow' in q or 'available' in q):
            sevas = self.env['rn.temple.seva.service'].available_sevas_tomorrow(company_id)
            names = ', '.join(sevas.mapped('name')) or 'No sevas configured'
            return f'Available sevas: {names}. Contact temple office to book.'
        if 'abhishekam' in q or 'archana' in q:
            return 'Seva bookings can be made at the temple office or online when enabled.'
        if 'festival' in q or 'next' in q:
            fest = self.env['rn.temple.festival'].search([
                ('company_id', '=', company_id),
                ('date_start', '>=', fields.Date.context_today(self)),
                ('state', 'in', ('planned', 'active')),
            ], order='date_start', limit=1)
            if fest:
                return f'Next festival: {fest.name} starting {fest.date_start}.'
            return 'No upcoming festivals scheduled.'
        return 'Thank you. Please contact the temple office for assistance.'

    def donation_analytics_answer(self, question, company_id=None):
        q = (question or '').lower()
        company_id = company_id or self.env.company.id
        dash = self.env['rn.temple.dashboard.service'].get_trustee_dashboard(company_id)
        if 'month' in q or 'this month' in q:
            return f'Total donations this month: {dash["donations_month"]} ({dash["donation_count_month"]} receipts).'
        if 'festival' in q:
            fests = self.env['rn.temple.festival'].search([
                ('company_id', '=', company_id),
            ], order='donation_total desc', limit=3)
            if fests:
                lines = [f'{f.name}: {f.donation_total}' for f in fests]
                return 'Top festivals by donations: ' + '; '.join(lines)
        if 'repeat' in q or 'donor' in q:
            devotees = self.env['rn.temple.devotee'].search([
                ('company_id', '=', company_id),
                ('donation_total', '>', 0),
            ], order='donation_total desc', limit=5)
            if devotees:
                return 'Top donors: ' + ', '.join(f'{d.name} ({d.donation_total})' for d in devotees)
        return f'Month donations: {dash["donations_month"]}. Active devotees: {dash["devotee_count"]}.'

    def search_receipts(self, donor_name, festival_name=None):
        domain = [('state', '=', 'confirmed')]
        if donor_name:
            domain += ['|', ('donor_name', 'ilike', donor_name), ('devotee_id.name', 'ilike', donor_name)]
        if festival_name:
            fest = self.env['rn.temple.festival'].search([('name', 'ilike', festival_name)], limit=1)
            if fest:
                domain.append(('festival_id', '=', fest.id))
        donations = self.env['rn.temple.donation'].search(domain, limit=20)
        return [{
            'receipt': d.receipt_number or d.name,
            'donor': d.donor_name or (d.devotee_id.name if d.devotee_id else ''),
            'amount': d.amount,
            'date': fields.Datetime.to_string(d.donation_date),
        } for d in donations]

    def financial_summary(self, company_id=None):
        company_id = company_id or self.env.company.id
        dash = self.env['rn.temple.dashboard.service'].get_trustee_dashboard(company_id)
        annadhanam_cost = sum(self.env['rn.temple.annadhanam'].search([
            ('company_id', '=', company_id),
            ('meal_date', '>=', fields.Date.context_today(self).replace(day=1)),
        ]).mapped('cost_estimate'))
        return {
            'donations_month': dash['donations_month'],
            'annadhanam_cost_month': annadhanam_cost,
            'hundi_pending': dash['hundi_pending'],
            'note': 'Summary for trustee review. Full accounting in Odoo Finance.',
        }

    def plan_event(self, festival_id, expected_attendance):
        fest = self.env['rn.temple.festival'].browse(festival_id)
        meal_est = self.env['rn.temple.annadhanam.service'].estimate_ingredients(expected_attendance)
        volunteers_needed = max(5, int(expected_attendance / 50))
        return {
            'festival': fest.name,
            'expected_attendance': expected_attendance,
            'volunteers_suggested': volunteers_needed,
            'ingredients': meal_est,
            'note': 'Heuristic event plan from historical patterns.',
        }
