# -*- coding: utf-8 -*-

from odoo import models


class RnJewelleryInsightService(models.AbstractModel):
    _name = 'rn.jewellery.insight.service'
    _description = 'Jewellery AI Insight Service'

    def search_inventory(self, query, max_price=None, company_id=None):
        company_id = company_id or self.env.company.id
        domain = [('company_id', '=', company_id)]
        q = (query or '').lower()
        if 'necklace' in q or 'bridal' in q:
            domain.append(('collection', 'ilike', 'bridal'))
        if 'lightweight' in q or 'light' in q:
            domain.append(('net_weight', '<', 15))
        items = self.env['rn.jewellery.item.spec'].search(domain, limit=20)
        if max_price:
            items = items.filtered(lambda i: i.list_price_computed <= max_price)
        return [{
            'name': i.name,
            'collection': i.collection or '',
            'net_weight': i.net_weight,
            'price': i.list_price_computed,
            'barcode': i.barcode or '',
        } for i in items[:10]]

    def sales_assistant_answer(self, question, company_id=None):
        q = (question or '').lower()
        if 'under' in q or 'below' in q or 'lakh' in q:
            max_price = 200000 if '2 lakh' in q or '2lakh' in q else None
            items = self.search_inventory(q, max_price=max_price, company_id=company_id)
            if items:
                return f'Found {len(items)} matching items. Top: {items[0]["name"]} at {items[0]["price"]}.'
            return 'No matching inventory found for that criteria.'
        dash = self.env['rn.jewellery.dashboard.service'].get_retail_dashboard(company_id)
        if 'gold rate' in q or 'rate' in q:
            return f'Today gold rate: {dash["gold_rate"]} per gram. Silver: {dash["silver_rate"]}.'
        return f'Inventory: {dash["inventory_items"]} items. Value: {dash["inventory_value"]}.'

    def customer_insights(self, company_id=None):
        company_id = company_id or self.env.company.id
        profiles = self.env['rn.jewellery.customer.profile'].search([
            ('company_id', '=', company_id),
        ], order='loyalty_points desc', limit=5)
        dormant = self.env['rn.jewellery.customer.profile'].search([
            ('company_id', '=', company_id),
            ('last_purchase_date', '=', False),
        ], limit=5)
        return {
            'top_customers': [{'name': p.partner_id.name, 'points': p.loyalty_points} for p in profiles],
            'dormant_count': len(dormant),
            'note': 'Heuristic customer segmentation.',
        }

    def fraud_flags(self, company_id=None):
        company_id = company_id or self.env.company.id
        flags = []
        cards = self.env['rn.jewellery.job.card'].search([
            ('company_id', '=', company_id),
            ('issue_weight', '>', 0),
        ])
        for card in cards:
            if card.issue_weight and card.wastage_weight / card.issue_weight > 0.15:
                flags.append({
                    'type': 'high_wastage',
                    'ref': card.name,
                    'detail': f'Wastage {card.wastage_weight}g on issue {card.issue_weight}g',
                })
        return {
            'flag_count': len(flags),
            'flags': flags[:10],
            'note': 'Heuristic fraud and variance detection.',
        }

    def demand_forecast(self, category=None):
        return {
            'category': category or 'bridal',
            'forecast_note': 'Higher demand expected in wedding season and festival months.',
            'suggested_action': 'Review gold rate and replenish fast-moving bridal stock.',
        }
