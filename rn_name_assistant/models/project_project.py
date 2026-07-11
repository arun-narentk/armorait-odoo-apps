# -*- coding: utf-8 -*-

from odoo import models


class ProjectProject(models.Model):
    _inherit = ['project.project', 'rn.name.mixin']
