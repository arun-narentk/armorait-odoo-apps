# -*- coding: utf-8 -*-

from . import hms_department
from . import hms_doctor
from . import hms_patient
from . import hms_ward
from . import hms_bed
from . import hms_appointment
from . import hms_settings
from . import hms_subscription
from . import res_config_settings

from ..services import patient_service
from ..services import appointment_service
from ..services import bed_service
from ..services import notification_service
from ..services import dashboard_service
from ..services import export_service
from ..services import scheduler_service
