# -*- coding: utf-8 -*-

from odoo import models


class HrExpense(models.Model):
    _inherit = ['hr.expense', 'rn.workflow.mixin']
