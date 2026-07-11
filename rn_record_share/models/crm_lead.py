# -*- coding: utf-8 -*-

from odoo import models


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'rn.share.mixin']
