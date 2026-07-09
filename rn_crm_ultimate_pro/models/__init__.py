# -*- coding: utf-8 -*-

from . import crm_score
from . import crm_prediction
from . import crm_duplicate
from . import crm_merge
from . import crm_followup
from . import crm_reminder
from . import crm_source
from . import crm_dashboard
from . import crm_activity
from . import crm_settings
from . import crm_lead
from . import res_config_settings

from ..services import lead_scoring_service
from ..services import prediction_service
from ..services import duplicate_service
from ..services import merge_service
from ..services import followup_service
from ..services import activity_service
from ..services import dashboard_service
from ..services import notification_service
from ..services import scheduler_service
