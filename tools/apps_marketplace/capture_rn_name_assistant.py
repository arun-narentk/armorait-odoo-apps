#!/usr/bin/env python3
"""Capture live Name Assistant screenshots and GIFs for Apps Store assets."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_name_assistant'
MOD_DIR = ROOT / MODULE
PY = Path('/home/lenovo/bin/packages/PyCharm/odoovenvs/py310venv/bin/python')
ODOO_BIN = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/odoo-bin')
RC = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/.openerp_serverrc')

BASE = 'http://127.0.0.1:9196'
DB = 'armora_apps'
USER = 'admin'
PASSWORD = 'admin'
GIF_SECONDS = 18
GIF_INTERVAL = 2

SCREENSHOTS = (
    'workflow.png',
    'dashboard.png',
    'designer.png',
    'wizard.png',
    'settings.png',
    'report.png',
    'mobile.png',
)
GIFS = (
    'hero.gif',
    'workflow.gif',
    'dashboard.gif',
    'settings.gif',
    'reports.gif',
    'mobile.gif',
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
        print(proc.stdout, file=sys.stderr)
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

manager = env.ref('rn_name_assistant.group_rn_name_assistant_manager', raise_if_not_found=False)
user = env.ref('base.user_admin')
if manager:
    user.write({'group_ids': [(4, manager.id)]})

Category = env['product.category']
category = Category.search([('name', '=', 'Business Laptop')], limit=1)
if not category:
    category = Category.create({'name': 'Business Laptop'})

Product = env['product.template']
product = Product.search([('default_code', '=', 'NAMECAP-LAPTOP')], limit=1)
if not product:
    product = Product.create({
        'name': 'Laptop',
        'default_code': 'NAMECAP-LAPTOP',
        'rn_brand': 'Dell',
        'rn_series': 'Latitude',
        'rn_model_number': '7440',
        'categ_id': category.id,
    })
else:
    product.write({
        'name': 'Laptop',
        'rn_brand': 'Dell',
        'rn_series': 'Latitude',
        'rn_model_number': '7440',
        'categ_id': category.id,
    })

product2 = Product.search([('default_code', '=', 'NAMECAP-TABLE')], limit=1)
if not product2:
    table_cat = Category.search([('name', '=', 'Dining Table')], limit=1)
    if not table_cat:
        table_cat = Category.create({'name': 'Dining Table'})
    product2 = Product.create({
        'name': 'Table',
        'default_code': 'NAMECAP-TABLE',
        'rn_brand': 'IKEA',
        'rn_material': 'Oak',
        'rn_size': '120 cm',
        'categ_id': table_cat.id,
    })

template = env['rn.name.template'].search([('name', '=', 'Product Default')], limit=1)

def action_id(xmlid):
    rec = env.ref(xmlid, raise_if_not_found=False)
    return rec.id if rec else False

out = {
    'product_id': product.id,
    'product2_id': product2.id,
    'template_id': template.id if template else False,
    'templates_action_id': action_id('rn_name_assistant.action_rn_name_template'),
    'abbrev_action_id': action_id('rn_name_assistant.action_rn_name_abbreviation'),
    'products_action_id': action_id('product.product_template_action'),
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
            '-vf', 'fps=6,scale=1100:-1:flags=lanczos', str(out),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    Path(lst.name).unlink(missing_ok=True)


def record_scroll_gif(page, out: Path, steps: int = 9) -> None:
    frames: list[Path] = []
    for i in range(steps):
        page.evaluate(
            """(y) => {
                const targets = document.querySelectorAll('.o_content, .o_action_manager, main');
                targets.forEach(el => { if (el) el.scrollTop = y; });
                window.scrollTo(0, y);
            }""",
            i * 220,
        )
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
    hide_chatter(page)


def hide_chatter(page) -> None:
    page.evaluate(
        "document.querySelectorAll('.o-mail-Chatter,.o_Chatter').forEach(e => e.remove())"
    )


def open_record_form(page, model: str, record_id: int) -> None:
    page.set_viewport_size({'width': 1440, 'height': 900})
    for url in (
        f'{BASE}/odoo/{model}/{record_id}',
        f'{BASE}/web#id={record_id}&model={model}&view_type=form',
    ):
        page.goto(url, wait_until='domcontentloaded', timeout=120000)
        page.wait_for_timeout(4500)
        try:
            page.wait_for_selector('.o_form_view, .o_content', timeout=30000)
            hide_chatter(page)
            return
        except Exception:
            continue


def try_click_suggest_name(page) -> bool:
    selectors = (
        'button[name="action_suggest_name"]',
        '.oe_stat_button:has-text("Suggest Name")',
        'button:has-text("Suggest Name")',
    )
    for sel in selectors:
        try:
            page.click(sel, timeout=5000)
            page.wait_for_timeout(2500)
            return True
        except Exception:
            continue
    return False


def wait_for_wizard(page) -> bool:
    for sel in ('.o_dialog', '.modal-dialog', '[role="dialog"]', '.o_form_view'):
        try:
            page.wait_for_selector(sel, timeout=8000)
            return True
        except Exception:
            continue
    return False


def try_use_selected(page) -> bool:
    for sel in (
        'button[name="action_use_selected"]',
        'button:has-text("Use Selected")',
    ):
        try:
            page.click(sel, timeout=5000)
            page.wait_for_timeout(2000)
            return True
        except Exception:
            continue
    return False


def record_hero_gif(page, product_id: int, out: Path) -> None:
    frames: list[Path] = []
    steps = [
        ('form', lambda: open_record_form(page, 'product.template', product_id)),
        ('click', lambda: try_click_suggest_name(page)),
        ('wizard', lambda: wait_for_wizard(page)),
        ('apply', lambda: try_use_selected(page)),
        ('done', lambda: page.wait_for_timeout(1500)),
    ]
    for _, action in steps:
        action()
        page.wait_for_timeout(GIF_INTERVAL * 1000)
        tmp = Path(tempfile.mkstemp(suffix='.png')[1])
        page.screenshot(path=str(tmp), full_page=False)
        frames.append(tmp)
    frames_to_gif(frames, out, frame_duration=GIF_INTERVAL)
    for fr in frames:
        fr.unlink(missing_ok=True)


def capture_assets(meta: dict) -> None:
    shots_dir = MOD_DIR / 'marketplace' / 'screenshots'
    gifs_dir = MOD_DIR / 'marketplace' / 'gifs'
    desc_dir = MOD_DIR / 'static' / 'description'
    for folder in (shots_dir, gifs_dir, desc_dir):
        folder.mkdir(parents=True, exist_ok=True)

    templates_aid = meta.get('templates_action_id')
    abbrev_aid = meta.get('abbrev_action_id')
    products_aid = meta.get('products_action_id')
    product_id = meta.get('product_id')
    template_id = meta.get('template_id')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login(page)

        if templates_aid:
            open_action(page, templates_aid)
            page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'dashboard.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        if template_id:
            open_record_form(page, 'rn.name.template', template_id)
            page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)

        if product_id:
            open_record_form(page, 'product.template', product_id)
            page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)
            if try_click_suggest_name(page) and wait_for_wizard(page):
                page.wait_for_timeout(1500)
                page.screenshot(path=str(shots_dir / 'wizard.png'), full_page=False)
            record_hero_gif(page, product_id, gifs_dir / 'hero.gif')

        if abbrev_aid:
            open_action(page, abbrev_aid)
            page.screenshot(path=str(shots_dir / 'settings.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'settings.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        if products_aid and product_id:
            open_action(page, products_aid)
            page.wait_for_timeout(2000)
            page.screenshot(path=str(shots_dir / 'report.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'reports.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        if product_id:
            open_record_form(page, 'product.template', product_id)
            page.set_viewport_size({'width': 390, 'height': 844})
            page.wait_for_timeout(1500)
            page.screenshot(path=str(shots_dir / 'mobile.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'mobile.gif', steps=6)

        if templates_aid and product_id:
            frames: list[Path] = []
            for action in (
                lambda: open_action(page, templates_aid),
                lambda: open_record_form(page, 'product.template', product_id),
                lambda: (try_click_suggest_name(page), wait_for_wizard(page)),
            ):
                action()
                page.wait_for_timeout(GIF_INTERVAL * 1000)
                tmp = Path(tempfile.mkstemp(suffix='.png')[1])
                page.screenshot(path=str(tmp), full_page=False)
                frames.append(tmp)
            frames_to_gif(frames, gifs_dir / 'workflow.gif', frame_duration=GIF_INTERVAL)
            for fr in frames:
                fr.unlink(missing_ok=True)

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
    if not meta.get('product_id'):
        raise SystemExit('Capture seed failed: no product_id')
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
