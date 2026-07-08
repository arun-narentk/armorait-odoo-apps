# -*- coding: utf-8 -*-
"""CSV export helpers for HMS directory data."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHmsExportService(models.AbstractModel):
    """Export patients and appointments."""

    _name = 'rn.hms.export.service'
    _description = 'HMS Export Service'

    def export_patients_csv(self, patients):
        lines = ['code,name,phone,email,blood_group,gender']
        for patient in patients:
            lines.append('%s,%s,%s,%s,%s,%s' % (
                patient.patient_code or '',
                (patient.name or '').replace(',', ' '),
                patient.phone or '',
                patient.email or '',
                patient.blood_group or '',
                patient.gender or '',
            ))
        return {
            'ok': True,
            'filename': 'patients.csv',
            'datas': chr(10).join(lines),
        }
