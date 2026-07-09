# -*- coding: utf-8 -*-
"""Employee skills catalog."""

from odoo import fields, models


class RnHrmsSkill(models.Model):
    """Reusable skill tag for employees."""

    _name = 'rn.hrms.skill'
    _description = 'HRMS Skill'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
