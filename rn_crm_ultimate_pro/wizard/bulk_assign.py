# -*- coding: utf-8 -*-
"""Bulk / round-robin lead assignment wizard."""

from odoo import fields, models


class RnCrmBulkAssignWizard(models.TransientModel):
    """Assign leads to salespeople."""

    _name = 'rn.crm.bulk.assign.wizard'
    _description = 'Bulk Assign Leads'

    lead_ids = fields.Many2many('crm.lead', string='Leads')
    user_ids = fields.Many2many('res.users', string='Salespersons')
    mode = fields.Selection(
        selection=[('single', 'Assign All to One'), ('round_robin', 'Round Robin')],
        default='round_robin',
        required=True,
    )
    user_id = fields.Many2one('res.users', string='Salesperson')

    def action_assign(self):
        self.ensure_one()
        if self.mode == 'single' and self.user_id:
            self.lead_ids.write({'user_id': self.user_id.id})
            return {'type': 'ir.actions.act_window_close'}
        users = self.user_ids or self.env.ref('base.group_user').users
        if not users:
            return {'type': 'ir.actions.act_window_close'}
        user_list = list(users)
        for index, lead in enumerate(self.lead_ids):
            lead.user_id = user_list[index % len(user_list)].id
        return {'type': 'ir.actions.act_window_close'}
