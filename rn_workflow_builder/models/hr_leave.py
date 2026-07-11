# -*- coding: utf-8 -*-

from odoo import models


class HrLeave(models.Model):
    _inherit = ['hr.leave', 'rn.workflow.mixin']
