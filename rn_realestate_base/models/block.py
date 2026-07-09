# -*- coding: utf-8 -*-
"""Tower / block within a project."""

from odoo import fields, models


class RnRealestateBlock(models.Model):
    """Tower, block, or wing in a housing project."""

    _name = 'rn.realestate.block'
    _description = 'Project Block / Tower'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    project_id = fields.Many2one(
        'rn.realestate.project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    developer_id = fields.Many2one(
        related='project_id.developer_id',
        store=True,
        index=True,
    )
    total_floors = fields.Integer(string='Total Floors')
    unit_ids = fields.One2many('rn.realestate.unit', 'block_id', string='Units')
    unit_count = fields.Integer(compute='_compute_unit_count')
    company_id = fields.Many2one(
        related='project_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()

    def _compute_unit_count(self):
        for block in self:
            block.unit_count = len(block.unit_ids)
