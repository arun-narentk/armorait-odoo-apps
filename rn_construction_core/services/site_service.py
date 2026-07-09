# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionSiteService(models.AbstractModel):
    _name = 'rn.construction.site.service'
    _description = 'Site Operations Service'

    def log_daily_progress(self, site_id, note, labour_count=0, weather=None):
        site = self.env['rn.construction.site'].browse(site_id)
        site.ensure_one()
        log = self.env['rn.construction.site.daily.log'].create({
            'name': f'{site.name} - {fields.Date.context_today(self)}',
            'site_id': site.id,
            'log_date': fields.Date.context_today(self),
            'progress_note': note,
            'labour_count': labour_count,
            'weather': weather,
        })
        return log.id

    def open_issues_count(self, site_id=None, company_id=None):
        domain = [('state', '!=', 'resolved')]
        if site_id:
            domain.append(('site_id', '=', site_id))
        if company_id:
            domain.append(('company_id', '=', company_id))
        return self.env['rn.construction.site.issue'].search_count(domain)

    def pending_material_requests(self, site_id=None, company_id=None):
        domain = [('state', 'in', ('submitted', 'approved'))]
        if site_id:
            domain.append(('site_id', '=', site_id))
        if company_id:
            domain.append(('company_id', '=', company_id))
        return self.env['rn.construction.material.request'].search_count(domain)
