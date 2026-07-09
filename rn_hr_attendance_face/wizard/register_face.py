# -*- coding: utf-8 -*-
"""Multi-angle face registration wizard."""

from odoo import fields, models


class RnHrRegisterFaceWizard(models.TransientModel):
    """Capture enrollment images and store embedding (Phases 2-3)."""

    _name = 'rn.hr.register.face.wizard'
    _description = 'Register Employee Face'

    employee_id = fields.Many2one('hr.employee', required=True)
    face_id = fields.Many2one('rn.hr.employee.face', string='Face Profile')
    capture_count = fields.Integer(string='Captures', default=0)
    target_count = fields.Integer(string='Target Captures', default=10)
    pose = fields.Selection(
        selection=[
            ('front', 'Front'),
            ('left', 'Left'),
            ('right', 'Right'),
            ('up', 'Up'),
            ('down', 'Down'),
            ('smile', 'Smile'),
            ('no_smile', 'No Smile'),
            ('glasses', 'Glasses'),
            ('no_glasses', 'Without Glasses'),
        ],
        default='front',
    )
    notes = fields.Text()

    def action_open_capture(self):
        """Placeholder until OWL capture widget lands in Phase 2."""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Face Registration',
                'message': 'Multi-angle capture UI arrives in Phase 2.',
                'type': 'info',
                'sticky': False,
            },
        }

    def action_finalize(self):
        """Create or update face profile after captures (Phase 3)."""
        self.ensure_one()
        Face = self.env['rn.hr.employee.face']
        face = self.face_id
        if not face:
            face = Face.search([('employee_id', '=', self.employee_id.id)], limit=1)
        vals = {
            'employee_id': self.employee_id.id,
            'photo_count': self.capture_count,
            'status': 'draft',
        }
        if face:
            face.write(vals)
        else:
            face = Face.create(vals)
        return {'type': 'ir.actions.act_window_close'}
