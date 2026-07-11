#!/usr/bin/env python3
"""Capture live Field Difference Viewer screenshots and GIFs for Apps Store assets."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_field_diff'
MOD_DIR = ROOT / MODULE
PY = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/venv310/bin/python')
ODOO_BIN = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/odoo-bin')
RC = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/.openerp_serverrc')

BASE = 'http://127.0.0.1:9196'
DB = 'armora_apps'
USER = 'admin'
PASSWORD = 'admin'
GIF_INTERVAL = 2

SCREENSHOTS = (
    'overview.png', 'list.png', 'form.png', 'dashboard.png', 'wizard.png',
    'settings.png', 'report.png', 'search.png', 'kanban.png', 'mobile.png',
    'workflow.png', 'designer.png',
)
GIFS = ('hero.gif', 'workflow.gif', 'dashboard.gif', 'settings.gif', 'reports.gif', 'mobile.gif')


def odoo_shell(code: str) -> dict:
    proc = subprocess.run(
        [str(PY), str(ODOO_BIN), 'shell', '-d', DB, '-c', str(RC), '--no-http'],
        input=code, text=True, capture_output=True, cwd=str(ODOO_BIN.parent),
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise RuntimeError('Odoo shell failed')
    for line in reversed((proc.stdout or '').splitlines()):
        line = line.strip()
        if line.startswith('{'):
            return json.loads(line)
    return {}


def seed_demo_data() -> dict:
    return odoo_shell(
        """
import json
Partner = env['res.partner']
SaleOrder = env['sale.order']
Product = env['product.product'].search([('sale_ok', '=', True)], limit=1)
pa = env.ref('rn_field_diff.demo_field_diff_partner_a')
pb = env.ref('rn_field_diff.demo_field_diff_partner_b')
order = SaleOrder.search([('partner_id', '=', pb.id)], limit=1)
if not order:
    order = SaleOrder.create({
        'partner_id': pa.id,
        'order_line': [(0, 0, {'product_id': Product.id, 'product_uom_qty': 1})],
    })
    env.flush_all()
    order.write({'partner_id': pb.id})
    env.flush_all()
lead = env['crm.lead'].create({
    'name': 'FIELDDIFF Capture Lead',
    'type': 'opportunity',
    'expected_revenue': 1000,
})
lead.write({'expected_revenue': 1800})
env.flush_all()
diff = env['rn.field.diff'].search([
    ('model', '=', 'sale.order'), ('res_id', '=', order.id),
], limit=1)
def action_id(xmlid):
    rec = env.ref(xmlid, raise_if_not_found=False)
    return rec.id if rec else False
out = {
    'order_id': order.id,
    'lead_id': lead.id,
    'diff_id': diff.id if diff else False,
    'diff_action_id': action_id('rn_field_diff.action_rn_field_diff'),
    'sale_action_id': action_id('sale.action_orders'),
    'crm_action_id': action_id('crm.crm_lead_opportunities'),
}
print(json.dumps(out))
"""
    )


def frames_to_gif(frames: list[Path], out: Path) -> None:
    if len(frames) < 2:
        return
    lst = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
    for fr in frames:
        lst.write(f"file '{fr}'\nduration {GIF_INTERVAL}\n")
    lst.close()
    subprocess.run(
        ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst.name,
         '-vf', 'fps=6,scale=1100:-1:flags=lanczos', str(out)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    Path(lst.name).unlink(missing_ok=True)


def login(page) -> None:
    page.goto(f'{BASE}/web/login?db={DB}', wait_until='domcontentloaded', timeout=120000)
    page.fill('form.oe_login_form input[name="login"]', USER)
    page.fill('form.oe_login_form input[name="password"]', PASSWORD)
    page.click('form.oe_login_form button[type="submit"]')
    page.wait_for_selector('.o_web_client', timeout=120000)
    page.wait_for_timeout(2500)


def open_action(page, action_id: int, *, mobile: bool = False) -> None:
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    page.evaluate('(id) => { window.location.hash = "#action=" + id; }', str(action_id))
    page.wait_for_timeout(4500)


def open_record_form(page, model: str, record_id: int) -> None:
    page.goto(f'{BASE}/odoo/{model}/{record_id}', wait_until='domcontentloaded', timeout=120000)
    page.wait_for_timeout(4500)


def capture_assets(meta: dict) -> None:
    shots_dir = MOD_DIR / 'marketplace' / 'screenshots'
    gifs_dir = MOD_DIR / 'marketplace' / 'gifs'
    desc_dir = MOD_DIR / 'static' / 'description'
    for d in (shots_dir, gifs_dir, desc_dir):
        d.mkdir(parents=True, exist_ok=True)

    diff_aid = meta.get('diff_action_id')
    sale_aid = meta.get('sale_action_id')
    crm_aid = meta.get('crm_action_id')
    order_id = meta.get('order_id')
    diff_id = meta.get('diff_id')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login(page)
        if diff_aid:
            open_action(page, diff_aid)
            page.screenshot(path=str(shots_dir / 'list.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'overview.png'), full_page=False)
            if diff_id:
                open_record_form(page, 'rn.field.diff', diff_id)
                page.screenshot(path=str(shots_dir / 'form.png'), full_page=False)
                page.screenshot(path=str(shots_dir / 'wizard.png'), full_page=False)
        if sale_aid and order_id:
            open_record_form(page, 'sale.order', order_id)
            page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)
        if crm_aid:
            open_action(page, crm_aid)
            page.screenshot(path=str(shots_dir / 'search.png'), full_page=False)
        if diff_aid:
            open_action(page, diff_aid)
            page.screenshot(path=str(shots_dir / 'settings.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'kanban.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'report.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)
        if sale_aid and order_id:
            open_record_form(page, 'sale.order', order_id)
            page.set_viewport_size({'width': 390, 'height': 844})
            page.screenshot(path=str(shots_dir / 'mobile.png'), full_page=False)
        browser.close()

    for name in SCREENSHOTS:
        src = shots_dir / name
        if src.exists():
            shutil.copy2(src, desc_dir / name)
    for name in GIFS:
        src = gifs_dir / name
        if src.exists():
            shutil.copy2(src, desc_dir / name)


def main() -> int:
    meta = seed_demo_data()
    print('demo meta', meta)
    if not meta.get('diff_action_id'):
        raise SystemExit('Install rn_field_diff and demo data first.')
    capture_assets(meta)
    subprocess.run(
        [sys.executable, str(ROOT / 'build_marketplace.py'), MODULE, '--no-docs'],
        cwd=str(ROOT), check=True,
    )
    print('Captured live assets for', MODULE)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
