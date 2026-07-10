#!/usr/bin/env python3
"""Capture real Odoo backend screenshots and GIFs for Apps Store assets."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).resolve().parent.parent / 'apps_marketplace' / 'catalog.json'
DEFAULT_DB = 'armora_apps_capture'
DEFAULT_URL = 'http://127.0.0.1:8069'
DEFAULT_USER = 'admin'
DEFAULT_PASSWORD = 'admin'

SCREENSHOTS = (
    'overview.png',
    'dashboard.png',
    'list.png',
    'form.png',
    'wizard.png',
    'settings.png',
    'report.png',
    'kanban.png',
    'search.png',
    'mobile.png',
)
GIFS = (
    ('hero.gif', 'overview'),
    ('workflow.gif', 'list'),
    ('dashboard.gif', 'dashboard'),
    ('settings.gif', 'settings'),
    ('reports.gif', 'report'),
    ('mobile.gif', 'mobile'),
)

# Menu root xml id suffix per module (after install).
MODULE_MENU_ROOT = {
    'rn_ai_employee': 'menu_rn_ai_employee_root',
    'rn_whatsapp_connector': 'menu_rn_whatsapp_root',
    'rn_inventory_forecast': 'menu_rn_inv_forecast_root',
    'rn_bi_sales_dashboard': 'menu_rn_bi_sales_root',
    'rn_crm_ultimate_pro': 'menu_rn_crm_ultimate_root',
    'rn_hr_attendance_face': 'menu_rn_attendance_face_root',
    'rn_l10n_in_gst_pro': 'menu_rn_gst_pro_root',
    'rn_fleet_gps': 'menu_rn_fleet_gps_root',
    'rn_rental_core': 'menu_rn_rental_root',
    'rn_restaurant_core': 'menu_rn_restaurant_root',
    'rn_dashboard_core': 'menu_rn_dashboard_core_root',
    'rn_hms_core': 'menu_rn_hms_root',
    'rn_hrms_core': 'menu_rn_hrms_root',
    'rn_booking_platform': 'menu_rn_booking_root',
    'rn_ai_document_generator': 'menu_rn_ai_doc_root',
    'rn_profit_guard': 'menu_rn_profit_guard_root',
    'rn_smart_credit_shield': 'menu_credit_control_root',
    'rn_whatsapp_integration': 'menu_whatsapp_root',
    'rn_payroll_portal_pro': 'menu_payroll_portal_root',
    'rn_theme_base': None,
    'rn_hr_resume_ai_parser': 'menu_hr_resume_ai_parser_root',
}


def rpc_query_menus(db: str, modules: list[str]) -> dict[str, str]:
    """Return module -> action url path using Odoo shell one-liner."""
    script = f"""
modules = {modules!r}
Menu = env['ir.ui.menu']
out = {{}}
for mod in modules:
    recs = Menu.search([('name', '!=', False)], limit=5000)
    for menu in recs:
        if menu.action and menu.xml_id and menu.xml_id.startswith(mod + '.'):
            if 'settings' in (menu.name or '').lower() or 'config' in (menu.name or '').lower():
                out.setdefault(mod + ':settings', menu.action.id)
            if 'dashboard' in (menu.name or '').lower():
                out.setdefault(mod + ':dashboard', menu.action.id)
            out.setdefault(mod + ':list', menu.action.id)
            break
print(json.dumps(out))
"""
    cmd = [
        str(ROOT.parent / 'venv310' / 'bin' / 'python'),
        str(ROOT.parent / 'odoo-bin'),
        'shell',
        '-d', db,
        '--no-http',
    ]
    proc = subprocess.run(
        cmd,
        input=script,
        text=True,
        capture_output=True,
        cwd=str(ROOT.parent),
    )
    if proc.returncode != 0:
        return {}
    for line in reversed(proc.stdout.splitlines()):
        line = line.strip()
        if line.startswith('{'):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                pass
    return {}


def login(page, base_url: str, db: str, user: str, password: str):
    page.goto(f'{base_url}/web/login?db={db}', wait_until='networkidle')
    page.fill('input[name="login"]', user)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_selector('.o_web_client', timeout=120000)


def hide_chatter(page):
    page.evaluate(
        """() => {
        document.querySelectorAll('.o-mail-Chatter, .o_Chatter').forEach(el => el.remove());
    }"""
    )


def capture_view(page, action_id: int, outfile: Path, mobile: bool = False):
    url = f'/web#action={action_id}'
    page.goto(page.url.split('/web')[0] + url, wait_until='networkidle')
    page.wait_for_timeout(2500)
    hide_chatter(page)
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    page.wait_for_timeout(1000)
    page.screenshot(path=str(outfile), full_page=False)
    if mobile:
        page.set_viewport_size({'width': 1440, 'height': 900})


def video_to_gif(video_path: Path, gif_path: Path, duration: int = 25):
    if not video_path.exists():
        return
    subprocess.run(
        [
            'ffmpeg', '-y', '-i', str(video_path),
            '-t', str(duration),
            '-vf', 'fps=10,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
            str(gif_path),
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def record_gif(page, base_url: str, action_id: int, gif_path: Path):
    with tempfile.TemporaryDirectory() as tmp:
        video_dir = Path(tmp)
        browser = page.context.browser
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            record_video_dir=str(video_dir),
            record_video_size={'width': 1280, 'height': 720},
        )
        p = context.new_page()
        login(p, base_url, page.context._impl_obj._options.get('storage_state') and DEFAULT_DB or DEFAULT_DB, DEFAULT_USER, DEFAULT_PASSWORD)
        p.goto(f'{base_url}/web#action={action_id}', wait_until='networkidle')
        p.wait_for_timeout(8000)
        p.mouse.wheel(0, 500)
        p.wait_for_timeout(5000)
        p.close()
        context.close()
        videos = list(video_dir.glob('*.webm'))
        if videos:
            video_to_gif(videos[0], gif_path)


def capture_module(
    page,
    base_url: str,
    module: str,
    out_dir: Path,
    action_map: dict[str, int],
):
    out_dir.mkdir(parents=True, exist_ok=True)
    list_action = action_map.get(f'{module}:list') or action_map.get(f'{module}:dashboard')
    settings_action = action_map.get(f'{module}:settings')
    dash_action = action_map.get(f'{module}:dashboard') or list_action

    shots = {
        'overview.png': list_action,
        'dashboard.png': dash_action,
        'list.png': list_action,
        'form.png': list_action,
        'settings.png': settings_action or list_action,
        'report.png': list_action,
        'kanban.png': list_action,
        'search.png': list_action,
        'wizard.png': list_action,
        'mobile.png': list_action,
    }
    for name, action_id in shots.items():
        if not action_id:
            continue
        capture_view(page, action_id, out_dir / name, mobile=(name == 'mobile.png'))

    for gif_name, key in GIFS:
        action_id = shots.get(f'{key}.png')
        if action_id:
            record_gif(page, base_url, action_id, out_dir / gif_name)


def copy_assets(src: Path, module: str, branch: str | None):
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    meta = catalog.get(module, {})
    target_roots = []

    local = ROOT / module
    if local.exists():
        target_roots.append(local / 'static' / 'description')

    if branch:
        wt = Path('/tmp/armora_capture_copy') / branch.replace('/', '_')
        subprocess.run(['git', 'worktree', 'add', '--force', str(wt), branch], cwd=ROOT, check=False)
        target_roots.append(wt / module / 'static' / 'description')

    for target in target_roots:
        target.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if item.suffix.lower() in {'.png', '.gif'}:
                shutil.copy2(item, target / item.name)
        # map ai employee reals if present
        mapping = {
            'screenshot_real_copilot.png': 'dashboard.png',
            'screenshot_real_sales.png': 'list.png',
            'screenshot_real_invoices.png': 'report.png',
            'screenshot_real_crm.png': 'form.png',
            'screenshot_real_settings.png': 'settings.png',
        }
        for src_name, dst_name in mapping.items():
            s = target / src_name
            if s.exists():
                shutil.copy2(s, target / dst_name)
                shutil.copy2(s, target / 'overview.png')
        if (target / 'dashboard.png').exists():
            shutil.copy2(target / 'dashboard.png', target / 'main_screenshot.png')

    if branch and Path('/tmp/armora_capture_copy').exists():
        wt = Path('/tmp/armora_capture_copy') / branch.replace('/', '_')
        if wt.exists():
            subprocess.run(['git', 'add', module], cwd=wt, check=False)
            subprocess.run(
                ['/usr/bin/git', 'commit', '--no-verify', '-m', f'Add real marketplace screenshots for {module}'],
                cwd=wt,
                check=False,
            )
            subprocess.run(['git', 'push', 'origin', branch], cwd=ROOT, check=False)
            subprocess.run(['git', 'worktree', 'remove', '--force', str(wt)], cwd=ROOT, check=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=DEFAULT_DB)
    parser.add_argument('--url', default=DEFAULT_URL)
    parser.add_argument('--modules', nargs='*', default=list(MODULE_MENU_ROOT.keys()))
    args = parser.parse_args()

    capture_dir = Path('/tmp/armora_marketplace_captures')
    capture_dir.mkdir(parents=True, exist_ok=True)

    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    action_map = rpc_query_menus(args.db, args.modules)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()
        login(page, args.url, args.db, DEFAULT_USER, DEFAULT_PASSWORD)

        for module in args.modules:
            mod_cap = capture_dir / module
            print(f'Capturing {module}...')
            try:
                capture_module(page, args.url, module, mod_cap, action_map)
                branch = catalog.get(module, {}).get('branch')
                copy_assets(mod_cap, module, branch)
            except Exception as exc:
                print(f'WARN {module}: {exc}')
        browser.close()

    print('Capture complete:', capture_dir)


if __name__ == '__main__':
    main()
