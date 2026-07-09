# -*- coding: utf-8 -*-

from odoo import fields, models


class RnJewelleryDashboardService(models.AbstractModel):
    _name = 'rn.jewellery.dashboard.service'
    _description = 'Jewellery Dashboard Service'

    def get_manufacturing_dashboard(self, company_id=None):
        company_id = company_id or self.env.company.id
        JobCard = self.env['rn.jewellery.job.card']
        cards = JobCard.search([('company_id', '=', company_id)])
        in_progress = cards.filtered(lambda c: c.state == 'in_progress')
        pending_orders = self.env['rn.jewellery.customer.order'].search_count([
            ('company_id', '=', company_id),
            ('state', 'in', ('confirmed', 'in_production')),
        ])
        total_wastage = sum(cards.mapped('wastage_weight'))
        return {
            'job_cards_active': len(in_progress),
            'pending_orders': pending_orders,
            'total_wastage_g': round(total_wastage, 3),
            'qc_pending': JobCard.search_count([
                ('company_id', '=', company_id),
                ('stage', '=', 'qc'),
            ]),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def get_retail_dashboard(self, company_id=None):
        company_id = company_id or self.env.company.id
        gold_rate = self.env['rn.jewellery.metal.rate'].get_latest_rate('gold', company_id)
        silver_rate = self.env['rn.jewellery.metal.rate'].get_latest_rate('silver', company_id)
        items = self.env['rn.jewellery.item.spec'].search([
            ('company_id', '=', company_id),
        ])
        repairs_open = self.env['rn.jewellery.repair.order'].search_count([
            ('company_id', '=', company_id),
            ('state', 'in', ('received', 'in_progress', 'ready')),
        ])
        return {
            'gold_rate': gold_rate,
            'silver_rate': silver_rate,
            'inventory_items': len(items),
            'inventory_value': round(sum(items.mapped('list_price_computed')), 2),
            'open_repairs': repairs_open,
            'custom_orders_pending': self.env['rn.jewellery.customer.order'].search_count([
                ('company_id', '=', company_id),
                ('state', 'in', ('confirmed', 'in_production', 'ready')),
            ]),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
