# Developer Guide

Implement a connector by inheriting `rn.fleet.gps.provider.base` and registering it in `PROVIDER_REGISTRY` / companion module overrides.

Ingest path: provider/API -> `rn.fleet.location.service.ingest` -> trip / geofence / alert engines.

ARMORA IT Technologies | https://www.armorait.com
