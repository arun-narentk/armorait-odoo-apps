# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionSite(models.Model):
    _name = 'rn.construction.site'
    _description = 'Construction Site'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    construction_project_id = fields.Many2one(
        'rn.construction.project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    location = fields.Char()
    site_engineer_id = fields.Many2one('hr.employee', string='Site Engineer')
    warehouse_id = fields.Many2one('stock.warehouse', string='Site Warehouse')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        related='construction_project_id.company_id',
        store=True,
        index=True,
    )
