# -*- coding: utf-8 -*-
"""Manual face verification wizard for HR officers."""

from odoo import fields, models


class RnHrVerifyFaceWizard(models.TransientModel):
    """Verify a live capture against an employee profile."""

    _name = 'rn.hr.verify.face.wizard'
    _description = 'Verify Employee Face'

    employee_id = fields.Many2one('hr.employee', required=True)
    face_id = fields.Many2one('rn.hr.employee.face', string='Face Profile')
    result = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('matched', 'Matched'),
            ('failed', 'Failed'),
        ],
        default='pending',
    )
    confidence = fields.Float(digits=(16, 4))

    def action_verify(self):
        """Run matcher once Phase 4 engine is available."""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Face Verification',
                'message': 'Live verification arrives in Phase 4.',
                'type': 'info',
                'sticky': False,
            },
        }
