# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionInsightService(models.AbstractModel):
    _name = 'rn.construction.insight.service'
    _description = 'Construction AI Insight Service'

    def draft_daily_summary(self, log_id):
        log = self.env['rn.construction.site.daily.log'].browse(log_id)
        log.ensure_one()
        parts = [
            f'Site: {log.site_id.name}',
            f'Date: {log.log_date}',
            f'Labour on site: {log.labour_count or 0}',
        ]
        if log.weather:
            parts.append(f'Weather: {log.weather}')
        if log.incidents:
            parts.append(f'Incidents noted: yes')
        return ' | '.join(parts)

    def answer_project_question(self, question, project_id=None, company_id=None):
        q = (question or '').lower()
        company_id = company_id or self.env.company.id
        dash = self.env['rn.construction.dashboard.service'].get_management_dashboard(company_id)
        if project_id:
            project = self.env['rn.construction.project'].browse(project_id)
            compare = self.env['rn.construction.estimation.service'].compare_budget_vs_actual(project_id)
            if 'behind' in q or 'delay' in q or 'schedule' in q:
                late = project.date_end and project.date_end < fields.Date.context_today(self)
                return (
                    f'{project.name}: progress {project.progress_pct}%. '
                    f'{"Behind schedule." if late else "On track by dates."} '
                    f'Cost variance {compare["variance_pct"]}%.'
                )
            if 'cost' in q or 'budget' in q:
                return (
                    f'{project.name}: estimated {compare["estimated"]}, '
                    f'actual {compare["actual"]}, variance {compare["variance_pct"]}%.'
                )
        if 'delay' in q:
            return f'{dash["delayed_projects"]} projects appear delayed.'
        if 'issue' in q:
            return f'{dash["open_issues"]} open site issues company-wide.'
        if 'material' in q:
            return f'{dash["pending_mr"]} material requests pending approval or PO.'
        return (
            f'Active projects: {dash["active_projects"]}. '
            f'Budget variance: {dash["variance"]}. Open issues: {dash["open_issues"]}.'
        )

    def predict_cost_risk(self, project_id):
        compare = self.env['rn.construction.estimation.service'].compare_budget_vs_actual(project_id)
        risk = 'low'
        if compare['variance_pct'] > 15:
            risk = 'high'
        elif compare['variance_pct'] > 5:
            risk = 'medium'
        return {
            'risk_level': risk,
            'variance_pct': compare['variance_pct'],
            'note': 'Heuristic cost risk based on BOQ actual vs estimated.',
        }

    def forecast_material(self, site_id, product_id=None):
        domain = [('site_id', '=', site_id), ('state', 'in', ('submitted', 'approved', 'ordered'))]
        if product_id:
            domain.append(('product_id', '=', product_id))
        requests = self.env['rn.construction.material.request'].search(domain)
        qty = sum(requests.mapped('quantity'))
        return {
            'pending_qty': qty,
            'request_count': len(requests),
            'note': 'Forecast based on open material requests at site.',
        }
