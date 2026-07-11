#!/usr/bin/env python3
"""Capture live Bookmarks screenshots and GIFs for Apps Store assets."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_bookmarks'
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
Folder = env['rn.bookmark.folder']
Bookmark = env['rn.bookmark']
Service = env['rn.bookmark.service']
Tag = env['rn.bookmark.tag']

sales = Folder.search([('name', '=', 'Sales')], limit=1)
if not sales:
    sales = Folder.create({'name': 'Sales', 'color': 'green', 'icon': 'fa-shopping-cart'})
invoices = Folder.search([('name', '=', 'Invoices')], limit=1)
if not invoices:
    invoices = Folder.create({'name': 'Invoices', 'color': 'blue', 'icon': 'fa-file-text-o'})
crm = Folder.search([('name', '=', 'CRM')], limit=1)
if not crm:
    crm = Folder.create({'name': 'CRM', 'color': 'purple', 'icon': 'fa-users'})

vip = Tag.search([('name', '=', 'VIP')], limit=1)
if not vip:
    vip = Tag.create({'name': 'VIP', 'color': 'purple'})
urgent = Tag.search([('name', '=', 'Urgent')], limit=1)
if not urgent:
    urgent = Tag.create({'name': 'Urgent', 'color': 'red'})

partner = env['res.partner'].search([('name', 'ilike', 'Azure')], limit=1)
if not partner:
    partner = env['res.partner'].create({'name': 'Azure Technologies'})
order = env['sale.order'].search([], limit=1)
if not order:
    order = env['sale.order'].create({'partner_id': partner.id})

def ensure_record_bookmark(record, folder, **extra):
    bm = Bookmark.search([
        ('bookmark_type', '=', 'record'),
        ('res_model', '=', record._name),
        ('res_id', '=', record.id),
        ('user_id', '=', env.user.id),
    ], limit=1)
    vals = {
        'name': record.display_name,
        'bookmark_type': 'record',
        'res_model': record._name,
        'res_id': record.id,
        'folder_id': folder.id,
        'user_id': env.user.id,
    }
    vals.update(extra)
    if bm:
        bm.write(vals)
    else:
        bm = Bookmark.create(vals)
    return bm

bm_order = ensure_record_bookmark(order, sales, is_pinned=True, is_favorite=True, color='green',
                                  tag_ids=[(6, 0, [urgent.id])], note='Customer waiting.')
bm_partner = ensure_record_bookmark(partner, crm, is_favorite=True, color='purple',
                                    tag_ids=[(6, 0, [vip.id])])
list_bm = Bookmark.search([('name', '=', 'BMCAP Draft Sales')], limit=1)
if not list_bm:
    list_bm = Service.create_list_bookmark(
        'BMCAP Draft Sales', 'sale.order', domain=[('state', '=', 'draft')], folder_id=sales.id,
    )
list_bm.write({'is_pinned': True, 'note': 'Overdue follow-up list'})

def action_id(xmlid):
    rec = env.ref(xmlid, raise_if_not_found=False)
    return rec.id if rec else False

out = {
    'bookmark_id': bm_order.id,
    'sale_order_id': order.id,
    'partner_id': partner.id,
    'all_action_id': action_id('rn_bookmarks.action_rn_bookmark_all'),
    'pinned_action_id': action_id('rn_bookmarks.action_rn_bookmark_pinned'),
    'favorites_action_id': action_id('rn_bookmarks.action_rn_bookmark_favorites'),
    'recent_action_id': action_id('rn_bookmarks.action_rn_bookmark_recent'),
    'folders_action_id': action_id('rn_bookmarks.action_rn_bookmark_folder'),
    'dashboard_action_id': action_id('rn_bookmarks.action_rn_bookmark_dashboard'),
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
    for selector in ('button:has-text("Bookmarks")', 'a:has-text("Bookmarks")'):
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
        pinned_aid = meta.get('pinned_action_id')
        fav_aid = meta.get('favorites_action_id')
        recent_aid = meta.get('recent_action_id')
        folders_aid = meta.get('folders_action_id')
        dashboard_aid = meta.get('dashboard_action_id')
        sale_order_id = meta.get('sale_order_id')
        bookmark_id = meta.get('bookmark_id')

        if all_aid:
            open_action(page, all_aid)
            page.screenshot(path=str(shots_dir / 'list.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'overview.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'search.png'), full_page=False)

        if bookmark_id:
            open_record_form(page, 'rn.bookmark', bookmark_id)
            page.screenshot(path=str(shots_dir / 'form.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)

        if sale_order_id:
            open_record_form(page, 'sale.order', sale_order_id)
            page.screenshot(path=str(shots_dir / 'wizard.png'), full_page=False)

        if dashboard_aid:
            open_action(page, dashboard_aid)
            page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)

        if folders_aid:
            open_action(page, folders_aid)
            page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'kanban.png'), full_page=False)

        if pinned_aid:
            open_action(page, pinned_aid)
            page.screenshot(path=str(shots_dir / 'report.png'), full_page=False)

        if fav_aid:
            open_action(page, fav_aid)
            page.wait_for_timeout(1500)

        open_settings(page)
        page.screenshot(path=str(shots_dir / 'settings.png'), full_page=False)

        if all_aid and folders_aid:
            frames = []
            for aid in (folders_aid, all_aid, pinned_aid or all_aid):
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

        if dashboard_aid:
            open_action(page, dashboard_aid)
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

        if sale_order_id:
            open_record_form(page, 'sale.order', sale_order_id)
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
        raise SystemExit('Install rn_bookmarks before capture.')
    capture_assets(meta)
    subprocess.run([sys.executable, str(ROOT / 'build_marketplace.py'), MODULE, '--no-docs'], cwd=str(ROOT), check=True)
    print('Captured live assets for', MODULE)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
