# -*- coding: utf-8 -*-
"""Automated employee onboarding checklist stubs."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrmsOnboardingService(models.AbstractModel):
    """Run onboarding steps for a new employee."""

    _name = 'rn.hrms.onboarding.service'
    _description = 'HRMS Onboarding Service'

    def onboard_employee(self, employee):
        """Assign code, set joining date, and mark onboarded."""
        employee.ensure_one()
        self.env['rn.hrms.employee.service'].assign_employee_code(employee)
        self.env['rn.hrms.employee.service'].mark_onboarded(employee)
        employee.message_post(body='Employee onboarding completed via HRMS Core.')
        _logger.info('Onboarded employee %s', employee.name)
        return True
