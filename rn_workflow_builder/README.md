# AI Automation Platform

ARMORA IT Technologies automation platform for Odoo 19 Community.

Zapier/Make style workflows native to Odoo business objects, permissions, and your product ecosystem.

## Business problem

Companies need automation (confirm SO, create project, low stock RFQ, overdue reminders) without custom Python per request. This module is the shared runtime for OCR, MES, WhatsApp, approvals, and AI Copilot.

## Phase 1 features

- Workflow definitions with trigger, condition, and action nodes
- Execution engine with run logs and retry queue
- Triggers: record created/updated, schedule, webhook, manual
- Conditions: field rules, domains, amount thresholds
- Actions: create/update records, email, notification, webhook, approval hook, AI summary
- Connector registry (Odoo, email, webhook, WhatsApp, MES, OCR ready)
- AI build from plain English (heuristic)
- AI validation and automation suggestions
- OWL designer and monitoring dashboard
- Webhook endpoint: `/rn_workflow/webhook/<token>`
- Hooks on `sale.order` and `purchase.order`

## Distinction from rn_approval_engine

| Module | Role |
|--------|------|
| `rn_approval_engine` | Multi-level document approvals |
| `rn_workflow_builder` | Full automation platform (triggers, branches, external actions) |

## Installation

1. Install Sales, Purchase, Accounting, HR, Inventory.
2. Install **AI Automation Platform**.
3. Assign **Workflow Designer** or **Workflow Manager** groups.

## Usage

- **Workflow Builder > Build from Text** for AI draft workflows
- **Workflows** to configure nodes and activate
- **Monitor** for success rate, failures, and suggestions

## Support

- https://www.armorait.com
- info@armorait.com

## License

OPL-1
