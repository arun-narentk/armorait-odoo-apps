# AI Copilot for Odoo: Architecture

Technical module name: `rn_ai_employee` (stable for upgrades and Apps Store history).

Product name: **AI Copilot for Odoo**, the enterprise intelligence layer above Odoo ERP.

## Vision

Users interact through chat, systray, and proactive briefings. Behind the UI, one orchestration layer routes questions to domain skills, enforces permissions, confirms writes, and logs every action.

```text
User (chat / systray / briefing)
        |
        v
Domain Agent (Sales / Finance / Executive)  [Phase 4]
        |
        v
Orchestrator (rn.ai.employee.service)
        |
   +----+----+---------+----------+
   |    |    |         |          |
Intent Memory LLM    Confirm    Audit
   |    |    |         |          |
   +----+----+---------+----------+
        |
   Skill Registry (tools/)
        |
   Odoo ORM (Sales, Finance, Inventory, CRM, Purchase)
```

## Layers

### 1. Interfaces

| Surface | Path | Role |
|---------|------|------|
| Form chat | `rn.ai.employee.chat` | Full conversations, suggested questions |
| Systray widget | `static/src/js/ai_employee_systray.js` | Quick copilot from any screen |
| Morning briefing | `cron_morning_briefing` | Proactive executive summary |

### 2. Orchestration (`models/rn_ai_employee_service.py`)

Pipeline per message:

1. Persist user message
2. Resolve tool via intent rules, session memory, or LLM
3. Queue confirmation for write skills (if enabled)
4. Execute skill through ORM
5. Write audit log
6. Update session memory
7. Explain result and attach action cards

### 3. Session memory (`services/memory_service.py`)

JSON context on `rn.ai.employee.chat.memory_context` stores recent tool results (model, record ids, headline). Enables follow-ups such as "email the first three customers" after "show pending quotations".

### 4. Skill registry (`tools/`)

| Package | Skills |
|---------|--------|
| `sales.py` | today_sales, pending_quotations, top_customers, ... |
| `accounting.py` | overdue_invoices, revenue_this_month, ... |
| `inventory.py` | low_stock, negative_stock, ... |
| `crm.py` | pipeline_revenue, find_customer, ... |
| `actions.py` | create_quotation, send_payment_reminders |
| `phase3_actions.py` | create_rfq, schedule_activity, send_partner_email, confirm_purchase_order, reserve_stock, morning_briefing |

Each skill extends `BaseAITool`:

- `is_write_tool`: marks data-changing skills
- `requires_confirmation`: gates execution behind user approval
- `execute()`: ORM-only business logic, returns structured dict

### 5. Security

| Control | Implementation |
|---------|----------------|
| Groups | `group_rn_ai_employee_user`, `group_rn_ai_employee_manager` |
| Record rules | Users see own chats and messages |
| ORM access | `check_access()` in every skill |
| Write confirmation | `rn.ai.employee.pending.action` + Confirm/Cancel cards |
| Audit trail | `rn.ai.employee.audit.log` on every execution |

### 6. LLM routing (`services/provider_factory.py`, `providers/`)

Rules-first intent detection. Optional OpenAI-compatible tool calling when API key is configured. Memory context is injected into the LLM system prompt.

## Data models

| Model | Purpose |
|-------|---------|
| `rn.ai.employee.agent` | Domain agent with scoped skills and persona |
| `rn.ai.employee.chat` | Conversation session |
| `rn.ai.employee.message` | User, assistant, tool, system messages |
| `rn.ai.employee.message.action` | Open list, open form, confirm write, cancel write |
| `rn.ai.employee.tool` | Database registry of active skills |
| `rn.ai.employee.pending.action` | Queued write awaiting confirmation |
| `rn.ai.employee.audit.log` | Immutable execution audit |
| `rn.ai.employee.suggestion` | Starter questions |

## Configuration (`ir.config_parameter`)

| Key | Default | Purpose |
|-----|---------|---------|
| `rn_ai_employee.enabled` | False | Master switch |
| `rn_ai_employee.use_llm` | True | LLM fallback routing |
| `rn_ai_employee.require_write_confirmation` | True | Confirmation gate |
| `rn_ai_employee.morning_briefing_enabled` | False | Proactive cron |

## Roadmap (post Phase 4)

| Phase | Focus |
|-------|-------|
| 5 | AI dashboard widgets, skills marketplace UI, knowledge base hooks |
| 6 | Workflow engine, approval center, WhatsApp/voice interfaces |
| 7 | Private LLM, on-prem packaging, SaaS metering |

## Shipped in Phase 4

Domain agents scope the existing skill registry without duplicating tools:

| Agent | Code | Focus |
|-------|------|-------|
| Sales AI | `sales` | Quotations, customers, CRM, pipeline |
| Finance AI | `finance` | Invoices, revenue, profit, collections |
| Executive AI | `executive` | Briefings, KPIs, approvals, cross-domain insight |

```text
User -> Domain Agent -> Scoped Skill Registry -> Orchestrator -> Odoo ORM
```

## Roadmap (historical)

| Phase | Focus |
|-------|-------|
| 4 | Domain agents (Sales AI, Finance AI, Executive AI) |

## Moat

The defensible layer is Odoo-aware orchestration: permissions, workflows, transactional safety, audit logs, and domain skills. The LLM is interchangeable.

## Company

ARMORA IT Technologies  
https://www.armorait.com  
info@armorait.com
