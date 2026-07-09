# -*- coding: utf-8 -*-
"""CSV export for menu catalog."""

import base64
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnRestaurantExportService(models.AbstractModel):
    _name = 'rn.restaurant.export.service'
    _description = 'Restaurant Export Service'

    def export_menu_csv(self, restaurant):
        restaurant.ensure_one()
        lines = ['code,name,category,price,state,station']
        for item in restaurant.menu_category_ids.mapped('item_ids'):
            lines.append('%s,%s,%s,%s,%s,%s' % (
                item.code or '',
                (item.name or '').replace(',', ' '),
                item.category_id.name or '',
                item.list_price,
                item.state,
                item.kitchen_station or '',
            ))
        content = chr(10).join(lines)
        attachment = self.env['ir.attachment'].create({
            'name': 'menu_%s.csv' % (restaurant.code or restaurant.id),
            'type': 'binary',
            'datas': base64.b64encode(content.encode('utf-8')),
            'mimetype': 'text/csv',
        })
        _logger.info('Exported menu for restaurant %s', restaurant.id)
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
