# ARMORA Fleet GPS

Provider-agnostic fleet GPS tracking for Odoo 19 Community.

## Overview

`rn_fleet_gps` extends standard Fleet with device management, live location ingest, trips, geofencing, fuel and expense logs, alerts, OWL live board, and a connector framework for Traccar and other GPS vendors.

## Business Problem

GPS hardware, expenses, drivers, and maintenance often live in separate tools. This module gives logistics, transport, school buses, and field-service fleets one operational layer on Odoo Community.

## Phase 1 Features

- GPS devices with provider registry (manual, Traccar stub, others ready for add-ons)
- Location ingest API and wizard
- Trip engine with distance and auto-close
- Geofences and overspeed / offline alerts
- Fuel and expense logs, driver assignments
- Fleet vehicle GPS tab and live board
- REST JSON endpoints under `/api/rn_fleet/v1/*`

## Suite

```
rn_fleet_gps
├── rn_fleet_dashboard
├── rn_fleet_gps_traccar / teltonika / gt06 / wialon / ...
├── rn_fleet_fuel
├── rn_fleet_driver
├── rn_fleet_route_optimizer
├── rn_fleet_maintenance_ai
└── rn_fleet_mobile
```

## Pricing

| Package | USD |
|---|---|
| Base Module | 49.99 |
| GPS Connector Add-ons | 29.99 to 99.99 |
| Fleet Dashboard | 39.99 |
| Complete Suite Bundle | 199 to 299 |

## Installation

1. Install Fleet and HR.
2. Update Apps List and install **ARMORA Fleet GPS**.
3. Create a GPS device, assign a vehicle, push a point or connect a provider.

## Support

ARMORA IT Technologies  
Website: https://www.armorait.com  
Support: info@armorait.com

## License

OPL-1
