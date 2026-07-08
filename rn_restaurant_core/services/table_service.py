# -*- coding: utf-8 -*-
"""Table status helpers for POS / QR companions."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnRestaurantTableService(models.AbstractModel):
    _name = 'rn.restaurant.table.service'
    _description = 'Restaurant Table Service'

    def summary_by_branch(self, branch):
        branch.ensure_one()
        Table = self.env['rn.restaurant.table']
        domain = [('branch_id', '=', branch.id), ('active', '=', True)]
        return {
            'available': Table.search_count(domain + [('state', '=', 'available')]),
            'occupied': Table.search_count(domain + [('state', '=', 'occupied')]),
            'reserved': Table.search_count(domain + [('state', '=', 'reserved')]),
            'dirty': Table.search_count(domain + [('state', '=', 'dirty')]),
            'blocked': Table.search_count(domain + [('state', '=', 'blocked')]),
            'total': Table.search_count(domain),
        }

    def occupy(self, tables):
        tables.write({'state': 'occupied'})
        return True

    def release(self, tables):
        tables.write({'state': 'dirty'})
        return True
