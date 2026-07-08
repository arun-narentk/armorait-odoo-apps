# CRM Ultimate Pro

Complete CRM enhancement suite for Odoo 19 Community.

## Phase 1 (current)

- Installable skeleton with service-layer architecture
- Lead score fields, badge, and basic scoring rules
- Duplicate scan stub (email match)
- Prediction provider interface (rule engine)
- Follow-up rules, reminders, activity templates
- Merge / bulk follow-up / bulk assign wizards
- OWL dashboard shell, menus, security, crons, tests

## Architecture

```
CRM Lead / Opportunity
        |
        v
Scoring / Prediction / Duplicate / Follow-up Services
        |
        v
Dashboard + Automation + APIs
```

## Installation

1. Install CRM and Sales.
2. Install **CRM Ultimate Pro**.
3. Open **CRM Ultimate > Configuration** and adjust settings.

## Roadmap

| Phase | Focus |
|-------|-------|
| 1 | Skeleton (done) |
| 2 | Full scoring formula engine |
| 3 | Follow-up automation + escalations |
| 4 | Smart duplicate / fuzzy matching |
| 5 | Merge with chatter/attachments |
| 6 | Enrichment provider abstraction |
| 7 | Pipeline SLA and aging |
| 8 | Email tracking |
| 9 | Full OWL analytics |
| 10 | Packaging, docs, Apps release |

## License

LGPL-3

## Support

info@armorait.com
