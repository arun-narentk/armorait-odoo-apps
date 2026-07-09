# -*- coding: utf-8 -*-
"""Restaurant overview KPIs for Phase 1."""

from odoo import fields, models


class RnRestaurantDashboardService(models.AbstractModel):
    _name = 'rn.restaurant.dashboard.service'
    _description = 'Restaurant Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        Restaurant = self.env['rn.restaurant']
        Branch = self.env['rn.restaurant.branch']
        Table = self.env['rn.restaurant.table']
        Item = self.env['rn.restaurant.menu.item']
        domain_co = [('company_id', '=', company_id)]
        cards = {
            'restaurants': Restaurant.search_count(domain_co),
            'branches': Branch.search_count(domain_co),
            'tables': Table.search_count(domain_co),
            'tables_available': Table.search_count(domain_co + [('state', '=', 'available')]),
            'tables_occupied': Table.search_count(domain_co + [('state', '=', 'occupied')]),
            'menu_items': Item.search_count(domain_co),
            'items_out': Item.search_count(domain_co + [('state', '=', 'out')]),
        }
        sub = self.env['rn.restaurant.subscription'].search([
            ('company_id', '=', company_id),
            ('state', 'in', ['trial', 'active']),
        ], limit=1)
        return {
            'cards': cards,
            'edition': sub.plan if sub else 'starter',
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
            'suite_hint': 'Install rn_restaurant_pos next for fast billing.',
        }
