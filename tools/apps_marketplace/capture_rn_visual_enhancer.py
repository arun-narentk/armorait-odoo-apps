#!/usr/bin/env python3
"""Capture live Visual Enhancer screenshots and GIFs for Apps Store assets."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_visual_enhancer'
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
Rule = env['rn.color.rule']
Status = env['rn.visual.status']
SaleOrder = env['sale.order']
Product = env['product.product'].search([('sale_ok', '=', True)], limit=1)
if not Product:
    Product = env['product.product'].create({
        'name': 'Visual Enhancer Demo Product',
        'type': 'consu',
        'list_price': 10.0,
        'sale_ok': True,
    })

partner = Partner.search([('name', '=', 'VISUAL Capture Customer')], limit=1)
if not partner:
    partner = Partner.create({
        'name': 'VISUAL Capture Customer',
        'email': 'visual.capture@armorait.com',
    })

rule = Rule.search([('name', '=', 'VISUAL Live Capture Rule')], limit=1)
if not rule:
    rule = Rule.with_context(rn_skip_color_recompute=True).create({
        'name': 'VISUAL Live Capture Rule',
        'model_id': env.ref('sale.model_sale_order').id,
        'domain': "[('partner_id.name', 'ilike', 'VISUAL%')]",
        'color': 'purple',
        'priority': 150,
        'icon': 'star',
        'emoji': '⭐',
        'label': 'VIP',
    })

status = Status.search([
    ('model_name', '=', 'sale.order'),
    ('field_name', '=', 'state'),
    ('field_value', '=', 'draft'),
], limit=1)
if status:
    status.write({'emoji': '📝', 'label': 'Draft'})

draft = SaleOrder.search([
    ('partner_id', '=', partner.id),
    ('state', '=', 'draft'),
], limit=1)
if not draft:
    draft = SaleOrder.with_context(rn_skip_color_refresh=True).create({
        'partner_id': partner.id,
        'order_line': [(0, 0, {'product_id': Product.id, 'product_uom_qty': 1})],
    })

confirmed = SaleOrder.search([
    ('partner_id', '=', partner.id),
    ('state', '=', 'sale'),
], limit=1)
if not confirmed:
    confirmed = SaleOrder.with_context(rn_skip_color_refresh=True).create({
        'partner_id': partner.id,
        'order_line': [(0, 0, {'product_id': Product.id, 'product_uom_qty': 2})],
    })
    confirmed.with_context(rn_skip_color_refresh=True).action_confirm()

for order in draft | confirmed:
    order._rn_refresh_color_tags()

def action_id(xmlid):
    rec = env.ref(xmlid, raise_if_not_found=False)
    return rec.id if rec else False

out = {
    'rule_id': rule.id,
    'draft_order_id': draft.id,
    'confirmed_order_id': confirmed.id,
    'rules_action_id': action_id('rn_visual_enhancer.action_rn_color_rule'),
    'status_action_id': action_id('rn_visual_enhancer.action_rn_visual_status'),
    'sale_action_id': action_id('sale.action_orders'),
    'invoice_action_id': action_id('account.action_move_out_invoice_type'),
    'crm_action_id': action_id('crm.crm_lead_opportunities'),
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


def capture_assets(meta: dict) -> None:
    shots_dir = MOD_DIR / 'marketplace' / 'screenshots'
    gifs_dir = MOD_DIR / 'marketplace' / 'gifs'
    desc_dir = MOD_DIR / 'static' / 'description'
    for d in (shots_dir, gifs_dir, desc_dir):
        d.mkdir(parents=True, exist_ok=True)

    rules_aid = meta.get('rules_action_id')
    status_aid = meta.get('status_action_id')
    sale_aid = meta.get('sale_action_id')
    invoice_aid = meta.get('invoice_action_id')
    crm_aid = meta.get('crm_action_id')
    rule_id = meta.get('rule_id')
    draft_id = meta.get('draft_order_id')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login(page)

        if status_aid:
            open_action(page, status_aid)
            page.screenshot(path=str(shots_dir / 'settings.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'wizard.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'settings.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        if rules_aid:
            open_action(page, rules_aid)
            page.screenshot(path=str(shots_dir / 'list.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'overview.png'), full_page=False)
            if rule_id:
                open_record_form(page, 'rn.color.rule', rule_id)
                page.screenshot(path=str(shots_dir / 'form.png'), full_page=False)
                page.screenshot(path=str(shots_dir / 'designer.png'), full_page=False)

        if sale_aid:
            open_action(page, sale_aid)
            page.screenshot(path=str(shots_dir / 'dashboard.png'), full_page=False)
            page.screenshot(path=str(shots_dir / 'workflow.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'dashboard.gif', steps=GIF_SECONDS // GIF_INTERVAL)
            if draft_id:
                open_record_form(page, 'sale.order', draft_id)
                page.screenshot(path=str(shots_dir / 'kanban.png'), full_page=False)

        if invoice_aid:
            open_action(page, invoice_aid)
            page.screenshot(path=str(shots_dir / 'report.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'reports.gif', steps=GIF_SECONDS // GIF_INTERVAL)

        if crm_aid:
            open_action(page, crm_aid)
            page.screenshot(path=str(shots_dir / 'search.png'), full_page=False)

        if sale_aid:
            open_action(page, sale_aid, mobile=True)
            page.screenshot(path=str(shots_dir / 'mobile.png'), full_page=False)
            record_scroll_gif(page, gifs_dir / 'mobile.gif', steps=6)

        hero_actions = [aid for aid in (status_aid, rules_aid, sale_aid, invoice_aid) if aid]
        if hero_actions:
            record_action_sequence_gif(page, hero_actions, gifs_dir / 'hero.gif')
        if status_aid and sale_aid:
            record_action_sequence_gif(page, [status_aid, sale_aid], gifs_dir / 'workflow.gif')

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
    if not meta.get('rules_action_id'):
        raise SystemExit('Visual Enhancer actions missing. Install rn_visual_enhancer first.')
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
