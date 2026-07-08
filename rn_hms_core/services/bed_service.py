# -*- coding: utf-8 -*-
"""Bed allocation helpers for IPD foundation."""

import logging

from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnHmsBedService(models.AbstractModel):
    """Allocate and release beds."""

    _name = 'rn.hms.bed.service'
    _description = 'HMS Bed Service'

    def allocate(self, bed, patient):
        bed.ensure_one()
        patient.ensure_one()
        if bed.state != 'available':
            raise UserError('Bed %s is not available.' % bed.display_name)
        bed.write({'state': 'occupied', 'patient_id': patient.id})
        _logger.info('Allocated bed %s to %s', bed.name, patient.patient_code)
        return True

    def release(self, bed, cleaning=True):
        bed.ensure_one()
        bed.write({
            'state': 'cleaning' if cleaning else 'available',
            'patient_id': False,
        })
        return True

    def occupancy_stats(self, company_id=None):
        company_id = company_id or self.env.company.id
        beds = self.env['rn.hms.bed'].search([('company_id', '=', company_id)])
        total = len(beds)
        occupied = len(beds.filtered(lambda b: b.state == 'occupied'))
        return {
            'total': total,
            'occupied': occupied,
            'available': len(beds.filtered(lambda b: b.state == 'available')),
            'occupancy_pct': (occupied / total * 100.0) if total else 0.0,
        }
