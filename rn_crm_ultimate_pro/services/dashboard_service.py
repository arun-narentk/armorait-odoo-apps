# -*- coding: utf-8 -*-
"""CRM dashboard KPI aggregation."""

from odoo import models


class RnCrmDashboardService(models.AbstractModel):
    """Compute KPI cards for the OWL CRM dashboard."""

    _name = 'rn.crm.dashboard.service'
    _description = 'CRM Dashboard Service'

    def get_kpis(self, company_id=None):
        """Return live CRM KPI dictionary."""
        company_id = company_id or self.env.company.id
        Lead = self.env['crm.lead']
        domain = [('company_id', '=', company_id)]
        leads = Lead.search(domain + [('type', '=', 'lead')])
        opps = Lead.search(domain + [('type', '=', 'opportunity')])
        won = Lead.search(domain + [('probability', '=', 100)])
        lost = Lead.search(domain + [('active', '=', False), ('probability', '=', 0)])
        return {
            'leads': len(leads),
            'opportunities': len(opps),
            'won': len(won),
            'lost': len(lost),
            'revenue': sum(won.mapped('expected_revenue')),
            'forecast': sum(opps.mapped('expected_revenue')),
        }

    def create_snapshot(self):
        """Persist a dashboard snapshot row."""
        kpis = self.get_kpis()
        return self.env['rn.crm.dashboard.snapshot'].create({
            'name': 'Auto Snapshot',
            'lead_count': kpis['leads'],
            'opportunity_count': kpis['opportunities'],
            'won_count': kpis['won'],
            'lost_count': kpis['lost'],
            'revenue': kpis['revenue'],
            'forecast': kpis['forecast'],
        })
