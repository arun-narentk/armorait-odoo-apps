# -*- coding: utf-8 -*-
from odoo import models


class Base(models.AbstractModel):
    _name = 'base'
    _inherit = ['base', 'rn.qr.mixin']
