"""Load demo data for the RN Saudi finance dashboard.

Run with:
    odoo-bin shell -d rn --no-http < this_file.py

It creates customers, products and posted customer invoices spread across the
last six months (with 15% VAT), and registers payments on some of them so the
dashboard shows revenue, VAT, cash position, receivables and top customers.
"""

from datetime import date

from dateutil.relativedelta import relativedelta

company = env.company
currency = company.currency_id

# --- Building blocks ------------------------------------------------------
sale_tax = env["account.tax"].search(
    [("type_tax_use", "=", "sale"), ("amount", "=", 15)], limit=1
)
sale_journal = env["account.journal"].search(
    [("type", "=", "sale"), ("company_id", "=", company.id)], limit=1
)
bank_journal = env["account.journal"].search(
    [("type", "=", "bank"), ("company_id", "=", company.id)], limit=1
)
if not bank_journal:
    bank_journal = env["account.journal"].create({
        "name": "Bank",
        "type": "bank",
        "code": "BNK1",
        "company_id": company.id,
    })

income_account = env["account.account"].search(
    [("account_type", "=", "income")], limit=1
)

# --- Products -------------------------------------------------------------
product_defs = [
    ("Consulting Service", 2500.0),
    ("Software License", 1800.0),
    ("Annual Maintenance", 1200.0),
    ("Implementation Package", 5000.0),
    ("Training Session", 800.0),
]
products = env["product.product"]
for name, price in product_defs:
    prod = env["product.product"].search([("name", "=", name)], limit=1)
    if not prod:
        prod = env["product.product"].create({
            "name": name,
            "type": "service",
            "list_price": price,
            "taxes_id": [(6, 0, sale_tax.ids)],
        })
    products |= prod

# --- Customers ------------------------------------------------------------
customer_names = [
    "Al Rajhi Trading Est.",
    "Jeddah Industrial Co.",
    "Riyadh Tech Solutions",
    "Dammam Logistics LLC",
    "Makkah Retail Group",
]
customers = env["res.partner"]
for name in customer_names:
    partner = env["res.partner"].search([("name", "=", name)], limit=1)
    if not partner:
        partner = env["res.partner"].create({
            "name": name,
            "company_type": "company",
            "country_id": env.ref("base.sa").id,
        })
    customers |= partner

customers = list(customers)
products = list(products)

# --- Invoices spread across the last 6 months -----------------------------
today = date.today()
first_month = today.replace(day=1) - relativedelta(months=5)

# (month_offset, customer_index, [(product_index, qty), ...], pay?)
plan = [
    (0, 0, [(0, 2), (4, 1)], True),
    (0, 1, [(1, 3)], False),
    (1, 2, [(3, 1), (2, 2)], True),
    (1, 0, [(4, 4)], True),
    (2, 3, [(0, 1), (1, 2)], False),
    (2, 4, [(2, 5)], True),
    (3, 1, [(3, 2)], True),
    (3, 2, [(0, 3), (4, 2)], False),
    (4, 0, [(1, 4)], True),
    (4, 3, [(3, 1), (2, 1)], True),
    (5, 4, [(0, 2), (1, 1), (4, 3)], False),
    (5, 2, [(3, 3)], True),
]

created = env["account.move"]
for month_offset, cust_idx, lines, do_pay in plan:
    inv_date = first_month + relativedelta(months=month_offset)
    inv_date = inv_date.replace(day=min(15, 28))
    line_vals = []
    for prod_idx, qty in lines:
        product = products[prod_idx]
        line_vals.append((0, 0, {
            "product_id": product.id,
            "quantity": qty,
            "price_unit": product.list_price,
            "tax_ids": [(6, 0, sale_tax.ids)],
        }))
    move = env["account.move"].create({
        "move_type": "out_invoice",
        "partner_id": customers[cust_idx].id,
        "invoice_date": inv_date,
        "date": inv_date,
        "journal_id": sale_journal.id,
        "invoice_line_ids": line_vals,
    })
    move.action_post()
    created |= move

    if do_pay:
        wizard = env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=move.ids,
        ).create({
            "journal_id": bank_journal.id,
            "payment_date": inv_date,
        })
        wizard.action_create_payments()

env.cr.commit()

paid = created.filtered(lambda m: m.payment_state in ("paid", "in_payment"))
print("=== DEMO DATA LOADED ===")
print("Invoices created:", len(created))
print("Paid invoices:", len(paid))
print("Total invoiced (incl. tax):", sum(created.mapped("amount_total_signed")), currency.name)
print("Total VAT:", sum(created.mapped("amount_tax_signed")), currency.name)
