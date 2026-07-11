#!/usr/bin/env python3
"""Capture live Smart Duplicate Finder screenshots and GIFs for Apps Store assets."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_duplicate_finder'
MOD_DIR = ROOT / MODULE
PY = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/venv310/bin/python')
ODOO_BIN = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/odoo-bin')
RC = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS/.openerp_serverrc')

BASE = 'http://127.0.0.1:9196'
DB = 'armora_apps'
USER = 'admin'
PASSWORD = 'admin'
GIF_SECONDS = 18
GIF_INTERVAL = 2

SCREENSHOTS = (
    'overview.png',
    'list.png',
    'form.png',
    'dashboard.png',
    'wizard.png',
    'settings.png',
    'report.png',
    'search.png',
    'kanban.png',
    'mobile.png',
    'workflow.png',
    'designer.png',
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
Rule = env['rn.dup.rule']
ScanService = env['rn.dup.scan.service']

partners = [
    ('DUPCAP Acme Supplies', 'dupcap.acme@armorait.com'),
    ('DUPCAP ACME Supplies Ltd', 'dupcap.acme@armorait.com'),
    ('DUPCAP Blue Desk Co', 'dupcap.blue@armorait.com'),
    ('DUPCAP BlueDesk Company', 'dupcap.blue@armorait.com'),
]
for name, email in partners:
    if not Partner.search([('name', '=', name)], limit=1):
        Partner.create({'name': name, 'email': email, 'is_company': False})

rule = Rule.search([('name', '=', 'DUPCAP Live Capture Rule')], limit=1)
if not rule:
    rule = Rule.create({
        'name': 'DUPCAP Live Capture Rule',
        'model_id': env.ref('base.model_res_partner').id,
        'match_threshold': 80.0,
        'record_domain': "[('name', 'ilike', 'DUPCAP%')]",
        'field_line_ids': [
            (0, 0, {'field_name': 'email', 'match_type': 'exact', 'weight': 60}),
            (0, 0, {'field_name': 'name', 'match_type': 'fuzzy', 'weight': 40}),
        ],
    })

scan = ScanService.run_rule_scan(rule)
result = env['rn.dup.result'].search([
    ('scan_id', '=', scan.id),
    ('state', '=', 'new'),
], order='score desc', limit=1)

def action_id(xmlid):
    rec = env.ref(xmlid, raise_if_not_found=False)
    return rec.id if rec else False

out = {
    'rule_id': rule.id,
    'scan_id': scan.id,
    'result_id': result.id if result else False,
    'match_count': scan.match_count,
    'rules_action_id': action_id('rn_duplicate_finder.action_rn_dup_rule'),
    'matches_action_id': action_id('rn_duplicate_finder.action_rn_dup_result'),
    'scans_action_id': action_id('rn_duplicate_finder.action_rn_dup_scan'),
    'ignore_action_id': action_id('rn_duplicate_finder.action_rn_dup_ignore'),
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


def record_action_sequence_gif(page, action_ids: list[int], out: Path) -> None:
    frames: list[Path] = []
    per_action = max(2, (GIF_SECONDS // GIF_INTERVAL) // max(1, len(action_ids)))
    for action_id in action_ids:
        open_action(page, action_id)
        for i in range(per_action):
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
    page.wait_for_selector('.o_action_manager, .o_web_client', timeout=60000)
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
            break
        except Exception:
            continue
    page.evaluate(
        "document.querySelectorAll('.o-mail-Chatter,.o_Chatter').forEach(e => e.remove())"
    )


def try_open_first_record(page) -> bool:
    for sel in (
        '.o_list_table tbody tr:first-child td.o_data_cell',
        '.o_list_renderer tbody tr:first-child td.o_data_cell',
        '.o_kanban_record:first-child',
    ):
        try:
            page.click(sel, timeout=3000)
            page.wait_for_timeout(2500)
            return True
        except Exception:
            continue
    return False


def try_open_merge_wizard(page) -> bool:
    for sel in (
        'button[name="action_open_merge_wizard"]',
        '.o_form_view button:has-text("Merge")',
    ):
        try:
            page.click(sel, timeout=4000)
            page.wait_for_timeout(2500)
            return True
        except Exception:
            continue
    return False


def capture_assets(meta: dict) -> None:
    shots_dir = MOD_DIR / 'marketplace' / 'screenshots'
    gifs_dir = MOD_DIR / 'marketplace' / 'gifs'
    desc_dir = MOD_DIR / 'static' / 'description'
    for d in (shots_dir, gifs_dir, desc_dir):
        d.mkdir(parents=True, exist_ok=True)

    rules_aid = meta.get('rules_action_id')
    matches_aid = meta.get('matches_action_id')
    scans_aid = meta.get('scans_action_id')
    ignore_aid = meta.get('ignore_action_id')
    rule_id = meta.get('rule_id')
    scan_id = meta.get('scan_id')
    result_id = meta.get('result_id')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login(page)

        if rules_aid:
            open_action(page, rules_aid)
            page.screenshot(path=str(shots_dir / 'list.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'overview.png'), full_page=False)
            if rule_id:
                open_record_form(page, 'rn.dup.rule', rule_id)
                page.screenshot(path=str(shots_dir / 'form.png'), full_page=False)
                page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)

        if matches_aid:
            open_action(page, matches_aid)
            page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'search.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'kanban.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'dashboard.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        if result_id:
            open_record_form(page, 'rn.dup.result', result_id)
            page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)
            if try_open_merge_wizard(page):
                page.wait_for_timeout(2000)
                page.screenshot(path=str(shots_dir / 'wizard.png'), full_page=False)

        if scans_aid:
            open_action(page, scans_aid)
            if scan_id and try_open_first_record(page):
                open_record_form(page, 'rn.dup.scan', scan_id)
            page.screenshot(path=str(shots_dir / 'report.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'reports.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        if ignore_aid:
            open_action(page, ignore_aid)
            page.screenshot(path=str(shots_dir / 'settings.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'settings.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        if matches_aid:
            open_action(page, matches_aid, mobile=True)
            page.screenshot(path=str(shots_dir / 'mobile.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'mobile.gif', steps=6)

        hero_actions = [aid for aid in (rules_aid, matches_aid, scans_aid) if aid]
        if hero_actions:
            record_action_sequence_gif(page, hero_actions, gifs_dir / 'hero.gif')
        if rules_aid and matches_aid:
            record_action_sequence_gif(page, [rules_aid, matches_aid], gifs_dir / 'workflow.gif')

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
    if not meta.get('match_count'):
        raise SystemExit('Capture seed scan produced no matches. Check demo data.')
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
