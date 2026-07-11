#!/usr/bin/env python3
"""Capture live Odoo screenshots and GIFs for rn_record_timeline Apps Store page."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ODOO_ROOT = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA_ODOO_APPS')
ARMORA = ODOO_ROOT / 'armora'
MODULE = 'rn_record_timeline'
PY = Path('/home/lenovo/bin/packages/PyCharm/Old/Odoo_19_ARMORA/venv310/bin/python')
ODOO_BIN = ODOO_ROOT / 'odoo-bin'
ADDONS_PATH = f'{ODOO_ROOT / "addons"},{ARMORA}'

DB = 'test_rn_timeline_live'
BASE = 'http://127.0.0.1:8070'
USER = 'admin'
PASSWORD = 'admin'
HTTP_PORT = 8070
GIF_SECONDS = 20
GIF_INTERVAL = 2

DB_ARGS = [
    '--db_host=localhost',
    '--db_port=5435',
    '--db_user=ubuntu',
    '--db_password=ubuntu',
]
BASE_ARGS = [f'--addons-path={ADDONS_PATH}', *DB_ARGS]


def shell_json(code: str) -> dict:
    script = f"import json\n{code}\n"
    proc = subprocess.run(
        [str(PY), str(ODOO_BIN), 'shell', '-d', DB, '--no-http', *BASE_ARGS],
        input=script,
        text=True,
        capture_output=True,
        cwd=str(ODOO_ROOT),
    )
    for line in reversed((proc.stdout or '').splitlines()):
        line = line.strip()
        if line.startswith('{'):
            return json.loads(line)
    if proc.stderr:
        print(proc.stderr[-2000:], file=sys.stderr)
    return {}


def db_exists() -> bool:
    proc = subprocess.run(
        ['psql', '-h', 'localhost', '-p', '5435', '-U', 'ubuntu', '-d', 'postgres',
         '-tAc', f"SELECT 1 FROM pg_database WHERE datname='{DB}'"],
        env={'PGPASSWORD': 'ubuntu'},
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() == '1'


def ensure_database():
    if db_exists():
        print(f'Database {DB} already exists, skipping bootstrap')
        return
    proc = subprocess.run(
        [str(PY), str(ODOO_BIN), '-d', DB, *BASE_ARGS,
         '-i', 'base,sale_management,purchase,account,crm,rn_record_timeline',
         '--stop-after-init'],
        cwd=str(ODOO_ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 and 'already exists' not in (proc.stderr or '').lower():
        print(proc.stdout[-3000:])
        print(proc.stderr[-3000:])
        raise SystemExit(f'Database bootstrap failed ({proc.returncode})')


def run_tests():
    proc = subprocess.run(
        [str(PY), str(ODOO_BIN), '-d', DB, *BASE_ARGS,
         '-u', MODULE, '--test-enable', '--test-tags', f'/{MODULE}',
         '--stop-after-init'],
        cwd=str(ODOO_ROOT),
        capture_output=True,
        text=True,
    )
    tail = (proc.stdout or '') + (proc.stderr or '')
    print(tail[-4000:])
    if '0 failed, 0 error' not in tail and 'failed, 0 error' not in tail:
        raise SystemExit(f'Tests failed ({proc.returncode})')


def discover_actions() -> dict[str, int]:
    payload = shell_json(
        "Menu = env['ir.ui.menu']\n"
        "out = {}\n"
        "for xmlid_suffix, key in [\n"
        "    ('menu_rn_timeline_events', 'events'),\n"
        "    ('menu_rn_timeline_templates', 'templates'),\n"
        "    ('menu_rn_timeline_root', 'root'),\n"
        "]:\n"
        "    menu = env.ref(f'rn_record_timeline.{xmlid_suffix}', raise_if_not_found=False)\n"
        "    if menu and menu.action and menu.action._name == 'ir.actions.act_window':\n"
        "        out[key] = menu.action.id\n"
        "Sale = env['sale.order']\n"
        "so = Sale.search([], order='id desc', limit=1)\n"
        "if so:\n"
        "    out['sale_order_id'] = so.id\n"
        "print(json.dumps(out))\n"
    )
    return payload


def start_odoo_server() -> subprocess.Popen:
    return subprocess.Popen(
        [str(PY), str(ODOO_BIN), '-d', DB, *BASE_ARGS,
         '--http-port', str(HTTP_PORT)],
        cwd=str(ODOO_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_odoo(timeout: int = 120):
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f'{BASE}/web/login', timeout=3) as resp:
                if resp.status == 200:
                    return
        except Exception:
            time.sleep(2)
    raise SystemExit('Odoo server did not start in time')


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
         '-vf', 'fps=8,scale=960:-1:flags=lanczos', str(out)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    Path(lst.name).unlink(missing_ok=True)


def login(page):
    page.goto(f'{BASE}/web/login?db={DB}', wait_until='domcontentloaded', timeout=120000)
    page.fill('form.oe_login_form input[name="login"]', USER)
    page.fill('form.oe_login_form input[name="password"]', PASSWORD)
    page.click('form.oe_login_form button[type="submit"]')
    page.wait_for_selector('.o_web_client', timeout=120000)
    page.wait_for_timeout(2500)


def open_sale_order_form(page, sale_order_id: int, mobile: bool = False):
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    page.goto(
        f'{BASE}/web#id={sale_order_id}&model=sale.order&view_type=form',
        wait_until='domcontentloaded',
        timeout=120000,
    )
    page.wait_for_timeout(4000)
    page.wait_for_selector('.o_form_view', timeout=60000)


def click_timeline_tab(page):
    for selector in (
        'a.nav-link:has-text("Timeline")',
        '.nav-link:has-text("Timeline")',
        'button:has-text("Timeline")',
    ):
        try:
            page.click(selector, timeout=4000)
            page.wait_for_timeout(2500)
            return True
        except Exception:
            continue
    return False


def open_action(page, action_id: int, mobile: bool = False):
    if mobile:
        page.set_viewport_size({'width': 390, 'height': 844})
    else:
        page.set_viewport_size({'width': 1440, 'height': 900})
    page.evaluate("(id) => { window.location.hash = '#action=' + id; }", str(action_id))
    page.wait_for_timeout(4500)
    page.wait_for_selector('.o_action_manager, .o_web_client', timeout=60000)


def record_frames(page, out: Path, steps: int = 10, scroll_step: int = 120):
    frames: list[Path] = []
    for i in range(steps):
        page.evaluate(
            """(y) => {
                document.querySelectorAll('.o_content, .o_action_manager, main, .o_form_view')
                    .forEach(el => { if (el) el.scrollTop = y; });
                window.scrollTo(0, y);
            }""",
            i * scroll_step,
        )
        page.wait_for_timeout(GIF_INTERVAL * 1000)
        tmp = Path(tempfile.mkstemp(suffix='.png')[1])
        page.screenshot(path=str(tmp), full_page=False)
        frames.append(tmp)
    frames_to_gif(frames, out, frame_duration=GIF_INTERVAL)
    for fr in frames:
        fr.unlink(missing_ok=True)


def capture_live_assets(out_dir: Path, actions: dict[str, int]):
    out_dir.mkdir(parents=True, exist_ok=True)
    sale_id = actions.get('sale_order_id')
    if not sale_id:
        raise SystemExit('No sale order found for live capture')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login(page)

        # workflow.png: events list menu
        if actions.get('events'):
            open_action(page, actions['events'])
            page.screenshot(path=str(out_dir / 'workflow.png'), full_page=False)

        # dashboard.png: sale order timeline tab
        open_sale_order_form(page, sale_id)
        click_timeline_tab(page)
        page.screenshot(path=str(out_dir / 'dashboard.png'), full_page=False)

        # designer.png: templates menu (manager)
        if actions.get('templates'):
            open_action(page, actions['templates'])
            page.screenshot(path=str(out_dir / 'designer.png'), full_page=False)

        # Extra stills for gallery depth
        open_action(page, actions.get('events', actions.get('templates', 0)))
        page.screenshot(path=str(out_dir / 'list.png'), full_page=False)
        open_sale_order_form(page, sale_id)
        click_timeline_tab(page)
        page.screenshot(path=str(out_dir / 'form.png'), full_page=False)

        # hero.gif: open SO and timeline tab
        open_sale_order_form(page, sale_id)
        frames: list[Path] = []
        tmp = Path(tempfile.mkstemp(suffix='.png')[1])
        page.screenshot(path=str(tmp), full_page=False)
        frames.append(tmp)
        click_timeline_tab(page)
        for i in range(4):
            page.evaluate("(y) => window.scrollTo(0, y)", i * 100)
            page.wait_for_timeout(GIF_INTERVAL * 1000)
            tmp = Path(tempfile.mkstemp(suffix='.png')[1])
            page.screenshot(path=str(tmp), full_page=False)
            frames.append(tmp)
        frames_to_gif(frames, out_dir / 'hero.gif', frame_duration=GIF_INTERVAL)
        for fr in frames:
            fr.unlink(missing_ok=True)

        # workflow.gif: events list then SO timeline
        workflow_frames: list[Path] = []
        if actions.get('events'):
            open_action(page, actions['events'])
            for i in range(4):
                page.evaluate("(y) => window.scrollTo(0, y)", i * 140)
                page.wait_for_timeout(GIF_INTERVAL * 1000)
                tmp = Path(tempfile.mkstemp(suffix='.png')[1])
                page.screenshot(path=str(tmp), full_page=False)
                workflow_frames.append(tmp)
        open_sale_order_form(page, sale_id)
        click_timeline_tab(page)
        for i in range(4):
            page.evaluate("(y) => window.scrollTo(0, y)", i * 100)
            page.wait_for_timeout(GIF_INTERVAL * 1000)
            tmp = Path(tempfile.mkstemp(suffix='.png')[1])
            page.screenshot(path=str(tmp), full_page=False)
            workflow_frames.append(tmp)
        frames_to_gif(workflow_frames, out_dir / 'workflow.gif', frame_duration=GIF_INTERVAL)
        for fr in workflow_frames:
            fr.unlink(missing_ok=True)

        # dashboard.gif: timeline tab scrolling
        open_sale_order_form(page, sale_id)
        click_timeline_tab(page)
        record_frames(page, out_dir / 'dashboard.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        # settings.gif: templates configuration
        if actions.get('templates'):
            open_action(page, actions['templates'])
            record_frames(page, out_dir / 'settings.gif', steps=5, scroll_step=160)

        # reports.gif: timeline tab then events list
        report_frames: list[Path] = []
        open_sale_order_form(page, sale_id)
        click_timeline_tab(page)
        for i in range(3):
            page.evaluate("(y) => window.scrollTo(0, y)", i * 80)
            page.wait_for_timeout(GIF_INTERVAL * 1000)
            tmp = Path(tempfile.mkstemp(suffix='.png')[1])
            page.screenshot(path=str(tmp), full_page=False)
            report_frames.append(tmp)
        if actions.get('events'):
            open_action(page, actions['events'])
            for i in range(3):
                page.evaluate("(y) => window.scrollTo(0, y)", i * 120)
                page.wait_for_timeout(GIF_INTERVAL * 1000)
                tmp = Path(tempfile.mkstemp(suffix='.png')[1])
                page.screenshot(path=str(tmp), full_page=False)
                report_frames.append(tmp)
        frames_to_gif(report_frames, out_dir / 'reports.gif', frame_duration=GIF_INTERVAL)
        for fr in report_frames:
            fr.unlink(missing_ok=True)

        # mobile.gif
        open_sale_order_form(page, sale_id, mobile=True)
        click_timeline_tab(page)
        record_frames(page, out_dir / 'mobile.gif', steps=5, scroll_step=90)

        browser.close()


def sync_to_module(out_dir: Path):
    module_dir = ARMORA / MODULE
    desc = module_dir / 'static' / 'description'
    marketplace = module_dir / 'marketplace'
    for sub in ('screenshots', 'gifs'):
        (marketplace / sub).mkdir(parents=True, exist_ok=True)
    desc.mkdir(parents=True, exist_ok=True)

    png_targets = {
        'workflow.png', 'dashboard.png', 'designer.png',
    }
    gif_targets = {
        'hero.gif', 'workflow.gif', 'dashboard.gif',
        'settings.gif', 'reports.gif', 'mobile.gif',
    }
    for path in out_dir.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() == '.png' and path.name in png_targets:
            shutil.copy2(path, desc / path.name)
            shutil.copy2(path, marketplace / 'screenshots' / path.name)
        elif path.suffix.lower() == '.gif' and path.name in gif_targets:
            shutil.copy2(path, desc / path.name)
            shutil.copy2(path, marketplace / 'gifs' / path.name)


def rebuild_index():
    subprocess.run(
        [str(PY), str(ARMORA / 'build_marketplace.py'), MODULE, '--no-docs'],
        cwd=str(ARMORA),
        check=True,
    )


def seed_demo_data():
    shell_json(
        "partner = env['res.partner'].create({'name': 'Timeline Demo Customer'})\n"
        "product = env['product.product'].create({'name': 'Timeline Demo Product', 'list_price': 100})\n"
        "order = env['sale.order'].create({\n"
        "    'partner_id': partner.id,\n"
        "    'order_line': [(0, 0, {'product_id': product.id, 'product_uom_qty': 2, 'price_unit': 100})],\n"
        "})\n"
        "try:\n"
        "    order.action_confirm()\n"
        "except Exception:\n"
        "    order.write({'state': 'sent'})\n"
        "service = env['rn.timeline.service']\n"
        "service.create_event(order, 'Invoice Posted', event_type='invoice', filter_category='financial')\n"
        "service.create_event(order, 'Payment Registered', event_type='payment', filter_category='financial')\n"
        "service.create_event(order, 'Delivered', event_type='delivery', filter_category='logistics')\n"
        "env.cr.commit()\n"
        "print(json.dumps({'sale_order_id': order.id, 'events': env['rn.timeline.event'].search_count([])}))\n"
    )


def main():
    cap_dir = Path('/tmp/rn_record_timeline_live')
    if cap_dir.exists():
        shutil.rmtree(cap_dir)
    cap_dir.mkdir()

    print('Bootstrapping database...')
    ensure_database()
    print('Running tests...')
    run_tests()

    seed_demo_data()

    server = start_odoo_server()
    try:
        print('Waiting for Odoo HTTP...')
        wait_for_odoo()
        actions = discover_actions()
        print('Actions:', json.dumps(actions, indent=2))
        print('Capturing live assets...')
        capture_live_assets(cap_dir, actions)
    finally:
        server.terminate()
        server.wait(timeout=30)

    sync_to_module(cap_dir)
    rebuild_index()
    print('Live capture complete:', cap_dir)
    print('Updated:', ARMORA / MODULE / 'static/description')


if __name__ == '__main__':
    main()
