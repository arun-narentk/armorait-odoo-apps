# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionPhase(models.Model):
    _name = 'rn.construction.phase'
    _description = 'Project Phase'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    construction_project_id = fields.Many2one(
        'rn.construction.project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    date_start = fields.Date()
    date_end = fields.Date()
    progress_pct = fields.Float(string='Progress %')
    company_id = fields.Many2one(related='construction_project_id.company_id', store=True)
