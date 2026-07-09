# -*- coding: utf-8 -*-

from odoo import fields, models


class RnJewelleryJobIssueWizard(models.TransientModel):
    _name = 'rn.jewellery.job.issue.wizard'
    _description = 'Issue Gold to Karigar'

    job_card_id = fields.Many2one('rn.jewellery.job.card', required=True)
    karigar_id = fields.Many2one('rn.jewellery.karigar', required=True)
    issue_weight = fields.Float(required=True, digits=(16, 3))

    def action_issue(self):
        self.ensure_one()
        work_id = self.env['rn.jewellery.job.work.service'].issue_gold(
            self.job_card_id.id,
            self.karigar_id.id,
            self.issue_weight,
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.jewellery.job.work',
            'res_id': work_id,
            'view_mode': 'form',
            'target': 'current',
        }
