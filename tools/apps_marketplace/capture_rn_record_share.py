#!/usr/bin/env python3
"""Capture live Record Share screenshots and GIFs for Apps Store assets."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_record_share'
MOD_DIR = ROOT / MODULE
PY = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/venv310/bin/python')
ODOO_BIN = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/odoo-bin')
RC = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/.openerp_serverrc')

BASE = 'http://127.0.0.1:9196'
DB = 'armora_apps'
USER = 'admin'
PASSWORD = 'admin'
GIF_SECONDS = 12
GIF_INTERVAL = 2

SCREENSHOTS = (
    'workflow.png',
    'dashboard.png',
    'designer.png',
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

Partner = env['res.partner']
partner = Partner.search([('name', '=', 'ShareCap Demo Customer')], limit=1)
if not partner:
    partner = Partner.create({
        'name': 'ShareCap Demo Customer',
        'email': 'sharecap.demo@armorait.com',
        'is_company': True,
    })

manager = env.ref('rn_record_share.group_rn_record_share_manager', raise_if_not_found=False)
user = env.ref('base.user_admin')
if manager:
    user.write({'group_ids': [(4, manager.id)]})

out = {
    'partner_id': partner.id,
    'history_action_id': env.ref('rn_record_share.action_rn_share_log').id,
    'settings_action_id': env.ref('base.res_config_setting_act_window').id,
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


def open_partner_form(page, partner_id: int, *, mobile: bool = False) -> None:
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    page.goto(f'{BASE}/odoo/res.partner/{partner_id}', wait_until='domcontentloaded', timeout=120000)
    page.wait_for_timeout(5000)
    page.wait_for_selector('.o_form_view, .o_content', timeout=30000)


def open_action(page, action_id: int) -> None:
    page.set_viewport_size({'width': 1440, 'height': 900})
    page.evaluate('(id) => { window.location.hash = "#action=" + id; }', str(action_id))
    page.wait_for_timeout(4500)
    page.wait_for_selector('.o_action_manager, .o_web_client', timeout=60000)


def copy_placeholders() -> None:
    src = ROOT / 'rn_smart_search' / 'static' / 'description'
    desc = MOD_DIR / 'static' / 'description'
    desc.mkdir(parents=True, exist_ok=True)
    for name in (*SCREENSHOTS, *GIFS, 'overview.png', 'list.png', 'form.png'):
        src_file = src / name
        if src_file.exists():
            shutil.copy2(src_file, desc / name)


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

        if meta.get('partner_id'):
            open_partner_form(page, meta['partner_id'])
            page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'workflow.gif', steps=GIF_SECONDS // GIF_INTERVAL)
            record_scroll_gif(page, gifs_dir / 'hero.gif', steps=max(4, GIF_SECONDS // GIF_INTERVAL))

            share_btn = page.locator('button:has-text("Share"), .o_stat_text:has-text("Share")').first
            if share_btn.count():
                share_btn.click()
                page.wait_for_timeout(3000)
                page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)
                record_scroll_gif(page, gifs_dir / 'dashboard.gif', steps=6)

            open_partner_form(page, meta['partner_id'], mobile=True)
            page.screenshot(path=str(shots_dir / 'mobile.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'mobile.gif', steps=6)

        if meta.get('history_action_id'):
            open_action(page, meta['history_action_id'])
            page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'reports.gif', steps=6)

        if meta.get('settings_action_id'):
            open_action(page, meta['settings_action_id'])
            page.wait_for_timeout(2500)
            page.screenshot(path=str(shots_dir / 'settings.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'settings.gif', steps=6)

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
    print(f'Seeding demo data for {MODULE}...')
    meta = seed_demo_data()
    print(json.dumps(meta, indent=2))
    try:
        capture_assets(meta)
        print('Live capture completed.')
    except Exception as exc:
        print(f'Live capture failed ({exc}); copying placeholder assets.', file=sys.stderr)
        copy_placeholders()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
