#!/usr/bin/env python3
"""Capture live Domain Builder screenshots and GIFs for Apps Store assets."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_domain_builder'
MOD_DIR = ROOT / MODULE
PY = Path('/home/lenovo/bin/packages/PyCharm/odoovenvs/py310venv/bin/python')
ODOO_BIN = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/odoo-bin')
RC = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/.openerp_serverrc')

BASE = 'http://127.0.0.1:9196'
DB = 'armora_apps'
USER = 'admin'
PASSWORD = 'admin'
GIF_SECONDS = 10
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


BUILDER_ACTION_ID = 646
DICTIONARY_ACTION_ID = 647
HISTORY_ACTION_ID = 648


def seed_demo_data() -> dict:
    return {
        'builder_action_id': BUILDER_ACTION_ID,
        'dictionary_action_id': DICTIONARY_ACTION_ID,
        'history_action_id': HISTORY_ACTION_ID,
    }


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


def open_action(page, action_id: int, *, mobile: bool = False) -> None:
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    page.evaluate('(id) => { window.location.hash = "#action=" + id; }', str(action_id))
    page.wait_for_timeout(4500)


def open_builder_wizard(page) -> None:
    page.set_viewport_size({'width': 1440, 'height': 900})
    action_id = resolve_action_id(page, 'rn_domain_builder.action_rn_domain_builder')
    if action_id:
        page.evaluate('(id) => { window.location.hash = "#action=" + id; }', str(action_id))
        page.wait_for_timeout(4500)
    page.wait_for_selector('.o_form_view', timeout=60000)
    desc = page.locator('textarea[name="description"], .o_field_widget[name="description"] textarea')
    if desc.count():
        desc.first.fill('confirmed quotations')
    page.click('button[name="action_generate"], footer button:has-text("Generate")')
    page.wait_for_timeout(2500)


def open_menu_action(page, menu_name: str) -> None:
    page.click(f'.o_menu_sections button:has-text("{menu_name}"), .o_navbar_apps_menu button')
    page.wait_for_timeout(800)
    page.click(f'a:has-text("{menu_name}"), button:has-text("{menu_name}")')
    page.wait_for_timeout(3500)


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

        open_action(page, meta['builder_action_id'])
        page.wait_for_timeout(5000)
        page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)
        page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)
        record_scroll_gif(page, gifs_dir / 'hero.gif', steps=5)
        record_scroll_gif(page, gifs_dir / 'workflow.gif', steps=5)

        open_action(page, meta['dictionary_action_id'])
        page.wait_for_timeout(2500)
        page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)
        record_scroll_gif(page, gifs_dir / 'dashboard.gif', steps=5)
        record_scroll_gif(page, gifs_dir / 'settings.gif', steps=5)

        open_action(page, meta['history_action_id'])
        page.wait_for_timeout(2500)
        record_scroll_gif(page, gifs_dir / 'reports.gif', steps=5)

        page.set_viewport_size({'width': 390, 'height': 844})
        open_action(page, meta['builder_action_id'], mobile=True)
        page.wait_for_timeout(3000)
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
