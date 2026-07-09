# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    construction_project_id = fields.Many2one('rn.construction.project', string='Construction Project')
