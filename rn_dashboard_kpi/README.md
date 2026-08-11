# Dashboard KPI Studio

Technical name: `rn_dashboard_kpi`

Odoo 19 Community no-code / low-code dashboard builder by ARMORA IT Technologies.

Create dashboards from accessible Odoo models, configure KPI tiles and charts, arrange layouts, apply filters, drill into data, and (in later phases) import/export definitions and use optional AI-assisted generation.

## Status

Phase 2 complete: backend data model plus secure ORM data engine.

Implemented now:

- Full dashboard / item / filter / bookmark / item-filter fields
- Validation, company checks, SQL constraints and indexes
- Duplicate, export definition, create menu, toggle favorite
- Portable `get_dashboard_definition()` / `get_configuration()`
- Secure `get_data()` via `rn.kpi.dashboard.data.service` (count and grouped aggregations)
- Backend views, menus, demo data, commercial docs, Apps assets
- Model tests for validation, lifecycle, and data fetch

Not implemented yet (planned phases):

- Full chart renderers and drag/resize grid
- Item configurator wizard
- Import definition wizard, realtime bus, formulas, AI

## Architecture

```text
User / Manager
      |
      v
OWL Dashboard Action  -->  rn.kpi.dashboard (+ items, filters)
      |
      v
Data Engine (Phase 3) -->  ORM read_group / search_read (user rights)
      |
      v
Visualization Registry -->  Tile / Chart / List renderers
```

AI sits above configuration later, never as a bypass around validation or ORM security.

## Independence

This module is original ARMORA work. It does not copy proprietary code, assets, or branding from third-party dashboard apps.

It is also separate from `rn_dashboard_core` (MRP / analytics shell). Models use the `rn.kpi.dashboard*` namespace to avoid collisions with `rn.dashboard`.

## Installation

1. Add `armora` to your addons path.
2. Update the Apps list.
3. Install **Dashboard KPI Studio** (`rn_dashboard_kpi`).
4. Assign **Dashboard KPI Studio / User** or **Manager**.

## License

OPL-1

## Support

- ARMORA IT Technologies
- https://www.armorait.com
- info@armorait.com
