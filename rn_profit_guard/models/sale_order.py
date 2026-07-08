# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    margin_blocked = fields.Boolean(
        string='Margin Blocked',
        default=False,
        copy=False,
    )

    def action_confirm(self):
        if self.env.context.get('margin_override'):
            return super(SaleOrder, self).action_confirm()
        need_override_order = None
        for order in self:
            if order.state not in ('draft', 'sent'):
                continue
            danger_lines = order.order_line.filtered(
                lambda l: not l.display_type and l.margin_status == 'danger'
            )
            if danger_lines:
                need_override_order = need_override_order or order
        if need_override_order:
            need_override_order.margin_blocked = True
            return need_override_order._action_margin_override_wizard()
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            warning_lines = order.order_line.filtered(
                lambda l: not l.display_type and l.margin_status == 'warning'
            )
            for line in warning_lines:
                self.env['margin.violation.log'].create({
                    'order_id': order.id,
                    'order_line_id': line.id,
                    'margin_pct': line.real_margin,
                    'status': 'warning',
                    'reason': _('Order confirmed with margin warning.'),
                })
        return res

    def _action_margin_override_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Margin Override'),
            'res_model': 'margin.override.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def action_margin_override(self):
        """Open margin override wizard from button."""
        self.ensure_one()
        return self._action_margin_override_wizard()
