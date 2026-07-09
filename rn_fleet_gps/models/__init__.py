# -*- coding: utf-8 -*-

from . import fleet_gps_device
from . import fleet_gps_location
from . import fleet_trip
from . import fleet_geofence
from . import fleet_alert
from . import fleet_driver_assignment
from . import fleet_fuel_log
from . import fleet_expense_log
from . import fleet_vehicle
from . import fleet_settings
from . import fleet_subscription
from . import res_config_settings

from ..services import provider_service
from ..services import location_service
from ..services import trip_service
from ..services import geofence_service
from ..services import alert_service
from ..services import fuel_service
from ..services import dashboard_service
from ..services import export_service
from ..services import scheduler_service
from ..services.providers import base
from ..services.providers import manual
from ..services.providers import traccar
