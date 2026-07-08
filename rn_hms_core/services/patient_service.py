# -*- coding: utf-8 -*-
"""Patient registration helpers."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHmsPatientService(models.AbstractModel):
    """Create patients and optionally mirror a res.partner."""

    _name = 'rn.hms.patient.service'
    _description = 'HMS Patient Service'

    def register_patient(self, vals):
        """Create patient and linked partner when requested."""
        Partner = self.env['res.partner']
        partner_vals = {
            'name': vals.get('name'),
            'phone': vals.get('phone'),
            'email': vals.get('email'),
            'company_id': vals.get('company_id') or self.env.company.id,
        }
        if not vals.get('partner_id'):
            partner = Partner.create(partner_vals)
            vals = dict(vals, partner_id=partner.id)
        patient = self.env['rn.hms.patient'].create(vals)
        _logger.info('Registered patient %s', patient.patient_code)
        return patient
