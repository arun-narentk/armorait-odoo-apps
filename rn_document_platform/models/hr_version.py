# -*- coding: utf-8 -*-

from odoo import models


class HrVersion(models.Model):
    _inherit = ['hr.version', 'rn.doc.platform.mixin']
