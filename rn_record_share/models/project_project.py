# -*- coding: utf-8 -*-

from odoo import models


class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'rn.share.mixin']
