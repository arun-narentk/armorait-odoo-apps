"""Extra demo data: vendor bills (payables + costs) and overdue receivables.

Run with:
    odoo-bin shell -d rn --no-http < this_file.py

Adds posted vendor bills across the last 6 months (some paid, some open) so the
"Vendor Payables" and "Monthly Profit Estimate" KPIs show real figures, and
marks older unpaid customer invoices as past due so the "Overdue Payments"
KPI is populated.
"""

from datetime import date

from dateutil.relativedelta import relativedelta

company = env.company
today = date.today()
month_start = today.replace(day=1)
first_month = month_start - relativedelta(months=5)

purchase_tax = env["account.tax"].search(
    [("type_tax_use", "=", "purchase"), ("amount", "=", 15)], limit=1
)
purchase_journal = env["account.journal"].search(
    [("type", "=", "purchase"), ("company_id", "=", company.id)], limit=1
)
bank_journal = env["account.journal"].search(
    [("type", "=", "bank"), ("company_id", "=", company.id)], limit=1
)
expense_account = env["account.account"].search(
    [("account_type", "=", "expense")], limit=1
)

# --- Vendors --------------------------------------------------------------
vendor_names = [
    "Saudi Industrial Suppliers",
    "Gulf Office Services",
    "National Logistics Co.",
]
vendors = []
for name in vendor_names:
    partner = env["res.partner"].search([("name", "=", name)], limit=1)
    if not partner:
        partner = env["res.partner"].create({
            "name": name,
            "company_type": "company",
            "supplier_rank": 1,
        })
    vendors.append(partner)

# --- Vendor bills across the last 6 months --------------------------------
# (month_offset, vendor_index, untaxed_amount, pay?)
bill_plan = [
    (0, 0, 4000.0, True),
    (1, 1, 2500.0, True),
    (2, 2, 6000.0, False),
    (3, 0, 3500.0, True),
    (4, 1, 2800.0, False),
    (5, 2, 5200.0, False),
]

created_bills = env["account.move"]
for month_offset, vendor_idx, amount, do_pay in bill_plan:
    bill_date = (first_month + relativedelta(months=month_offset)).replace(day=10)
    bill = env["account.move"].create({
        "move_type": "in_invoice",
        "partner_id": vendors[vendor_idx].id,
        "invoice_date": bill_date,
        "date": bill_date,
        "journal_id": purchase_journal.id,
        "invoice_line_ids": [(0, 0, {
            "name": "Operating expense",
            "quantity": 1,
            "price_unit": amount,
            "account_id": expense_account.id,
            "tax_ids": [(6, 0, purchase_tax.ids)],
        })],
    })
    bill.action_post()
    created_bills |= bill
    if do_pay:
        wizard = env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=bill.ids,
        ).create({
            "journal_id": bank_journal.id,
            "payment_date": bill_date,
        })
        wizard.action_create_payments()

# --- Make older unpaid customer invoices overdue --------------------------
open_invoices = env["account.move"].search([
    ("move_type", "=", "out_invoice"),
    ("state", "=", "posted"),
    ("payment_state", "in", ("not_paid", "partial")),
    ("invoice_date", "<", month_start),
])
overdue_set = 0
for move in open_invoices:
    # Due 30 days after the invoice date -> safely in the past for old months.
    move.invoice_date_due = move.invoice_date + relativedelta(days=30)
    overdue_set += 1

env.cr.commit()

print("=== VENDOR + OVERDUE DEMO DATA LOADED ===")
print("Vendor bills created:", len(created_bills))
print("Bills paid:", len(created_bills.filtered(lambda m: m.payment_state in ("paid", "in_payment"))))
print("Invoices marked overdue:", overdue_set)
