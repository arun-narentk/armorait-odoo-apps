#!/usr/bin/env python3
"""Capture live Attachment Preview screenshots and GIFs for Apps Store assets."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_attachment_preview'
MOD_DIR = ROOT / MODULE
PY = Path('/home/lenovo/bin/packages/PyCharm/odoovenvs/py310venv/bin/python')
ODOO_BIN = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/odoo-bin')
RC = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/.openerp_serverrc')

BASE = 'http://127.0.0.1:9196'
DB = 'armora_apps'
USER = 'admin'
PASSWORD = 'admin'
GIF_INTERVAL = 2


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
import base64
import json
Partner = env['res.partner']
Sale = env['sale.order']
Attachment = env['ir.attachment']
group = env.ref('rn_attachment_preview.group_rn_attachment_preview_manager', raise_if_not_found=False)
if group:
    env.user.write({'group_ids': [(4, group.id)]})

partner = Partner.search([('name', '=', 'PREVIEW Demo Customer')], limit=1)
if not partner:
    partner = Partner.create({'name': 'PREVIEW Demo Customer', 'email': 'preview.demo@armorait.com'})
order = Sale.search([('partner_id', '=', partner.id)], limit=1)
if not order:
    order = Sale.create({'partner_id': partner.id})

png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mNk+M9Qz0AEYBxVSF+FABJADveWkH6oAAAAAElFTkSuQmCC')
for name, mimetype, raw in [
    ('product-photo.png', 'image/png', png),
    ('invoice-notes.txt', 'text/plain', b'Invoice notes\\nGST Number: 29ABCDE1234F1Z5\\n'),
]:
    exists = Attachment.search([
        ('res_model', '=', 'sale.order'),
        ('res_id', '=', order.id),
        ('name', '=', name),
    ], limit=1)
    if not exists:
        Attachment.create({
            'name': name,
            'res_model': 'sale.order',
            'res_id': order.id,
            'type': 'binary',
            'mimetype': mimetype,
            'datas': base64.b64encode(raw),
        })

out = {'sale_order_id': order.id}
print(json.dumps(out))
"""
    )


def frames_to_gif(frames: list[Path], out: Path, frame_duration: float = 2.0) -> None:
    if not frames:
        return
    if len(frames) == 1:
        shutil.copy2(frames[0], out.with_suffix('.png'))
        return
    lst = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
    for fr in frames:
        lst.write(f"file '{fr}'\n")
        lst.write(f"duration {frame_duration}\n")
    lst.close()
    subprocess.run(
        [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst.name,
            '-vf', 'fps=4,scale=800:-1:flags=lanczos',
            '-loop', '0',
            str(out),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    Path(lst.name).unlink(missing_ok=True)


def record_scroll_gif(page, out: Path, steps: int = 5) -> None:
    frames: list[Path] = []
    for i in range(steps):
        page.evaluate('(y) => window.scrollTo(0, y)', i * 180)
        page.wait_for_timeout(GIF_INTERVAL * 1000)
        tmp = Path(tempfile.mkstemp(suffix='.png')[1])
        page.screenshot(path=str(tmp), full_page=False)
        frames.append(tmp)
    frames_to_gif(frames, out, frame_duration=GIF_INTERVAL)
    for fr in frames:
        fr.unlink(missing_ok=True)


def login(page) -> None:
    page.goto(f'{BASE}/web/login?db={DB}', wait_until='domcontentloaded', timeout=120000)
    page.wait_for_selector('form.oe_login_form input[name="login"]', timeout=120000)
    page.fill('form.oe_login_form input[name="login"]', USER)
    page.fill('form.oe_login_form input[name="password"]', PASSWORD)
    page.click('form.oe_login_form button[type="submit"]')
    page.wait_for_selector('.o_web_client', timeout=120000)
    page.wait_for_timeout(2500)


def open_sale_order(page, order_id: int, *, mobile: bool = False) -> None:
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    urls = [
        f'{BASE}/odoo/sale.order/{order_id}',
        f'{BASE}/web#id={order_id}&model=sale.order&view_type=form',
    ]
    for url in urls:
        page.goto(url, wait_until='domcontentloaded', timeout=120000)
        page.wait_for_timeout(5000)
        try:
            page.wait_for_selector('.o_form_view, .o_content', timeout=30000)
            break
        except Exception:
            continue
    tab = page.locator('a.nav-link:has-text("Attachments"), button.nav-link:has-text("Attachments")')
    if tab.count():
        tab.first.click()
        page.wait_for_timeout(2500)


def capture_assets(meta: dict) -> None:
    shots_dir = MOD_DIR / 'marketplace' / 'screenshots'
    gifs_dir = MOD_DIR / 'marketplace' / 'gifs'
    desc_dir = MOD_DIR / 'static' / 'description'
    for d in (shots_dir, gifs_dir, desc_dir):
        d.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login(page)

        if meta.get('sale_order_id'):
            open_sale_order(page, meta['sale_order_id'])
            page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'hero.gif', steps=5)
            record_scroll_gif(page, gifs_dir / 'workflow.gif', steps=5)

            preview_btn = page.locator('button:has-text("Preview")')
            if preview_btn.count():
                preview_btn.first.click()
                page.wait_for_timeout(2500)
                page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)
                record_scroll_gif(page, gifs_dir / 'dashboard.gif', steps=4)
                record_scroll_gif(page, gifs_dir / 'settings.gif', steps=4)
                record_scroll_gif(page, gifs_dir / 'reports.gif', steps=4)
                page.keyboard.press('Escape')
                page.wait_for_timeout(1000)

            open_sale_order(page, meta['sale_order_id'], mobile=True)
            page.screenshot(path=str(shots_dir / 'mobile.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'mobile.gif', steps=4)

        browser.close()

    for sub, pattern in [('screenshots', '*.png'), ('gifs', '*.gif')]:
        src = MOD_DIR / 'marketplace' / sub
        for src_file in src.glob(pattern):
            shutil.copy2(src_file, desc_dir / src_file.name)

    subprocess.run(
        [sys.executable, str(ROOT / 'build_marketplace.py'), MODULE, '--no-docs'],
        cwd=str(ROOT),
        check=True,
    )
    print('Captured assets for', MODULE)


def main() -> int:
    meta = seed_demo_data()
    capture_assets(meta)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
