# -*- coding: utf-8 -*-
"""Quality inspection workflow service."""

from odoo import models
from odoo.exceptions import UserError


class RnMesQualityService(models.AbstractModel):
    """Create and complete inspections from checklists."""

    _name = 'rn.mes.quality.service'
    _description = 'MES Quality Service'

    def create_from_checklist(self, checklist_id, workorder_id=None, session_id=None, operator_id=None):
        checklist = self.env['rn.mes.quality.checklist'].browse(checklist_id)
        if not checklist.exists():
            raise UserError('Checklist not found.')
        lines = []
        for line in checklist.line_ids:
            lines.append((0, 0, {
                'sequence': line.sequence,
                'name': line.name,
                'check_type': line.check_type,
            }))
        inspection = self.env['rn.mes.quality.inspection'].create({
            'checklist_id': checklist.id,
            'workorder_id': workorder_id,
            'session_id': session_id,
            'operator_id': operator_id,
            'state': 'in_progress',
            'line_ids': lines,
        })
        return inspection.id

    def submit_results(self, inspection_id, line_results):
        inspection = self.env['rn.mes.quality.inspection'].browse(inspection_id)
        if not inspection.exists():
            raise UserError('Inspection not found.')
        line_map = {line.id: line for line in inspection.line_ids}
        failed = False
        for item in line_results or []:
            line = line_map.get(item.get('line_id'))
            if not line:
                continue
            vals = {
                'result': item.get('result'),
                'measured_value': item.get('measured_value', 0.0),
                'note': item.get('note', ''),
            }
            line.write(vals)
            if vals['result'] == 'fail':
                failed = True
        inspection.state = 'fail' if failed else 'pass'
        return inspection.state
