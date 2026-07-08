# AI Copilot for Odoo 19 Community

**Market name:** AI Copilot for Odoo  
**Technical module name:** `ai_employee`

Business assistant for everyday Odoo questions. Phase 1 delivers read-only analytics managers actually ask every day.

## What managers can ask (Phase 1)

### Sales
- Show today's sales
- Show pending quotations
- Top customers
- Best selling products
- Lost quotations

### Accounting
- Overdue invoices
- Customer balance
- Revenue this month
- Expenses this month
- Profit this month
- Why did revenue decrease?

### Inventory
- Negative stock
- Low stock
- Products not moved
- Inventory valuation

### CRM
- Top opportunities
- Lost leads
- Follow-up overdue
- Expected pipeline revenue

## Product flow

```
Manager question
    -> Intent detection
    -> Analytics tool (ORM only)
    -> Structured result
    -> Plain-language explanation
    -> Action cards (Open List, Create Activity)
```

The LLM is **not** responsible for business logic in Phase 1. Tools own the data. The assistant explains results and offers next steps.

## Installation

1. Add `ai_employee` to your addons path.
2. Update the apps list.
3. Install **AI Copilot for Odoo**.

## Configuration

1. Open **AI Copilot > Settings**.
2. Enable AI Copilot.
3. Optional provider fields are reserved for Phase 2 live LLM polish.

## Usage

1. Open **AI Copilot > Ask Copilot**.
2. Pick a suggested question or type your own.
3. Click **Send**.
4. Open the assistant answer and use action cards such as **Open List**.

## Screenshots (placeholders)

| File | Description |
|------|-------------|
| `static/description/screenshot_chat.png` | Chat with suggested questions |
| `static/description/screenshot_actions.png` | Answer with action cards |
| `static/description/screenshot_settings.png` | Settings panel |

## Roadmap

### Phase 1 - Analytics (current)
Read-only insights across Sales, Accounting, Inventory, and CRM.

### Phase 2 - Guided Actions
Controlled write operations with confirmation:
- Create quotations (customer -> product -> confirm)
- Create leads and purchase orders
- Draft emails and reminders

### Phase 3 - AI Everywhere
- AI sidebar on every page
- Context-aware Explain buttons on list views
- Dashboard insights

### Phase 4 - Automation
- Scheduled AI reports
- Workflow routing
- Email automation

## Testing

```bash
./odoo-bin -c odoo.conf -d your_db --test-tags=ai_employee --stop-after-init
```

## License

LGPL-3

## Author

ARMORAIT - https://www.armorait.com
