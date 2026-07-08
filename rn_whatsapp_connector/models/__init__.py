# -*- coding: utf-8 -*-

from . import whatsapp_account
from . import whatsapp_message
from . import whatsapp_template
from . import whatsapp_attachment
from . import whatsapp_webhook
from . import whatsapp_history
from . import whatsapp_automation
from . import whatsapp_subscription
from . import res_config_settings
from . import sale_order
from . import account_move
from . import stock_picking

from ..services import api_service
from ..services import provider_service
from ..services import message_service
from ..services import queue_service
from ..services import automation_service
from ..services import template_service
from ..services import dashboard_service
from ..services import pdf_service
from ..services import scheduler_service
from ..services import webhook_service
from ..services.providers import base
from ..services.providers import meta_cloud
from ..services.providers import twilio
from ..services.providers import dialog360
from ..services.providers import gupshup
from ..services.providers import interakt
