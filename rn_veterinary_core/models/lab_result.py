# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVetLabResult(models.Model):
    _name = 'rn.vet.lab.result'
    _description = 'Lab Result'
    _order = 'test_date desc'

    name = fields.Char(required=True)
    pet_id = fields.Many2one('rn.vet.pet', required=True, ondelete='cascade', index=True)
    test_type = fields.Selection(
        [
            ('blood', 'Blood Test'),
            ('urine', 'Urine Analysis'),
            ('biochemistry', 'Biochemistry'),
            ('microbiology', 'Microbiology'),
            ('other', 'Other'),
        ],
        default='blood',
    )
    test_date = fields.Date(default=fields.Date.context_today, required=True)
    result_summary = fields.Text()
    attachment_ids = fields.Many2many('ir.attachment', string='Report Files')
    company_id = fields.Many2one(related='pet_id.company_id', store=True, index=True)
