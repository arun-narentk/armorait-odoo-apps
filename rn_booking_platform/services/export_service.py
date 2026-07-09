# -*- coding: utf-8 -*-
"""Export stubs for booking reports."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnBookingExportService(models.AbstractModel):
    """CSV/PDF/Excel export helpers."""

    _name = 'rn.booking.export.service'
    _description = 'Booking Export Service'

    def export_appointments_csv(self, appointments):
        lines = ['name,customer,service,start,state,amount']
        for appt in appointments:
            lines.append('%s,%s,%s,%s,%s,%s' % (
                appt.name,
                (appt.partner_id.display_name or '').replace(',', ' '),
                (appt.service_id.display_name or '').replace(',', ' '),
                appt.start_datetime,
                appt.state,
                appt.amount_total,
            ))
        return {
            'ok': True,
            'filename': 'appointments.csv',
            'datas': '\n'.join(lines),
        }
