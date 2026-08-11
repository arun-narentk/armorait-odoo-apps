# Developer Guide

- Models: `rn.kpi.dashboard`, `rn.kpi.dashboard.item`, `rn.kpi.dashboard.filter`, `rn.kpi.dashboard.bookmark`, `rn.kpi.dashboard.item.filter`
- Service: `rn.kpi.dashboard.data.service` (ORM aggregations, no sudo data reads)
- Client action tag: `rn_dashboard_kpi.dashboard`
- Assets: SCSS, visualization registry, dashboard service, OWL action
- Extend by adding renderers under `static/src/components/` and registering them in the visualization registry

ARMORA IT Technologies | https://www.armorait.com | info@armorait.com
