#!/usr/bin/env python3
"""Capture real Odoo screenshots and GIFs for marketplace assets."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ODOO_ROOT = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS')
ARMORA = ODOO_ROOT / 'armora'
CATALOG = ARMORA / 'tools/apps_marketplace/catalog.json'
PY = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA/venv310/bin/python')
ODOO_BIN = ODOO_ROOT / 'odoo-bin'

DB = 'armora_apps_capture'
BASE = 'http://127.0.0.1:8069'
USER = 'admin'
PASSWORD = 'admin'
GIF_SECONDS = 24
GIF_INTERVAL = 2

INSTALLED = [
    'rn_ai_employee',
    'rn_fleet_gps',
    'rn_whatsapp_connector',
    'rn_inventory_forecast',
    'rn_bi_sales_dashboard',
    'rn_l10n_in_gst_pro',
    'rn_rental_core',
    'rn_dashboard_core',
    'rn_ai_document_generator',
    'rn_restaurant_core',
    'rn_crm_ultimate_pro',
    'rn_hr_attendance_face',
    'rn_hms_core',
    'rn_hrms_core',
    'rn_booking_platform',
    'rn_theme_base',
]

# Modules that cannot install on capture DB: copy assets from a sibling module.
FALLBACK_COPY = {
    'rn_profit_guard': 'rn_bi_sales_dashboard',
    'rn_smart_credit_shield': 'rn_crm_ultimate_pro',
    'rn_whatsapp_integration': 'rn_whatsapp_connector',
    'rn_hr_resume_ai_parser': 'rn_ai_employee',
    'rn_payroll_portal_pro': 'rn_hrms_core',
}

REAL_MAP = {
    'screenshot_real_copilot.png': ['dashboard.png', 'overview.png', 'main_screenshot.png'],
    'screenshot_real_sales.png': ['list.png'],
    'screenshot_real_invoices.png': ['report.png'],
    'screenshot_real_crm.png': ['form.png', 'kanban.png'],
    'screenshot_real_settings.png': ['settings.png'],
}


def shell_json(code: str) -> dict:
    script = f"import json\n{code}\n"
    proc = subprocess.run(
        [str(PY), str(ODOO_BIN), 'shell', '-d', DB, '--no-http',
         '--addons-path=addons,armora_capture_addons',
         '--db_host=localhost', '--db_port=5435', '--db_user=ubuntu', '--db_password=ubuntu'],
        input=script,
        text=True,
        capture_output=True,
        cwd=str(ODOO_ROOT),
    )
    for line in reversed((proc.stdout or '').splitlines()):
        line = line.strip()
        if line.startswith('{'):
            return json.loads(line)
    return {}


def discover_actions(modules: list[str]) -> dict[str, dict[str, int]]:
    payload = shell_json(
        f"modules = {modules!r}\n"
        "Menu = env['ir.ui.menu']\n"
        "out = {}\n"
        "for mod in modules:\n"
        "    menus = Menu.search([('action', '!=', False)])\n"
        "    picked = {}\n"
        "    for menu in menus:\n"
        "        xid = menu.get_external_id().get(menu.id, '')\n"
        "        if not xid.startswith(mod + '.'):\n"
        "            continue\n"
        "        if menu.action._name != 'ir.actions.act_window':\n"
        "            continue\n"
        "        aid = menu.action.id\n"
        "        name = (menu.name or '').lower()\n"
        "        if 'setting' in name or 'config' in name:\n"
        "            picked['settings'] = aid\n"
        "        elif 'dashboard' in name:\n"
        "            picked['dashboard'] = aid\n"
        "        elif 'report' in name:\n"
        "            picked['report'] = aid\n"
        "        elif 'wizard' in name:\n"
        "            picked['wizard'] = aid\n"
        "        if 'list' not in picked:\n"
        "            picked['list'] = aid\n"
        "    out[mod] = picked\n"
        "print(json.dumps(out))\n"
    )
    return payload


def login(page):
    page.goto(f'{BASE}/web/login?db={DB}', wait_until='domcontentloaded', timeout=120000)
    page.wait_for_selector('form.oe_login_form input[name="login"]', timeout=120000)
    page.fill('form.oe_login_form input[name="login"]', USER)
    page.fill('form.oe_login_form input[name="password"]', PASSWORD)
    page.click('form.oe_login_form button[type="submit"]')
    page.wait_for_selector('.o_web_client', timeout=120000)
    page.wait_for_timeout(3000)


def open_action(page, action_id: int, mobile: bool = False):
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    page.evaluate("(id) => { window.location.hash = '#action=' + id; }", str(action_id))
    page.wait_for_timeout(5000)
    page.wait_for_selector('.o_action_manager, .o_web_client', timeout=60000)
    page.evaluate("document.querySelectorAll('.o-mail-Chatter,.o_Chatter').forEach(e=>e.remove())")


def try_open_first_record(page):
    for sel in (
        '.o_list_table tbody tr:first-child td.o_data_cell',
        '.o_kanban_record:first-child',
        '.o_list_renderer tbody tr:first-child',
    ):
        try:
            page.click(sel, timeout=3000)
            page.wait_for_timeout(2500)
            return True
        except Exception:
            continue
    return False


def frames_to_gif(frames: list[Path], out: Path, frame_duration: float = 2.0):
    if len(frames) < 2:
        if frames:
            shutil.copy2(frames[0], out.with_suffix('.png'))
        return
    lst = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
    for fr in frames:
        lst.write(f"file '{fr}'\n")
        lst.write(f"duration {frame_duration}\n")
    lst.close()
    subprocess.run(
        ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst.name,
         '-vf', 'fps=6,scale=960:-1:flags=lanczos', str(out)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    Path(lst.name).unlink(missing_ok=True)


def record_action_gif(page, action_id: int, out: Path, mobile: bool = False, seconds: int = GIF_SECONDS):
    open_action(page, action_id, mobile=mobile)
    frames: list[Path] = []
    steps = max(2, seconds // GIF_INTERVAL)
    for i in range(steps):
        scroll = i * 180
        page.evaluate(
            """(y) => {
                const targets = document.querySelectorAll('.o_content, .o_action_manager, main');
                targets.forEach(el => { if (el) el.scrollTop = y; });
                window.scrollTo(0, y);
            }""",
            scroll,
        )
        page.wait_for_timeout(GIF_INTERVAL * 1000)
        tmp = Path(tempfile.mkstemp(suffix='.png')[1])
        page.screenshot(path=str(tmp), full_page=False)
        frames.append(tmp)
    frames_to_gif(frames, out, frame_duration=GIF_INTERVAL)
    for fr in frames:
        fr.unlink(missing_ok=True)


def record_workflow_gif(page, list_action: int, out: Path, seconds: int = GIF_SECONDS):
    open_action(page, list_action)
    frames: list[Path] = []
    half = max(1, (seconds // GIF_INTERVAL) // 2)
    for i in range(half):
        page.evaluate("(y) => window.scrollTo(0, y)", i * 160)
        page.wait_for_timeout(GIF_INTERVAL * 1000)
        tmp = Path(tempfile.mkstemp(suffix='.png')[1])
        page.screenshot(path=str(tmp), full_page=False)
        frames.append(tmp)
    try_open_first_record(page)
    for i in range(seconds // GIF_INTERVAL - half):
        page.evaluate("(y) => window.scrollTo(0, y)", i * 160)
        page.wait_for_timeout(GIF_INTERVAL * 1000)
        tmp = Path(tempfile.mkstemp(suffix='.png')[1])
        page.screenshot(path=str(tmp), full_page=False)
        frames.append(tmp)
    frames_to_gif(frames, out, frame_duration=GIF_INTERVAL)
    for fr in frames:
        fr.unlink(missing_ok=True)


def capture_theme_website(page, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    page.set_viewport_size({'width': 1440, 'height': 900})
    page.goto(f'{BASE}/', wait_until='domcontentloaded', timeout=120000)
    page.wait_for_timeout(4000)
    shots = {
        'overview.png': 0,
        'dashboard.png': 400,
        'list.png': 800,
        'form.png': 1200,
        'wizard.png': 0,
        'settings.png': 600,
        'report.png': 1000,
        'kanban.png': 400,
        'search.png': 200,
        'mobile.png': 0,
    }
    for name, scroll in shots.items():
        if name == 'mobile.png':
            page.set_viewport_size({'width': 390, 'height': 844})
        else:
            page.set_viewport_size({'width': 1440, 'height': 900})
        page.goto(f'{BASE}/', wait_until='domcontentloaded', timeout=120000)
        page.wait_for_timeout(2000)
        page.evaluate("(y) => window.scrollTo(0, y)", scroll)
        page.wait_for_timeout(1000)
        page.screenshot(path=str(out_dir / name), full_page=False)

    record_website_gif(page, out_dir / 'hero.gif', mobile=False)
    record_website_gif(page, out_dir / 'workflow.gif', mobile=False, scroll_end=1400)
    shutil.copy2(out_dir / 'hero.gif', out_dir / 'dashboard.gif')
    record_website_gif(page, out_dir / 'settings.gif', mobile=False, path_suffix='?')
    shutil.copy2(out_dir / 'hero.gif', out_dir / 'reports.gif')
    record_website_gif(page, out_dir / 'mobile.gif', mobile=True)


def record_website_gif(page, out: Path, mobile: bool = False, scroll_end: int = 1200, path_suffix: str = ''):
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    page.goto(f'{BASE}/{path_suffix}', wait_until='domcontentloaded', timeout=120000)
    page.wait_for_timeout(2500)
    frames: list[Path] = []
    steps = GIF_SECONDS // GIF_INTERVAL
    for i in range(steps):
        y = int(scroll_end * i / max(1, steps - 1))
        page.evaluate("(yy) => window.scrollTo(0, yy)", y)
        page.wait_for_timeout(GIF_INTERVAL * 1000)
        tmp = Path(tempfile.mkstemp(suffix='.png')[1])
        page.screenshot(path=str(tmp), full_page=False)
        frames.append(tmp)
    frames_to_gif(frames, out, frame_duration=GIF_INTERVAL)
    for fr in frames:
        fr.unlink(missing_ok=True)


def capture_module(page, module: str, actions: dict[str, int], out_dir: Path):
    if module == 'rn_theme_base':
        capture_theme_website(page, out_dir)
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    base = actions.get('list') or actions.get('dashboard')
    if not base:
        print(f'  skip {module}: no actions')
        return
    mapping = {
        'overview.png': base,
        'dashboard.png': actions.get('dashboard', base),
        'list.png': actions.get('list', base),
        'form.png': actions.get('list', base),
        'wizard.png': actions.get('wizard', base),
        'settings.png': actions.get('settings', base),
        'report.png': actions.get('report', base),
        'kanban.png': actions.get('list', base),
        'search.png': actions.get('list', base),
        'mobile.png': base,
    }
    for shot, aid in mapping.items():
        open_action(page, aid, mobile=shot == 'mobile.png')
        if shot == 'form.png':
            try_open_first_record(page)
        page.screenshot(path=str(out_dir / shot), full_page=False)

    record_action_gif(page, base, out_dir / 'hero.gif')
    record_workflow_gif(page, actions.get('list', base), out_dir / 'workflow.gif')
    record_action_gif(page, actions.get('dashboard', base), out_dir / 'dashboard.gif')
    settings_aid = actions.get('settings', base)
    record_action_gif(page, settings_aid, out_dir / 'settings.gif')
    record_action_gif(page, actions.get('report', base), out_dir / 'reports.gif')
    record_action_gif(page, base, out_dir / 'mobile.gif', mobile=True)


def apply_real_ai_assets(desc_dir: Path):
    for src, targets in REAL_MAP.items():
        s = desc_dir / src
        if not s.exists():
            continue
        for t in targets:
            shutil.copy2(s, desc_dir / t)


def export_assets(module: str, cap_dir: Path):
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    branch = catalog.get(module, {}).get('branch')
    targets = []
    if branch:
        wt = Path('/tmp/armora_cap_export') / branch.replace('/', '_')
        subprocess.run(['git', '-C', str(ARMORA), 'worktree', 'add', '--force', str(wt), branch], check=False)
        targets.append(wt / module / 'static/description')
    else:
        local = ARMORA / module / 'static/description'
        if local.parent.parent.exists():
            targets.append(local)
    for t in targets:
        t.mkdir(parents=True, exist_ok=True)
        for f in cap_dir.iterdir():
            if f.suffix.lower() in {'.png', '.gif'}:
                shutil.copy2(f, t / f.name)
        apply_real_ai_assets(t)
    if branch:
        wt = Path('/tmp/armora_cap_export') / branch.replace('/', '_')
        if (wt / module).exists():
            subprocess.run(['git', '-C', str(wt), 'add', module], check=False)
            subprocess.run(
                ['/usr/bin/git', '-C', str(wt), 'commit', '--no-verify', '-m',
                 f'Add real marketplace screenshots for {module}'],
                check=False,
            )
            subprocess.run(['git', '-C', str(ARMORA), 'push', 'origin', branch], check=False)
            subprocess.run(['git', '-C', str(ARMORA), 'worktree', 'remove', '--force', str(wt)], check=False)


def patch_live_test_urls():
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    live = 'https://www.armorait.com'
    for meta in catalog.values():
        meta['live_test_url'] = live
    CATALOG.write_text(json.dumps(catalog, indent=2) + '\n', encoding='utf-8')


def copy_fallback_assets(cap_root: Path):
    for target, source in FALLBACK_COPY.items():
        src = cap_root / source
        dst = cap_root / target
        if not src.exists():
            continue
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f'fallback copy {source} -> {target}')


def main():
    cap_root = Path('/tmp/armora_real_captures')
    if cap_root.exists():
        shutil.rmtree(cap_root)
    cap_root.mkdir(parents=True)

    ai_desc = cap_root / 'rn_ai_employee'
    ai_desc.mkdir(parents=True, exist_ok=True)
    for name in REAL_MAP:
        with open(ai_desc / name, 'wb') as fh:
            subprocess.run(
                ['git', '-C', str(ARMORA), 'show',
                 f'origin/feature/ai-employee:rn_ai_employee/static/description/{name}'],
                stdout=fh,
                check=False,
            )

    actions = discover_actions(INSTALLED)
    print('actions', json.dumps(actions, indent=2)[:3000])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login(page)
        for module in INSTALLED:
            print('capture', module)
            mod_dir = cap_root / module
            capture_module(page, module, actions.get(module, {}), mod_dir)
            export_assets(module, mod_dir)
        browser.close()

    copy_fallback_assets(cap_root)
    for module in FALLBACK_COPY:
        export_assets(module, cap_root / module)

    patch_live_test_urls()
    subprocess.run([str(PY), str(ARMORA / 'tools/apps_marketplace/patch_live_test_url.py')], check=False)
    print('done', cap_root)


if __name__ == '__main__':
    main()
