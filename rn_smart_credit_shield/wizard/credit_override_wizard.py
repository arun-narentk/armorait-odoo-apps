# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class CreditOverrideWizard(models.TransientModel):
    _name = 'credit.override.wizard'
    _description = 'Credit Override Approval'

    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    reason = fields.Text(string='Reason', required=True)
    approval_by = fields.Many2one(
        'res.users',
        string='Approved By',
        default=lambda self: self.env.user,
        required=True,
    )

    def action_confirm_override(self):
        self.ensure_one()
        if not self.env.user.has_group('rn_smart_credit_shield.group_credit_manager'):
            raise AccessError(_('Only a Credit Manager can confirm a credit override.'))
        order = self.order_id
        if order.state in ('sale', 'cancel'):
            return {'type': 'ir.actions.act_window_close'}
        level = order.partner_id.commercial_partner_id.credit_risk_level or 'high'
        self.env['credit.violation.log'].log_block(
            order,
            risk_level=level,
            override_by=self.approval_by,
            override_reason=self.reason or '',
        )
        body = _(
            'Credit override: %s\nApproved by: %s\nReason: %s'
        ) % (level, self.approval_by.name, self.reason or '')
        order.with_context(credit_override=True).action_confirm()
        order.credit_blocked = False
        order.message_post(body=body, message_type='notification', subtype_xmlid='mail.mt_note')
        return {'type': 'ir.actions.act_window_close'}
