# -*- coding: utf-8 -*-

from odoo import models


class ProjectTask(models.Model):
    _inherit = ["project.task", "rn.color.mixin"]
