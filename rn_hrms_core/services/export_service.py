# -*- coding: utf-8 -*-
"""Export helpers for HRMS directory reports."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrmsExportService(models.AbstractModel):
    """CSV export for employee directory."""

    _name = 'rn.hrms.export.service'
    _description = 'HRMS Export Service'

    def export_employee_directory_csv(self, employees):
        lines = ['code,name,department,branch,designation,work_email']
        for emp in employees:
            lines.append('%s,%s,%s,%s,%s,%s' % (
                emp.rn_hrms_employee_code or '',
                (emp.name or '').replace(',', ' '),
                (emp.department_id.name or '').replace(',', ' '),
                (emp.rn_hrms_branch_id.name or '').replace(',', ' '),
                (emp.rn_hrms_designation_id.name or '').replace(',', ' '),
                emp.work_email or '',
            ))
        return {
            'ok': True,
            'filename': 'employee_directory.csv',
            'datas': '\n'.join(lines),
        }
