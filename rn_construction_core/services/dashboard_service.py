# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionDashboardService(models.AbstractModel):
    _name = 'rn.construction.dashboard.service'
    _description = 'Construction Dashboard Service'

    def get_management_dashboard(self, company_id=None):
        company_id = company_id or self.env.company.id
        Project = self.env['rn.construction.project']
        projects = Project.search([('company_id', '=', company_id)])
        active = projects.filtered(lambda p: p.state == 'active')
        delayed = projects.filtered(
            lambda p: p.date_end and p.date_end < fields.Date.context_today(self) and p.state == 'active'
        )
        total_budget = sum(projects.mapped('budget_total'))
        total_actual = sum(projects.mapped('actual_cost'))
        return {
            'project_count': len(projects),
            'active_projects': len(active),
            'delayed_projects': len(delayed),
            'budget_total': total_budget,
            'actual_cost': total_actual,
            'variance': total_actual - sum(projects.mapped('estimated_cost')),
            'open_issues': self.env['rn.construction.site.service'].open_issues_count(company_id=company_id),
            'pending_mr': self.env['rn.construction.site.service'].pending_material_requests(company_id=company_id),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def get_site_engineer_dashboard(self, employee_id=None, company_id=None):
        company_id = company_id or self.env.company.id
        Site = self.env['rn.construction.site']
        domain = [('company_id', '=', company_id), ('active', '=', True)]
        if employee_id:
            domain.append(('site_engineer_id', '=', employee_id))
        sites = Site.search(domain)
        site_ids = sites.ids
        return {
            'site_count': len(sites),
            'open_issues': self.env['rn.construction.site.issue'].search_count([
                ('site_id', 'in', site_ids),
                ('state', '!=', 'resolved'),
            ]) if site_ids else 0,
            'pending_mr': self.env['rn.construction.material.request'].search_count([
                ('site_id', 'in', site_ids),
                ('state', 'in', ('draft', 'submitted')),
            ]) if site_ids else 0,
            'logs_today': self.env['rn.construction.site.daily.log'].search_count([
                ('site_id', 'in', site_ids),
                ('log_date', '=', fields.Date.context_today(self)),
            ]) if site_ids else 0,
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
