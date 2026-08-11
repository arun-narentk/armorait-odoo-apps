#!/usr/bin/env python3
"""Capture live Universal QR screenshots and GIFs for Apps Store assets."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_universal_qr'
MOD_DIR = ROOT / MODULE
PY = Path('/home/lenovo/bin/packages/PyCharm/odoovenvs/py310venv/bin/python')
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
GIFS = (
    'hero.gif', 'workflow.gif', 'dashboard.gif',
    'settings.gif', 'reports.gif', 'mobile.gif',
)


def odoo_shell(code: str) -> dict:
    proc = subprocess.run(
        [str(PY), str(ODOO_BIN), 'shell', '-d', DB, '-c', str(RC), '--no-http'],
        input=code,
        text=True,
        capture_output=True,
        cwd=str(ODOO_BIN.parent),
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
Sale = env['sale.order']
Product = env['product.template']

partner = Partner.search([('name', '=', 'QRCAP Demo Customer')], limit=1)
if not partner:
    partner = Partner.create({'name': 'QRCAP Demo Customer', 'email': 'qrcap@armorait.com'})
partner.action_generate_qr()

order = Sale.search([('partner_id', '=', partner.id)], limit=1)
if not order:
    order = Sale.create({'partner_id': partner.id})
order.action_generate_qr()

product = Product.search([('name', '=', 'QRCAP Demo Product')], limit=1)
if not product:
    product = Product.create({'name': 'QRCAP Demo Product', 'list_price': 49.0})
product.product_variant_id.action_generate_qr()

qr_record = env['rn.qr.record'].search([
    ('res_model', '=', 'sale.order'),
    ('res_id', '=', order.id),
], limit=1)

scan_service = env['rn.qr.scan.service']
if qr_record:
    scan_service.log_scan(qr_record, source='web', user_agent='Capture Desktop', ip_address='127.0.0.1')
    scan_service.log_scan(qr_record, source='mobile', user_agent='Capture Mobile', ip_address='10.0.0.8')

def action_id(xmlid):
    rec = env.ref(xmlid, raise_if_not_found=False)
    return rec.id if rec else False

out = {
    'partner_id': partner.id,
    'sale_order_id': order.id,
    'product_id': product.product_variant_id.id,
    'qr_record_id': qr_record.id if qr_record else False,
    'records_action_id': action_id('rn_universal_qr.action_rn_qr_record'),
    'scan_logs_action_id': action_id('rn_universal_qr.action_rn_qr_scan_log'),
    'templates_action_id': action_id('rn_universal_qr.action_rn_qr_template'),
    'model_config_action_id': action_id('rn_universal_qr.action_rn_qr_model_config'),
    'bulk_wizard_action_id': action_id('rn_universal_qr.action_rn_qr_bulk_generate_wizard'),
}
print(json.dumps(out))
"""
    )


def frames_to_gif(frames: list[Path], out: Path, frame_duration: float = 2.0) -> None:
    if not frames:
        return
    lst = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
    for frame in frames:
        lst.write(f"file '{frame}'\n")
        lst.write(f"duration {frame_duration}\n")
    lst.close()
    subprocess.run(
        [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst.name,
            '-vf', 'fps=5,scale=900:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
            '-loop', '0', str(out),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    Path(lst.name).unlink(missing_ok=True)


def record_scroll_gif(page, out: Path, steps: int = 6) -> None:
    frames: list[Path] = []
    for i in range(steps):
        page.evaluate(
            """(y) => {
                document.querySelectorAll('.o_content, .o_action_manager, main').forEach(el => {
                    if (el) el.scrollTop = y;
                });
                window.scrollTo(0, y);
            }""",
            i * 220,
        )
        page.wait_for_timeout(GIF_INTERVAL * 1000)
        tmp = Path(tempfile.mkstemp(suffix='.png')[1])
        page.screenshot(path=str(tmp), full_page=False)
        frames.append(tmp)
    frames_to_gif(frames, out, frame_duration=GIF_INTERVAL)
    for frame in frames:
        frame.unlink(missing_ok=True)


def login(page) -> None:
    page.goto(f'{BASE}/web/login?db={DB}', wait_until='domcontentloaded', timeout=120000)
    page.fill('form.oe_login_form input[name="login"]', USER)
    page.fill('form.oe_login_form input[name="password"]', PASSWORD)
    page.click('form.oe_login_form button[type="submit"]')
    page.wait_for_selector('.o_web_client', timeout=120000)
    page.wait_for_timeout(2500)


def open_action(page, action_id: int) -> None:
    page.set_viewport_size({'width': 1440, 'height': 900})
    page.evaluate('(id) => { window.location.hash = "#action=" + id; }', str(action_id))
    page.wait_for_timeout(4500)
    page.evaluate(
        "document.querySelectorAll('.o-mail-Chatter,.o_Chatter').forEach(e => e.remove())"
    )


def open_record_form(page, model: str, record_id: int) -> None:
    page.set_viewport_size({'width': 1440, 'height': 900})
    page.goto(f'{BASE}/odoo/{model}/{record_id}', wait_until='domcontentloaded', timeout=120000)
    page.wait_for_timeout(4500)
    page.evaluate(
        "document.querySelectorAll('.o-mail-Chatter,.o_Chatter').forEach(e => e.remove())"
    )


def open_settings(page) -> None:
    page.set_viewport_size({'width': 1440, 'height': 900})
    page.goto(f'{BASE}/odoo/settings', wait_until='domcontentloaded', timeout=120000)
    page.wait_for_timeout(3500)
    for selector in (
        'button:has-text("Universal QR")',
        'a:has-text("Universal QR")',
        '[data-menu-xmlid*="rn_universal_qr"]',
    ):
        try:
            page.click(selector, timeout=3000)
            page.wait_for_timeout(2000)
            break
        except Exception:
            continue


def try_click_generate_qr(page) -> None:
    for selector in ('button:has-text("Generate QR")', 'button[name="action_generate_qr"]'):
        try:
            page.click(selector, timeout=4000)
            page.wait_for_timeout(2500)
            return
        except Exception:
            continue


def capture_assets(meta: dict) -> None:
    shots_dir = MOD_DIR / 'marketplace' / 'screenshots'
    gifs_dir = MOD_DIR / 'marketplace' / 'gifs'
    desc_dir = MOD_DIR / 'static' / 'description'
    for folder in (shots_dir, gifs_dir, desc_dir):
        folder.mkdir(parents=True, exist_ok=True)

    records_aid = meta.get('records_action_id')
    scans_aid = meta.get('scan_logs_action_id')
    templates_aid = meta.get('templates_action_id')
    config_aid = meta.get('model_config_action_id')
    bulk_aid = meta.get('bulk_wizard_action_id')
    sale_id = meta.get('sale_order_id')
    qr_record_id = meta.get('qr_record_id')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login(page)

        if records_aid:
            open_action(page, records_aid)
            page.screenshot(path=str(shots_dir / 'list.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'overview.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'search.png'), full_page=False)

        if qr_record_id:
            open_record_form(page, 'rn.qr.record', qr_record_id)
            page.screenshot(path=str(shots_dir / 'form.png'), full_page=False)

        if sale_id:
            open_record_form(page, 'sale.order', sale_id)
            page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)
            try_click_generate_qr(page)
            page.screenshot(path=str(shots_dir / 'report.png'), full_page=False)

        if scans_aid:
            open_action(page, scans_aid)
            page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'dashboard.gif')

        if templates_aid:
            open_action(page, templates_aid)
            page.screenshot(path=str(shots_dir / 'kanban.png'), full_page=False)

        if config_aid:
            open_action(page, config_aid)
            page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)

        open_settings(page)
        page.screenshot(path=str(shots_dir / 'settings.png'), full_page=False)
        record_scroll_gif(page, gifs_dir / 'settings.gif')

        if bulk_aid:
            open_action(page, bulk_aid)
            page.wait_for_timeout(2500)
            page.screenshot(path=str(shots_dir / 'wizard.png'), full_page=False)

        if sale_id:
            open_record_form(page, 'sale.order', sale_id)
            frames: list[Path] = []
            for _ in range(4):
                try_click_generate_qr(page)
                tmp = Path(tempfile.mkstemp(suffix='.png')[1])
                page.screenshot(path=str(tmp), full_page=False)
                frames.append(tmp)
                page.wait_for_timeout(GIF_INTERVAL * 1000)
            frames_to_gif(frames, gifs_dir / 'hero.gif', frame_duration=GIF_INTERVAL)
            for frame in frames:
                frame.unlink(missing_ok=True)

        workflow_actions = [aid for aid in (records_aid, scans_aid, templates_aid, config_aid) if aid]
        if len(workflow_actions) >= 2:
            frames = []
            for aid in workflow_actions[:4]:
                open_action(page, aid)
                page.wait_for_timeout(GIF_INTERVAL * 1000)
                tmp = Path(tempfile.mkstemp(suffix='.png')[1])
                page.screenshot(path=str(tmp), full_page=False)
                frames.append(tmp)
            frames_to_gif(frames, gifs_dir / 'workflow.gif', frame_duration=GIF_INTERVAL)
            for frame in frames:
                frame.unlink(missing_ok=True)

        if qr_record_id:
            open_record_form(page, 'rn.qr.record', qr_record_id)
            record_scroll_gif(page, gifs_dir / 'reports.gif', steps=5)

        if sale_id:
            page.set_viewport_size({'width': 390, 'height': 844})
            page.goto(f'{BASE}/odoo/sale.order/{sale_id}', wait_until='domcontentloaded', timeout=120000)
            page.wait_for_timeout(3000)
            page.screenshot(path=str(shots_dir / 'mobile.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'mobile.gif', steps=5)

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
    if not meta.get('records_action_id'):
        raise SystemExit('Universal QR actions not found. Install rn_universal_qr first.')
    capture_assets(meta)
    subprocess.run(
        [sys.executable, str(ROOT / 'build_marketplace.py'), MODULE, '--no-docs'],
        cwd=str(ROOT),
        check=True,
    )
    print('Captured live assets for', MODULE)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
