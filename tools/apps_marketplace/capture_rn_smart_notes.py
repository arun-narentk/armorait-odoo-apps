#!/usr/bin/env python3
"""Capture live Smart Notes screenshots and GIFs for Apps Store assets."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_smart_notes'
MOD_DIR = ROOT / MODULE
PY = Path('/home/lenovo/bin/packages/PyCharm/odoovenvs/py310venv/bin/python')
ODOO_BIN = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/odoo-bin')
RC = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/.openerp_serverrc')

BASE = 'http://127.0.0.1:9196'
DB = 'armora_apps'
USER = 'admin'
PASSWORD = 'admin'
GIF_SECONDS = 12
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
import json
Note = env['rn.smart.note']
Template = env['rn.smart.note.template']
Partner = env['res.partner']
Sale = env['sale.order']

partner = Partner.search([('name', '=', 'SMARTNOTE Demo Customer')], limit=1)
if not partner:
    partner = Partner.create({'name': 'SMARTNOTE Demo Customer', 'email': 'demo@armorait.com'})

order = Sale.search([('partner_id', '=', partner.id)], limit=1)
if not order:
    order = Sale.create({'partner_id': partner.id})

notes = [
    {'name': 'VIP Customer', 'note': '<p>Priority account. Handle with extra care.</p>', 'color': 'green', 'priority': 'high', 'icon': 'vip', 'is_pinned': True},
    {'name': 'Payment Delay', 'note': '<p>Customer often delays payment. Follow up before delivery.</p>', 'color': 'orange', 'priority': 'critical', 'icon': 'warning', 'is_pinned': True},
    {'name': 'Call Before Delivery', 'note': '<p>Call warehouse before dispatch.</p>', 'color': 'blue', 'priority': 'high', 'icon': 'call', 'is_pinned': False},
]
for vals in notes:
    exists = Note.search([
        ('res_model', '=', 'sale.order'),
        ('res_id', '=', order.id),
        ('name', '=', vals['name']),
    ], limit=1)
    if not exists:
        vals.update({
            'res_model': 'sale.order',
            'res_id': order.id,
            'company_id': env.company.id,
            'visibility': 'everyone',
        })
        Note.create(vals)

Menu = env['ir.ui.menu']
Action = env['ir.actions.act_window']

def action_id(xmlid):
    rec = env.ref(xmlid, raise_if_not_found=False)
    return rec.id if rec else False

sale_action = env.ref('sale.action_orders', raise_if_not_found=False)
out = {
    'sale_order_id': order.id,
    'sale_action_id': sale_action.id if sale_action else False,
    'notes_action_id': action_id('rn_smart_notes.action_rn_smart_note'),
    'templates_action_id': action_id('rn_smart_notes.action_rn_smart_note_template'),
}
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


def record_scroll_gif(page, out: Path, steps: int = 9) -> None:
    frames: list[Path] = []
    for i in range(steps):
        page.evaluate('(y) => window.scrollTo(0, y)', i * 220)
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


def open_action(page, action_id: int, *, mobile: bool = False) -> None:
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    page.evaluate('(id) => { window.location.hash = "#action=" + id; }', str(action_id))
    page.wait_for_timeout(4500)
    page.wait_for_selector('.o_action_manager, .o_web_client', timeout=60000)


def open_sale_order_with_notes(page, order_id: int) -> None:
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
    page.evaluate(
        """() => {
            document.querySelectorAll('.o-mail-Chatter,.o_Chatter').forEach(e => e.remove());
            const panel = document.querySelector('.o_rn_smart_notes_panel');
            if (panel) panel.scrollIntoView({block: 'center'});
        }"""
    )
    page.wait_for_timeout(2000)


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

        # workflow.png: sale order with notes panel
        if meta.get('sale_order_id'):
            open_sale_order_with_notes(page, meta['sale_order_id'])
            page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'workflow.gif', steps=GIF_SECONDS // GIF_INTERVAL)
            record_scroll_gif(page, gifs_dir / 'hero.gif', steps=max(4, GIF_SECONDS // GIF_INTERVAL))
            page.set_viewport_size({'width': 390, 'height': 844})
            page.goto(f'{BASE}/odoo/sale.order/{meta["sale_order_id"]}', wait_until='domcontentloaded')
            page.wait_for_timeout(3500)
            page.screenshot(path=str(shots_dir / 'mobile.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'mobile.gif', steps=6)

        page.set_viewport_size({'width': 1440, 'height': 900})

        # dashboard.png + dashboard.gif: notes kanban
        if meta.get('notes_action_id'):
            open_action(page, meta['notes_action_id'])
            page.wait_for_timeout(2500)
            page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'dashboard.gif', steps=GIF_SECONDS // GIF_INTERVAL)
            record_scroll_gif(page, gifs_dir / 'reports.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        # designer.png + settings.gif: note templates
        if meta.get('templates_action_id'):
            open_action(page, meta['templates_action_id'])
            page.wait_for_timeout(2500)
            page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'settings.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        browser.close()

    # Copy into static/description for product_builder
    for src_dir, names in (
        (shots_dir, ('workflow.png', 'dashboard.png', 'designer.png', 'mobile.png')),
        (gifs_dir, ('hero.gif', 'workflow.gif', 'dashboard.gif', 'settings.gif', 'reports.gif', 'mobile.gif')),
    ):
        for name in names:
            src = src_dir / name
            if src.exists():
                shutil.copy2(src, desc_dir / name)


def main() -> int:
    meta = seed_demo_data()
    print('demo meta', meta)
    capture_assets(meta)
    subprocess.run(
        ['python3', str(ROOT / 'build_marketplace.py'), MODULE, '--no-docs'],
        cwd=str(ROOT),
        check=True,
    )
    print('Captured live assets for', MODULE)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
