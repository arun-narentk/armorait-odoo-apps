# -*- coding: utf-8 -*-

from odoo import models


class AccountMove(models.Model):
    _inherit = ['account.move', 'rn.ai.email.mixin']
