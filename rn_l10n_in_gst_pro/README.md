# India GST Compliance Pro

Commercial-grade GST compliance suite for Odoo 19 Community.

## Phase 1 (current)

- Installable module skeleton on top of `l10n_in`
- Security groups: Administrator, Manager, Accountant, Auditor, Readonly
- Models for periods, returns, invoice lines, HSN, documents, validations, reconciliation, settings, exports
- Service stubs for calculation, JSON/Excel/PDF, validation, reports, reconciliation, dashboard, scheduler
- OWL dashboard shell, wizards for GSTR-1 / 3B / 9, menus and settings
- Sample return periods and skeleton tests

## Architecture

```
Accounting documents
        |
        v
GST Calculation Service
        |
        +-- Validation Service
        +-- JSON / Excel / PDF Services
        +-- Reconciliation Service
        |
        v
GST Returns / Dashboard / Exports
```

## Installation

1. Ensure `l10n_in` is installed.
2. Add `rn_l10n_in_gst_pro` to the addons path.
3. Install **India GST Compliance Pro**.
4. Configure GST Settings and enable the module under Settings.

## Roadmap

| Phase | Deliverable |
|-------|-------------|
| 1 | Skeleton (done) |
| 2 | GST masters (HSN/SAC/rates/state codes) |
| 3 | Validation engine |
| 4 | GSTR-1 computation and JSON |
| 5 | GSTR-3B |
| 6 | GSTR-9 |
| 7 | HSN/B2B/B2C document summaries |
| 8 | Excel/PDF/CSV/JSON exports |
| 9 | OWL dashboard charts |
| 10 | Reconciliation, crons, tests, docs |

## License

OPL-1

## Support

info@armorait.com
