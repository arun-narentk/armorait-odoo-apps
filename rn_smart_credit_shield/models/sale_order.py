# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    credit_blocked = fields.Boolean(
        string='Credit Blocked',
        default=False,
        copy=False,
        help='Confirmation was blocked due to credit risk; use Manager Override to confirm.',
    )

    def action_confirm(self):
        need_override_order = None
        ICP = self.env['ir.config_parameter'].sudo()
        enable_auto_block = ICP.get_param('rn_smart_credit_shield.enable_auto_block', 'True') == 'True'
        for order in self:
            if order.state in ('sale', 'cancel'):
                continue
            partner = order.partner_id.commercial_partner_id
            level = partner.credit_risk_level
            if enable_auto_block and level == 'critical' and not self.env.context.get('credit_override'):
                self.env['credit.violation.log'].log_block(order, risk_level='critical')
                raise UserError(
                    _(
                        'Credit risk is Critical for %s. Confirmation is blocked. '
                        'Use "Credit Override" from the Action menu to confirm with approval.'
                    ) % partner.name
                )
            if enable_auto_block and level == 'high' and not self.env.context.get('credit_override'):
                need_override_order = need_override_order or order
        if need_override_order:
            need_override_order.credit_blocked = True
            self.env['credit.violation.log'].log_block(
                need_override_order,
                risk_level='high',
                override_by=None,
                override_reason=None,
            )
            return need_override_order._action_confirm_with_credit_warning()
        return super(SaleOrder, self).action_confirm()

    def _action_confirm_with_credit_warning(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Credit Risk Warning'),
            'res_model': 'credit.override.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_reason': _('High credit risk – confirmation requires approval.'),
            },
        }

    def action_credit_override(self):
        """Open override wizard from button."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Credit Override'),
            'res_model': 'credit.override.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }
