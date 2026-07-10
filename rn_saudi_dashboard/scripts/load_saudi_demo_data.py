"""Replace all demo accounting data with a realistic Saudi Arabia dataset.

Run with:
    odoo-bin shell -d <db> --no-http < load_saudi_demo_data.py

This script:
  1. Removes existing customer invoices, vendor bills and payments for the
     current company (unreconciles, resets to draft, deletes).
  2. Removes the previously created demo customers, vendors and products.
  3. Creates a fresh, demo-ready Saudi dataset:
       - 5 customers (with Saudi VAT numbers, so e-invoices are ZATCA ready)
       - 5 vendors
       - 5 service products (priced in SAR)
       - customer invoices and vendor bills across the last 6 months with 15%
         VAT, a realistic paid / unpaid / overdue mix.

All amounts are in SAR. Example invoice: ERP Consulting Service 10,000 + 15%
VAT = 11,500 SAR. Example bill: Office Equipment 5,000 + 15% VAT = 5,750 SAR.
"""

from datetime import date

from dateutil.relativedelta import relativedelta

company = env.company
currency = company.currency_id
sa_country = env.ref("base.sa")

# Make sure the seller (company) is VAT registered for compliant invoices.
if not company.vat:
    company.vat = "300000000000003"
if not company.country_id:
    company.country_id = sa_country.id


# ==========================================================================
# 1 & 2. Clean previous demo data
# ==========================================================================
def safe_remove(records):
    """Delete records one by one, isolating each in a savepoint so a single
    failure cannot poison the whole transaction. Archive as a fallback."""
    removed = 0
    for rec in records:
        try:
            with env.cr.savepoint():
                rec.unlink()
            removed += 1
        except Exception:
            if "active" in rec._fields:
                rec.active = False
    return removed


print("=== CLEANING OLD DEMO DATA ===")

invoices_bills = env["account.move"].search([
    ("company_id", "=", company.id),
    ("move_type", "in", ("out_invoice", "out_refund", "in_invoice", "in_refund")),
])
payments = env["account.payment"].search([("company_id", "=", company.id)])

# Unreconcile everything, reset to draft, then delete payments before moves.
(payments.move_id | invoices_bills).line_ids.remove_move_reconcile()
if payments:
    payments.action_draft()
    print("Deleting payments:", len(payments))
    payments.unlink()                       # removes the linked payment moves too
posted = invoices_bills.filtered(lambda m: m.state == "posted")
if posted:
    posted.button_draft()
print("Deleting invoices/bills:", len(invoices_bills))
invoices_bills.unlink()

# Remove old demo partners and products created by earlier scripts.
old_partner_names = [
    "Al Rajhi Trading Est.", "Jeddah Industrial Co.", "Riyadh Tech Solutions",
    "Dammam Logistics LLC", "Makkah Retail Group",
    "Saudi Industrial Suppliers", "Gulf Office Services", "National Logistics Co.",
]
old_product_names = [
    "Consulting Service", "Software License", "Annual Maintenance",
    "Implementation Package", "Training Session",
]
old_partners = env["res.partner"].search([("name", "in", old_partner_names)])
old_products = env["product.product"].search([("name", "in", old_product_names)])
print("Removed old partners:", safe_remove(old_partners), "/", len(old_partners))
print("Removed old products:", safe_remove(old_products), "/", len(old_products))

env.cr.commit()


# ==========================================================================
# Building blocks
# ==========================================================================
sale_tax = env["account.tax"].search(
    [("type_tax_use", "=", "sale"), ("amount", "=", 15), ("company_id", "=", company.id)],
    limit=1,
)
purchase_tax = env["account.tax"].search(
    [("type_tax_use", "=", "purchase"), ("amount", "=", 15), ("company_id", "=", company.id)],
    limit=1,
)
sale_journal = env["account.journal"].search(
    [("type", "=", "sale"), ("company_id", "=", company.id)], limit=1
)
purchase_journal = env["account.journal"].search(
    [("type", "=", "purchase"), ("company_id", "=", company.id)], limit=1
)
bank_journal = env["account.journal"].search(
    [("type", "=", "bank"), ("company_id", "=", company.id)], limit=1
)
if not bank_journal:
    bank_journal = env["account.journal"].create({
        "name": "Bank", "type": "bank", "code": "BNK1", "company_id": company.id,
    })
expense_account = env["account.account"].search(
    [("account_type", "=", "expense"), ("company_ids", "in", company.id)], limit=1
) or env["account.account"].search([("account_type", "=", "expense")], limit=1)


# ==========================================================================
# 3. New Saudi master data
# ==========================================================================
# (name, city, vat number)
customer_defs = [
    ("Al Rajhi Trading LLC", "Riyadh", "310111111100003"),
    ("Riyadh Industrial Group", "Riyadh", "310222222200003"),
    ("Jeddah Electronics Co", "Jeddah", "310333333300003"),
    ("Al Noor Logistics", "Dammam", "310444444400003"),
    ("Saudi Business Solutions", "Riyadh", "310555555500003"),
]
vendor_defs = [
    ("Gulf Office Supplies", "Riyadh", "300611111100003"),
    ("Saudi Industrial Equipment", "Dammam", "300622222200003"),
    ("Riyadh Packaging Materials", "Riyadh", "300633333300003"),
    ("Arabian IT Solutions", "Jeddah", "300644444400003"),
    ("Al Faisal Trading", "Riyadh", "300655555500003"),
]
# (name, list price in SAR)
product_defs = [
    ("ERP Consulting Service", 10000.0),
    ("Accounting Implementation Service", 15000.0),
    ("Inventory Management Service", 8000.0),
    ("Annual ERP Support Contract", 20000.0),
    ("Business Process Consulting", 12000.0),
]


def upsert_partner(name, city, vat, is_vendor=False):
    partner = env["res.partner"].search([("name", "=", name)], limit=1)
    vals = {
        "name": name,
        "company_type": "company",
        "city": city,
        "country_id": sa_country.id,
        "vat": vat,
    }
    if is_vendor:
        vals["supplier_rank"] = 1
    else:
        vals["customer_rank"] = 1
    if partner:
        partner.write(vals)
    else:
        partner = env["res.partner"].create(vals)
    return partner


customers = [upsert_partner(n, c, v) for (n, c, v) in customer_defs]
vendors = [upsert_partner(n, c, v, is_vendor=True) for (n, c, v) in vendor_defs]

products = []
for name, price in product_defs:
    prod = env["product.product"].search([("name", "=", name)], limit=1)
    vals = {
        "name": name,
        "type": "service",
        "list_price": price,
        "taxes_id": [(6, 0, sale_tax.ids)],
        "supplier_taxes_id": [(6, 0, purchase_tax.ids)],
    }
    if prod:
        prod.write(vals)
    else:
        prod = env["product.product"].create(vals)
    products.append(prod)


# ==========================================================================
# 4. Sample transactions (last 6 months)
# ==========================================================================
today = date.today()
first_month = today.replace(day=1) - relativedelta(months=5)

# Customer invoices: (month_offset, customer_idx, [(product_idx, qty), ...], pay?)
invoice_plan = [
    (0, 0, [(0, 1)], True),            # Al Rajhi - ERP Consulting 10,000
    (0, 1, [(2, 1)], True),            # Riyadh Industrial - Inventory 8,000
    (1, 2, [(1, 1)], False),           # Jeddah Electronics - Accounting Impl 15,000
    (1, 3, [(4, 1)], True),            # Al Noor - Business Process 12,000
    (2, 4, [(0, 1), (2, 1)], True),    # Saudi Business - ERP + Inventory 18,000
    (2, 0, [(3, 1)], False),           # Al Rajhi - Annual Support 20,000
    (3, 1, [(4, 2)], True),            # Riyadh Industrial - Business Process x2 24,000
    (3, 2, [(0, 1)], False),           # Jeddah - ERP Consulting 10,000
    (4, 3, [(1, 1)], True),            # Al Noor - Accounting Impl 15,000
    (4, 4, [(2, 2)], False),           # Saudi Business - Inventory x2 16,000
    (5, 0, [(0, 1), (4, 1)], False),   # Al Rajhi - ERP + Business Process 22,000 (this month)
    (5, 1, [(3, 1)], True),            # Riyadh Industrial - Annual Support 20,000 (this month)
    (5, 2, [(1, 1)], False),           # Jeddah - Accounting Impl 15,000 (this month)
]

created_invoices = env["account.move"]
for month_offset, cust_idx, lines, do_pay in invoice_plan:
    inv_date = (first_month + relativedelta(months=month_offset)).replace(day=15)
    line_vals = []
    for prod_idx, qty in lines:
        product = products[prod_idx]
        line_vals.append((0, 0, {
            "product_id": product.id,
            "name": product.name,
            "quantity": qty,
            "price_unit": product.list_price,
            "tax_ids": [(6, 0, sale_tax.ids)],
        }))
    move = env["account.move"].create({
        "move_type": "out_invoice",
        "partner_id": customers[cust_idx].id,
        "invoice_date": inv_date,
        "date": inv_date,
        "invoice_date_due": inv_date + relativedelta(days=30),
        "journal_id": sale_journal.id,
        "invoice_line_ids": line_vals,
    })
    move.action_post()
    created_invoices |= move
    if do_pay:
        env["account.payment.register"].with_context(
            active_model="account.move", active_ids=move.ids,
        ).create({
            "journal_id": bank_journal.id,
            "payment_date": inv_date,
        }).action_create_payments()

# Vendor bills: (month_offset, vendor_idx, description, untaxed amount, pay?)
bill_plan = [
    (0, 0, "Office Equipment Purchase", 5000.0, True),     # 5,000 + 15% = 5,750
    (1, 1, "Industrial Equipment", 12000.0, True),
    (2, 2, "Packaging Materials", 4500.0, False),
    (3, 3, "IT Services & Software Licenses", 8000.0, True),
    (4, 4, "Trading Goods Supply", 6500.0, False),
    (5, 0, "Office Supplies Restock", 3000.0, False),      # this month
    (5, 1, "Machinery Maintenance", 7000.0, True),         # this month
]

created_bills = env["account.move"]
for month_offset, vendor_idx, desc, amount, do_pay in bill_plan:
    bill_date = (first_month + relativedelta(months=month_offset)).replace(day=10)
    bill = env["account.move"].create({
        "move_type": "in_invoice",
        "partner_id": vendors[vendor_idx].id,
        "invoice_date": bill_date,
        "date": bill_date,
        "invoice_date_due": bill_date + relativedelta(days=30),
        "journal_id": purchase_journal.id,
        "invoice_line_ids": [(0, 0, {
            "name": desc,
            "quantity": 1,
            "price_unit": amount,
            "account_id": expense_account.id,
            "tax_ids": [(6, 0, purchase_tax.ids)],
        })],
    })
    bill.action_post()
    created_bills |= bill
    if do_pay:
        env["account.payment.register"].with_context(
            active_model="account.move", active_ids=bill.ids,
        ).create({
            "journal_id": bank_journal.id,
            "payment_date": bill_date,
        }).action_create_payments()

env.cr.commit()


# ==========================================================================
# Summary
# ==========================================================================
paid_inv = created_invoices.filtered(lambda m: m.payment_state in ("paid", "in_payment"))
overdue_inv = created_invoices.filtered(
    lambda m: m.payment_state in ("not_paid", "partial")
    and m.invoice_date_due and m.invoice_date_due < today
)
print("=== SAUDI DEMO DATA LOADED ===")
print("Customers:", len(customers), "| Vendors:", len(vendors), "| Products:", len(products))
print("Customer invoices:", len(created_invoices), "| Paid:", len(paid_inv), "| Overdue:", len(overdue_inv))
print("Vendor bills:", len(created_bills))
print("Total invoiced (incl. VAT):", sum(created_invoices.mapped("amount_total_signed")), currency.name)
print("Output VAT:", sum(created_invoices.mapped("amount_tax_signed")), currency.name)
print("Total billed (incl. VAT):", -sum(created_bills.mapped("amount_total_signed")), currency.name)
