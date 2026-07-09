# -*- coding: utf-8 -*-

from odoo import models


class RnJewelleryManufacturingService(models.AbstractModel):
    _name = 'rn.jewellery.manufacturing.service'
    _description = 'Manufacturing Service'

    def advance_stage(self, job_card_id, stage):
        card = self.env['rn.jewellery.job.card'].browse(job_card_id)
        card.write({'stage': stage})
        if stage == 'done':
            card.state = 'done'
        return True

    def karigar_productivity(self, karigar_id, company_id=None):
        company_id = company_id or self.env.company.id
        works = self.env['rn.jewellery.job.work'].search([
            ('karigar_id', '=', karigar_id),
            ('company_id', '=', company_id),
            ('state', 'in', ('received', 'qc_pass')),
        ])
        total_issue = sum(works.mapped('issue_weight'))
        total_wastage = sum(works.mapped('wastage_weight'))
        pct = round((total_wastage / total_issue) * 100, 2) if total_issue else 0.0
        return {
            'jobs_completed': len(works),
            'total_issue_weight': total_issue,
            'wastage_pct': pct,
        }
