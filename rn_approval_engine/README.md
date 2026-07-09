# Workflow Approval Engine

ARMORA IT Technologies universal approval engine for Odoo 19 Community.

Configure multi-level and parallel approvals for purchase orders, vendor bills, and other documents without custom code per customer.

## Phase 1 features

- Workflow templates with unlimited stages
- Routing rules by amount, department, category, partner
- Sequential and parallel approval levels
- Conditional stage skip (amount threshold, new vendor legal review)
- Approval delegation
- Approve, reject, request changes with audit history
- Email notifications to pending approvers
- AI risk hints (amount vs history, duplicate warnings)
- OWL dashboard: pending, overdue, my queue
- Purchase order and vendor bill integration

## Installation

1. Add `rn_approval_engine` to your addons path.
2. Install **Workflow Approval Engine**.
3. Assign **Approval User**, **Approver**, or **Approval Manager** groups.
4. Create workflows and rules under **Approval Engine > Configuration**.

## Usage

1. Define a workflow for `purchase.order` or `account.move` with stages.
2. Add routing rules (e.g. amount ranges).
3. On a PO or vendor bill, click **Submit for Approval**.
4. Approvers act from **My Pending** or the request form.

## Support

- https://www.armorait.com
- info@armorait.com

## License

OPL-1
