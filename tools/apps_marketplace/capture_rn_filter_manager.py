#!/usr/bin/env python3
"""Capture live Filter Manager screenshots and GIFs for Apps Store assets."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_filter_manager'
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
Folder = env['rn.filter.folder']
Filters = env['ir.filters']
Service = env['rn.filter.service']

sales = Folder.search([('name', '=', 'Sales')], limit=1)
if not sales:
    sales = Folder.create({'name': 'Sales', 'color': 'green', 'icon': 'fa-shopping-cart'})
invoices = Folder.search([('name', '=', 'Invoices')], limit=1)
if not invoices:
    invoices = Folder.create({'name': 'Invoices', 'color': 'blue', 'icon': 'fa-file-text-o'})

def ensure_filter(name, model, domain, folder, **extra):
    filt = Filters.search([('name', '=', name)], limit=1)
    vals = {
        'name': name,
        'model_id': model,
        'domain': domain,
        'context': '{}',
        'sort': '[]',
        'rn_folder_id': folder.id,
        'user_ids': [(6, 0, [env.user.id])],
    }
    vals.update(extra)
    if filt:
        filt.write(vals)
    else:
        filt = Filters.create(vals)
    Service.log_filter_usage(filt, source='manager')
    return filt

ensure_filter('FILTCAP Confirmed Sales', 'sale.order', "[('state', '=', 'sale')]", sales,
              rn_is_pinned=True, rn_is_favorite=True, rn_color='green', rn_share_type='favorite')
ensure_filter('FILTCAP Draft Sales', 'sale.order', "[('state', '=', 'draft')]", sales,
              rn_is_favorite=True, rn_share_type='private')
ensure_filter('FILTCAP Overdue Invoices', 'account.move',
              "[('move_type', '=', 'out_invoice'), ('payment_state', '!=', 'paid')]", invoices,
              rn_is_pinned=True, rn_color='red', rn_share_type='company')

def action_id(xmlid):
    rec = env.ref(xmlid, raise_if_not_found=False)
    return rec.id if rec else False

filt = Filters.search([('name', '=', 'FILTCAP Confirmed Sales')], limit=1)
out = {
    'filter_id': filt.id if filt else False,
    'folder_id': sales.id,
    'all_action_id': action_id('rn_filter_manager.action_rn_filter_all'),
    'favorites_action_id': action_id('rn_filter_manager.action_rn_filter_favorites'),
    'recent_action_id': action_id('rn_filter_manager.action_rn_filter_recent'),
    'folders_action_id': action_id('rn_filter_manager.action_rn_filter_folder'),
    'import_action_id': action_id('rn_filter_manager.action_rn_filter_import_export_wizard'),
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
        ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst.name,
         '-vf', 'fps=5,scale=900:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
         '-loop', '0', str(out)],
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


def open_action(page, action_id: int, mobile: bool = False) -> None:
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    page.evaluate('(id) => { window.location.hash = "#action=" + id; }', str(action_id))
    page.wait_for_timeout(4500)
    page.evaluate("document.querySelectorAll('.o-mail-Chatter,.o_Chatter').forEach(e => e.remove())")


def open_record_form(page, model: str, record_id: int) -> None:
    page.set_viewport_size({'width': 1440, 'height': 900})
    page.goto(f'{BASE}/odoo/{model}/{record_id}', wait_until='domcontentloaded', timeout=120000)
    page.wait_for_timeout(4500)
    page.evaluate("document.querySelectorAll('.o-mail-Chatter,.o_Chatter').forEach(e => e.remove())")


def open_settings(page) -> None:
    page.goto(f'{BASE}/odoo/settings', wait_until='domcontentloaded', timeout=120000)
    page.wait_for_timeout(3500)
    for selector in ('button:has-text("Filter Manager")', 'a:has-text("Filter Manager")'):
        try:
            page.click(selector, timeout=3000)
            page.wait_for_timeout(2000)
            break
        except Exception:
            continue


def capture_assets(meta: dict) -> None:
    shots_dir = MOD_DIR / 'marketplace' / 'screenshots'
    gifs_dir = MOD_DIR / 'marketplace' / 'gifs'
    desc_dir = MOD_DIR / 'static' / 'description'
    for folder in (shots_dir, gifs_dir, desc_dir):
        folder.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login(page)

        all_aid = meta.get('all_action_id')
        fav_aid = meta.get('favorites_action_id')
        recent_aid = meta.get('recent_action_id')
        folders_aid = meta.get('folders_action_id')
        import_aid = meta.get('import_action_id')
        filter_id = meta.get('filter_id')

        if all_aid:
            open_action(page, all_aid)
            page.screenshot(path=str(shots_dir / 'list.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'overview.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'search.png'), full_page=False)

        if filter_id:
            open_record_form(page, 'ir.filters', filter_id)
            page.screenshot(path=str(shots_dir / 'form.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)

        if recent_aid:
            open_action(page, recent_aid)
            page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)

        if folders_aid:
            open_action(page, folders_aid)
            page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'kanban.png'), full_page=False)

        if fav_aid:
            open_action(page, fav_aid)
            page.screenshot(path=str(shots_dir / 'report.png'), full_page=False)

        if import_aid:
            open_action(page, import_aid)
            page.wait_for_timeout(2500)
            page.screenshot(path=str(shots_dir / 'wizard.png'), full_page=False)

        open_settings(page)
        page.screenshot(path=str(shots_dir / 'settings.png'), full_page=False)

        if all_aid and folders_aid:
            frames = []
            for aid in (folders_aid, all_aid, fav_aid or all_aid):
                if not aid:
                    continue
                open_action(page, aid)
                page.wait_for_timeout(GIF_INTERVAL * 1000)
                tmp = Path(tempfile.mkstemp(suffix='.png')[1])
                page.screenshot(path=str(tmp), full_page=False)
                frames.append(tmp)
            frames_to_gif(frames[:4], gifs_dir / 'hero.gif')
            frames_to_gif(frames[:4], gifs_dir / 'workflow.gif')
            for f in frames:
                f.unlink(missing_ok=True)

        if recent_aid:
            open_action(page, recent_aid)
            frames = []
            for _ in range(4):
                tmp = Path(tempfile.mkstemp(suffix='.png')[1])
                page.screenshot(path=str(tmp), full_page=False)
                frames.append(tmp)
                page.wait_for_timeout(GIF_INTERVAL * 1000)
            frames_to_gif(frames, gifs_dir / 'dashboard.gif')
            for f in frames:
                f.unlink(missing_ok=True)

        open_settings(page)
        frames = []
        for _ in range(4):
            tmp = Path(tempfile.mkstemp(suffix='.png')[1])
            page.screenshot(path=str(tmp), full_page=False)
            frames.append(tmp)
            page.wait_for_timeout(GIF_INTERVAL * 1000)
        frames_to_gif(frames, gifs_dir / 'settings.gif')
        for f in frames:
            f.unlink(missing_ok=True)

        if import_aid:
            open_action(page, import_aid)
            frames = []
            for _ in range(3):
                tmp = Path(tempfile.mkstemp(suffix='.png')[1])
                page.screenshot(path=str(tmp), full_page=False)
                frames.append(tmp)
                page.wait_for_timeout(GIF_INTERVAL * 1000)
            frames_to_gif(frames, gifs_dir / 'reports.gif')
            for f in frames:
                f.unlink(missing_ok=True)

        if all_aid:
            open_action(page, all_aid, mobile=True)
            page.screenshot(path=str(shots_dir / 'mobile.png'), full_page=False)
            frames = []
            for _ in range(3):
                tmp = Path(tempfile.mkstemp(suffix='.png')[1])
                page.screenshot(path=str(tmp), full_page=False)
                frames.append(tmp)
                page.wait_for_timeout(GIF_INTERVAL * 1000)
            frames_to_gif(frames, gifs_dir / 'mobile.gif')
            for f in frames:
                f.unlink(missing_ok=True)

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
    if not meta.get('all_action_id'):
        raise SystemExit('Install rn_filter_manager before capture.')
    capture_assets(meta)
    subprocess.run([sys.executable, str(ROOT / 'build_marketplace.py'), MODULE, '--no-docs'], cwd=str(ROOT), check=True)
    print('Captured live assets for', MODULE)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
