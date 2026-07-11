# -*- coding: utf-8 -*-

from odoo import models


class CrmLead(models.Model):
    _inherit = ['crm.lead', 'rn.timeline.mixin']

    def _timeline_state_field(self):
        return ''

    def write(self, vals):
        old_stages = {}
        if 'stage_id' in vals:
            old_stages = {lead.id: lead.stage_id.id for lead in self}
        result = super().write(vals)
        if 'stage_id' in vals:
            service = self.env['rn.timeline.service']
            for lead in self:
                previous_id = old_stages.get(lead.id)
                current_id = lead.stage_id.id
                if previous_id != current_id and lead.stage_id:
                    service.create_event(
                        lead,
                        lead.stage_id.name,
                        event_type='activity',
                        filter_category='general',
                    )
        return result
