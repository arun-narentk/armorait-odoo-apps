# -*- coding: utf-8 -*-

from odoo import models


class ResPartner(models.Model):
    _inherit = ['res.partner', 'rn.ai.email.mixin']
