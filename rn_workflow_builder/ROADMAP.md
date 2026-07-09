# AI Workflow Builder Roadmap

## Phase 1 (current)

- Workflow model and node graph
- Execution engine and audit logs
- Core triggers, conditions, actions
- AI text-to-workflow draft
- Monitoring dashboard
- Webhook ingress

## Phase 2

- Drag-and-drop visual canvas
- External connectors (WhatsApp, Slack, Teams, Razorpay)
- Scheduled cron runner
- Enhanced error handling and dead-letter queue

## Phase 3

- LLM-powered workflow generation
- AI optimization from execution history
- AI loop and permission diagnostics
- Workflow template marketplace

## Phase 4

- Versioning and collaborative editing
- Multi-tenant SaaS execution tier
- Published connector SDK for armora modules

## Ecosystem integration

Other ARMORA modules should publish events and actions here:

- `rn_ai_invoice_ocr`: Invoice processed trigger
- `rn_mes_core`: Machine stopped trigger
- `rn_whatsapp_connector`: Send WhatsApp action
- `rn_document_platform`: Signing completed trigger
- `rn_approval_engine`: Start approval action
