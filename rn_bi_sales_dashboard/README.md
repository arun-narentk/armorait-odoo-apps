# BI Sales Dashboard (`rn_bi_sales_dashboard`)

Commercial Business Intelligence Sales Dashboard for Odoo 19 Community.

**Commercial name:** Business Intelligence Sales Dashboard  
**Tagline:** Advanced Analytics & KPIs for Odoo 19 Community

## Phase 1 (current)

Installable BI framework for sales:

- Service-oriented architecture (sales, chart, forecast, cache, export, target, scheduler)
- Configurable dashboards, widgets, KPI cards, filters, favorites, settings
- Sales targets with achievement %
- Snapshot model and daily cron stubs
- OWL dashboard client action with live KPI aggregation
- JSON API routes for KPIs, charts, forecast, targets
- Security groups: Readonly, Sales User, Sales Manager, Dashboard Manager
- Chart.js-ready datasets (canvas rendering in Phase 2)

## Architecture

```
Filters / Company context
        |
        v
Dashboard Service  ---> Cache Service
        |
        +--> Sales Service (orders / quotes)
        +--> Chart Service (series + top lists)
        +--> Target Service
        +--> Forecast Service
        |
        v
OWL Dashboard / API Controllers / Snapshots
```

Future shared core (`bi_dashboard_core`) can extract widgets, filters, cache, and export so CRM, Purchase, Inventory, HR, Accounting, and MRP dashboards reuse the same engine.

## Installation

1. Install Sales (`sale_management`) and CRM.
2. Install **BI Sales Dashboard**.
3. Open **Sales BI > Dashboard**.
4. Configure targets under **Sales BI > Targets** and settings under **Configuration**.

## Configuration

- Refresh interval and cache TTL: Settings app or BI Settings
- Default dashboard and widgets: Dashboard Layouts
- KPI enable/order/colors: KPI Cards

## Performance Notes

Phase 1 uses live `sale.order` aggregation with a process-local TTL cache. Daily snapshots prepare the path for materialized aggregations and background warm-up jobs in later phases.

## Roadmap

| Phase | Focus |
|-------|-------|
| 1 | Framework skeleton (done) |
| 2 | Chart.js widgets and layout polish |
| 3 | Full filter panel + drill-down |
| 4 | Target & forecast UX |
| 5 | Favorites / share / default layouts |
| 6 | Export PDF / Excel / CSV / PNG |
| 7 | Materialized SQL snapshots |
| 8 | Extract `bi_dashboard_core` |
| 9 | Suite BI suite packaging |

## License

OPL-1

## Support

info@armorait.com
