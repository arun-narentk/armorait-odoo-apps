# -*- coding: utf-8 -*-

from . import document_type
from . import document_template
from . import document
from . import document_version
from . import document_approval
from . import document_settings
from . import document_subscription
from . import res_config_settings

from ..services import placeholder_service
from ..services import template_service
from ..services import ai_generation_service
from ..services import document_render_service
from ..services import pdf_service
from ..services import docx_service
from ..services import approval_service
from ..services import signature_service
from ..services import version_service
from ..services import export_service
from ..services import dashboard_service
from ..services import notification_service
from ..services import scheduler_service
