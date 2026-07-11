# -*- coding: utf-8 -*-

from odoo import _, models


class AccountMove(models.Model):
    _inherit = ['account.move', 'rn.timeline.mixin']

    def _timeline_created_label(self):
        return _('Draft Invoice')

    def _timeline_created_filter_category(self):
        return 'financial'
