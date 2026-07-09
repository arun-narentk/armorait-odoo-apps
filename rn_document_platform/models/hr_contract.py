# -*- coding: utf-8 -*-

from odoo import models


class HrContract(models.Model):
    _inherit = ['hr.contract', 'rn.doc.platform.mixin']
