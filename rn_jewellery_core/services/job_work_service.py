# -*- coding: utf-8 -*-

from odoo import models


class RnJewelleryJobWorkService(models.AbstractModel):
    _name = 'rn.jewellery.job.work.service'
    _description = 'Job Work Service'

    def issue_gold(self, job_card_id, karigar_id, issue_weight):
        card = self.env['rn.jewellery.job.card'].browse(job_card_id)
        work = self.env['rn.jewellery.job.work'].create({
            'job_card_id': job_card_id,
            'karigar_id': karigar_id,
            'issue_weight': issue_weight,
            'state': 'issued',
        })
        card.write({'state': 'in_progress', 'karigar_id': karigar_id, 'issue_weight': issue_weight})
        return work.id

    def receive_finished(self, job_work_id, receive_weight, qc_pass=True):
        work = self.env['rn.jewellery.job.work'].browse(job_work_id)
        work.write({
            'receive_weight': receive_weight,
            'state': 'qc_pass' if qc_pass else 'qc_fail',
        })
        card = work.job_card_id
        card.write({
            'receive_weight': receive_weight,
            'state': 'done' if qc_pass else 'in_progress',
            'stage': 'done' if qc_pass else 'qc',
        })
        return True
