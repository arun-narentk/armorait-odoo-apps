# -*- coding: utf-8 -*-
"""Wizard to merge selected leads."""

from odoo import fields, models
from odoo.exceptions import UserError


class RnCrmMergeLeadWizard(models.TransientModel):
    """Merge secondary leads into a master lead."""

    _name = 'rn.crm.merge.lead.wizard'
    _description = 'Merge Leads'

    master_lead_id = fields.Many2one('crm.lead', required=True)
    lead_ids = fields.Many2many('crm.lead', string='Leads to Merge')
    preserve_chatter = fields.Boolean(default=True)
    preserve_activities = fields.Boolean(default=True)
    preserve_attachments = fields.Boolean(default=True)

    def action_merge(self):
        self.ensure_one()
        others = self.lead_ids - self.master_lead_id
        if not others:
            raise UserError('Select at least one other lead to merge.')
        self.env['rn.crm.merge.service'].merge_leads(
            self.master_lead_id,
            others,
            preserve={
                'chatter': self.preserve_chatter,
                'activities': self.preserve_activities,
                'attachments': self.preserve_attachments,
            },
        )
        return {'type': 'ir.actions.act_window_close'}
