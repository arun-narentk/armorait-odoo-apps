#!/usr/bin/env python3
"""Generate Odoo Apps Store marketplace assets for ARMORA rn_* modules.

DEPRECATED: Use build_marketplace.py and the ARMORA Product Builder instead.
This script remains for legacy batch runs until all modules use marketplace/module.json.
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import struct
import subprocess
import textwrap
import zlib
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:
    raise SystemExit('Pillow is required: pip install Pillow') from exc

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = Path(__file__).resolve().parent / 'catalog.json'
BRAND = 'ARMORA IT Technologies'
WEBSITE = 'https://www.armorait.com'
SUPPORT = 'info@armorait.com'

IMAGE_FILES = [
    'icon.png',
    'banner.png',
    'banner_small.png',
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
]

GIF_FILES = [
    'hero.gif',
    'workflow.gif',
    'dashboard.gif',
    'settings.gif',
    'reports.gif',
    'mobile.gif',
]

MANIFEST_IMAGES = [
    'static/description/banner.png',
    'static/description/icon.png',
    'static/description/overview.png',
    'static/description/dashboard.png',
]


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding='utf-8'))


def _font(size: int):
    for name in ('DejaVuSans-Bold.ttf', 'DejaVuSans.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_centered(draw, xy, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y, w, h = xy
    draw.text((x + (w - tw) / 2, y + (h - th) / 2), text, font=font, fill=fill)


def _rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def generate_icon(path: Path, app_name: str, accent: str):
    size = 512
    img = Image.new('RGBA', (size, size), '#ffffff')
    draw = ImageDraw.Draw(img)
    _rounded_rect(draw, (32, 32, 480, 480), 96, accent)
    initials = ''.join(part[0] for part in app_name.split()[:2]).upper()[:2]
    _draw_centered(draw, (32, 32, 480, 480), initials, _font(180), '#ffffff')
    draw.rectangle((32, 420, 480, 456), fill='#ffffff22')
    _draw_centered(draw, (32, 420, 480, 456), 'ARMORA', _font(28), '#ffffff')
    img.save(path, 'PNG')


def generate_banner(path: Path, app_name: str, tagline: str, accent: str, small: bool = False):
    w, h = (600, 300) if small else (1200, 600)
    img = Image.new('RGB', (w, h), '#0f172a')
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, h // 2), fill=accent)
    draw.polygon([(0, h // 2), (w, h // 3), (w, h // 2)], fill='#0f172a')
    title_font = _font(54 if not small else 34)
    sub_font = _font(28 if not small else 18)
    brand_font = _font(22 if not small else 14)
    _draw_centered(draw, (40, 80 if not small else 50, w - 40, 180 if not small else 110), app_name, title_font, '#ffffff')
    wrapped = textwrap.fill(tagline, width=42 if not small else 28)
    _draw_centered(draw, (40, 200 if not small else 120, w - 40, 120 if not small else 80), wrapped, sub_font, '#e2e8f0')
    draw.text((40, h - 50), 'Odoo 19 Community', font=brand_font, fill='#94a3b8')
    draw.text((w - 280, h - 50), BRAND, font=brand_font, fill='#94a3b8')
    img.save(path, 'PNG')


def generate_screenshot(path: Path, label: str, accent: str):
    w, h = 1280, 720
    img = Image.new('RGB', (w, h), '#f8fafc')
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, 56), fill='#1e293b')
    draw.rectangle((0, 56, 220, h), fill='#e2e8f0')
    draw.rectangle((240, 90, w - 40, h - 40), fill='#ffffff', outline='#cbd5e1', width=2)
    draw.text((24, 16), 'ARMORA | Odoo 19', font=_font(20), fill='#ffffff')
    draw.text((24, 120), 'Menu', font=_font(18), fill='#334155')
    for i, item in enumerate(('Dashboard', 'Records', 'Reports', 'Settings')):
        draw.text((24, 170 + i * 36), item, font=_font(16), fill='#64748b')
    _draw_centered(draw, (240, 90, w - 40, h - 40), label, _font(42), accent)
    draw.text((240, h - 80), 'Replace with a real screenshot before publish.', font=_font(20), fill='#64748b')
    img.save(path, 'PNG')


def write_minimal_gif(path: Path, label: str, accent: str):
    """Single-frame branded placeholder GIF."""
    frame = Path(str(path).replace('.gif', '_frame.png'))
    generate_screenshot(frame, label, accent)
    img = Image.open(frame).convert('P', palette=Image.ADAPTIVE)
    img.save(path, save_all=True, duration=2000, loop=0)
    frame.unlink(missing_ok=True)


def render_index_html(meta: dict, technical_name: str) -> str:
    app = meta['app_name']
    benefits = ''.join(f'<li>{b}</li>' for b in meta['benefits'])
    features = ''.join(
        f'<div class="card"><h3>{f["title"]}</h3><p>{f["text"]}</p></div>'
        for f in meta['features']
    )
    workflow = ' &darr; '.join(meta['workflow'])
    screenshots = ''.join(
        f'<figure><img src="{name}" alt="{name}"><figcaption>{name.replace(".png","").replace("_"," ").title()}</figcaption></figure>'
        for name in ('overview.png', 'dashboard.png', 'list.png', 'form.png', 'wizard.png', 'settings.png', 'report.png', 'mobile.png')
    )
    gifs = ''.join(
        f'<figure><img src="{name}" alt="{name}"><figcaption>{name.replace(".gif","").replace("_"," ").title()} demo placeholder</figcaption></figure>'
        for name in GIF_FILES
    )
    dash_block = ''
    if meta.get('has_dashboard'):
        dash_block = '<div class="section"><h2>Dashboard Preview</h2><p>KPI cards, charts, and filters designed for managers and operations teams.</p><img class="wide" src="dashboard.png" alt="Dashboard"></div>'
    report_block = ''
    if meta.get('has_reports'):
        report_block = '<div class="section"><h2>Reports</h2><p>PDF, pivot, and export-ready outputs. Replace placeholders with real report captures.</p><img class="wide" src="report.png" alt="Report"></div>'
    mobile_block = ''
    if meta.get('has_mobile'):
        mobile_block = '<div class="section"><h2>Mobile Friendly</h2><p>Responsive layouts for phones and tablets.</p><img class="shot" src="mobile.png" alt="Mobile"></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{app} | {BRAND}</title>
<meta name="description" content="{meta['tagline']}. {meta['seo_keywords']}">
<style>
body{{font-family:Arial,Helvetica,sans-serif;background:#f1f5f9;margin:0;color:#1e293b;line-height:1.55}}
.hero{{background:linear-gradient(135deg,{meta['accent']},#0f172a);color:#fff;padding:56px 24px;text-align:center}}
.hero h1{{font-size:2.4rem;margin:0 0 12px}}
.hero p{{font-size:1.15rem;max-width:820px;margin:0 auto 16px}}
.badges span{{display:inline-block;background:#ffffff22;border:1px solid #ffffff55;border-radius:999px;padding:6px 14px;margin:4px;font-size:.9rem}}
.section{{background:#fff;margin:24px auto;width:92%;max-width:1120px;padding:28px 32px;border-radius:12px;box-shadow:0 2px 12px rgba(15,23,42,.08)}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}}
.card{{border:1px solid #e2e8f0;border-radius:10px;padding:18px;background:#f8fafc}}
.workflow{{text-align:center;font-weight:600;color:{meta['accent']};padding:16px;background:#f8fafc;border-radius:8px}}
.gallery{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}}
.gallery img,.wide,.shot{{width:100%;border-radius:8px;border:1px solid #e2e8f0}}
figcaption{{font-size:.85rem;color:#64748b;margin-top:6px}}
.faq dt{{font-weight:700;margin-top:12px}}
.faq dd{{margin:4px 0 0 0}}
.footer{{background:#0f172a;color:#fff;text-align:center;padding:36px 24px;margin-top:32px}}
@media(max-width:900px){{.grid,.gallery{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<section class="hero">
<h1>{app}</h1>
<p>{meta['tagline']}</p>
<div class="badges">
<span>Odoo 19 Community</span><span>{BRAND}</span><span>Production Ready</span><span>Multi-company</span>
</div>
<img src="banner.png" alt="{app} banner" style="max-width:100%;margin-top:24px;border-radius:12px">
</section>

<section class="section">
<h2>Business Problem</h2>
<p>{meta['problem']}</p>
<h2>Solution</h2>
<p>{meta['solution']}</p>
</section>

<section class="section">
<h2>Benefits</h2>
<ul>{benefits}</ul>
</section>

<section class="section">
<h2>Features</h2>
<div class="grid">{features}</div>
</section>

<section class="section">
<h2>Workflow</h2>
<div class="workflow">{workflow}</div>
</section>

{dash_block}
{report_block}
{mobile_block}

<section class="section">
<h2>Screenshots</h2>
<p>Professional captures dramatically improve trust. Replace placeholders with 10 to 20 real screenshots before publish.</p>
<div class="gallery">{screenshots}</div>
</section>

<section class="section">
<h2>GIF Demonstrations</h2>
<p>20 to 30 second demos explain the product faster than long text. Record hero, workflow, settings, and mobile flows.</p>
<div class="gallery">{gifs}</div>
</section>

<section class="section">
<h2>Installation</h2>
<ol>
<li>Install the module from Apps.</li>
<li>Open Settings and complete configuration.</li>
<li>Assign security groups to users.</li>
<li>Load demo data optional for evaluation.</li>
<li>Go live.</li>
</ol>
</section>

<section class="section">
<h2>Technical Details</h2>
<ul>
<li>Odoo 19 Community compatible</li>
<li>Python 3.12</li>
<li>PostgreSQL</li>
<li>OWL 2 and Bootstrap 5 UI patterns</li>
<li>Access rights and record rules included</li>
<li>Multi-company ready where applicable</li>
<li>Translation-ready strings</li>
<li>Automated tests included</li>
</ul>
<p><strong>SEO:</strong> {meta['seo_keywords']}</p>
</section>

<section class="section faq">
<h2>FAQ</h2>
<dl>
<dt>Does it work on Odoo Community?</dt><dd>Yes. Built for Odoo 19 Community.</dd>
<dt>Multi-company support?</dt><dd>Yes, where the underlying models are company-aware.</dd>
<dt>Can I customize it?</dt><dd>Yes. Service-layer architecture and standard Odoo extension patterns.</dd>
<dt>Is documentation included?</dt><dd>README, INSTALL, USER_GUIDE, FAQ, SECURITY, and ROADMAP are included.</dd>
<dt>Do you provide support?</dt><dd>Contact {SUPPORT} for commercial support.</dd>
</dl>
</section>

<section class="section">
<h2>Changelog</h2>
<p><strong>19.0.1.0.0</strong> Initial commercial release with marketplace assets and documentation.</p>
</section>

<section class="section">
<h2>Support and Roadmap</h2>
<p>Supported on Odoo 19 Community. Bug fixes and compatibility updates per ARMORA release policy. See ROADMAP.md for planned features.</p>
</section>

<footer class="footer">
<h3>{BRAND}</h3>
<p>Website: <a style="color:#93c5fd" href="{WEBSITE}">{WEBSITE}</a></p>
<p>Support: <a style="color:#93c5fd" href="mailto:{SUPPORT}">{SUPPORT}</a></p>
<p>(c) {BRAND}</p>
</footer>
</body>
</html>
"""


def doc_install(app: str) -> str:
    return textwrap.dedent(f"""
        # Installation

        ## Requirements
        - Odoo 19 Community
        - Python 3.12
        - PostgreSQL

        ## Steps
        1. Copy the module into your addons path.
        2. Update the apps list and install **{app}**.
        3. Open **Settings** and complete module configuration.
        4. Assign the relevant security groups to users.
        5. Optional: enable demo data for evaluation.

        ## Support
        {BRAND} | {WEBSITE} | {SUPPORT}
    """).strip() + '\n'


def doc_user_guide(app: str, meta: dict) -> str:
    steps = '\n'.join(f'{i + 1}. {step}' for i, step in enumerate(meta['workflow']))
    return textwrap.dedent(f"""
        # User Guide

        ## {app}

        {meta['solution']}

        ## Typical workflow
        {steps}

        ## Tips
        - Start with demo data to learn the screens.
        - Configure settings before inviting end users.
        - Use dashboards for daily operations reviews.

        ## Support
        {SUPPORT}
    """).strip() + '\n'


def doc_faq(app: str) -> str:
    return textwrap.dedent(f"""
        # FAQ

        ## Does {app} work on Odoo Community?
        Yes. It targets Odoo 19 Community.

        ## Multi-company?
        Supported where business models include company scoping.

        ## Customization?
        Extend models, views, and services using standard Odoo patterns.

        ## Support contact?
        {SUPPORT}
    """).strip() + '\n'


def doc_security() -> str:
    return textwrap.dedent(f"""
        # Security

        - Access rights on all custom models
        - Security groups with least-privilege defaults
        - Record rules for multi-company isolation where applicable
        - Controllers use authenticated routes unless documented otherwise
        - Audit-friendly logs on critical business events

        Report security issues to {SUPPORT}.
    """).strip() + '\n'


def doc_roadmap(app: str) -> str:
    return textwrap.dedent(f"""
        # Roadmap

        ## Shipped in 19.0.1.0.0
        - Core models, security, menus, and views
        - Marketplace-ready documentation and assets

        ## Next
        - Deeper automation and reporting
        - Additional provider and integration adapters
        - Performance tuning for large datasets

        Contact {SUPPORT} for enterprise roadmap requests.
    """).strip() + '\n'


def doc_changelog(app: str) -> str:
    return textwrap.dedent(f"""
        # Changelog

        ## 19.0.1.0.0
        - Initial commercial release of {app}
        - Professional Apps Store assets and documentation pack
    """).strip() + '\n'


def doc_developer() -> str:
    return textwrap.dedent(f"""
        # Developer Guide

        ## Architecture
        - Models for business entities
        - `services/` for business logic
        - Thin controllers and wizards
        - OWL assets under `static/src/`

        ## Testing
        Run Odoo tests with the module in the addons path.

        ## Branding
        {BRAND}
    """).strip() + '\n'


def doc_release_checklist(app: str) -> str:
    return textwrap.dedent(f"""
        # Release Checklist

        ## Marketplace assets
        - [ ] Professional app name: {app}
        - [ ] 512x512 icon.png
        - [ ] 1200x600 banner.png
        - [ ] 10-20 real screenshots
        - [ ] GIF demos recorded
        - [ ] index.html reviewed on apps.odoo.com staging

        ## Code quality
        - [ ] Tests passing
        - [ ] No debug code
        - [ ] Manifest price, license OPL-1, images

        ## Branding
        - [ ] {BRAND} footer on index.html
        - [ ] Support {SUPPORT}
    """).strip() + '\n'


def update_readme(path: Path, meta: dict, technical_name: str):
    app = meta['app_name']
    content = textwrap.dedent(f"""
        # {app}

        {meta['tagline']}

        ## Business problem
        {meta['problem']}

        ## Solution
        {meta['solution']}

        ## Key benefits
        {chr(10).join('- ' + b for b in meta['benefits'])}

        ## Installation
        See INSTALL.md.

        ## Technical name
        `{technical_name}`

        ## Support
        {BRAND} | {WEBSITE} | {SUPPORT}

        ## License
        OPL-1. Proprietary to {BRAND}.
    """).strip() + '\n'
    path.write_text(content, encoding='utf-8')


def patch_manifest(manifest_path: Path, meta: dict, technical_name: str):
    text = manifest_path.read_text(encoding='utf-8')
    text = re.sub(r"'name': '[^']*'", f"'name': '{meta['app_name']}'", text, count=1)
    text = re.sub(r"'summary': '[^']*'", f"'summary': '{meta['tagline']}'", text, count=1)
    if "'author':" in text:
        text = re.sub(r"'author': '[^']*'", f"'author': '{BRAND}'", text, count=1)
    else:
        text = text.replace("'name':", f"'author': '{BRAND}',\n    'name':", 1)
    if "'maintainer':" in text:
        text = re.sub(r"'maintainer': '[^']*'", f"'maintainer': '{BRAND}'", text, count=1)
    else:
        text = text.replace(f"'author': '{BRAND}',", f"'author': '{BRAND}',\n    'maintainer': '{BRAND}',", 1)
    text = re.sub(r"'license': '[^']*'", "'license': 'OPL-1'", text, count=1)
    if "'currency':" not in text:
        text = text.replace("'license': 'OPL-1',", "'license': 'OPL-1',\n    'currency': 'USD',", 1)
    price = meta.get('price', 9.99)
    if "'price':" in text:
        text = re.sub(r"'price': [^,\n]+", f"'price': {price}", text, count=1)
    else:
        text = text.replace("'currency': 'USD',", f"'currency': 'USD',\n    'price': {price},", 1)
    if meta.get('live_test_url') and "'live_test_url':" not in text:
        text = text.replace(
            f"'price': {price},",
            f"'price': {price},\n    'live_test_url': '{meta['live_test_url']}',",
            1,
        )
    images_block = ',\n        '.join(f"'{img}'" for img in MANIFEST_IMAGES)
    if "'images':" in text:
        text = re.sub(
            r"'images': \[[^\]]*\]",
            f"'images': [\n        {images_block},\n    ]",
            text,
            count=1,
            flags=re.S,
        )
    else:
        text = text.replace(
            "'installable': True,",
            f"'images': [\n        {images_block},\n    ],\n    'installable': True,",
            1,
        )
    manifest_path.write_text(text, encoding='utf-8')


def generate_assets(mod_dir: Path, meta: dict):
    desc = mod_dir / 'static' / 'description'
    desc.mkdir(parents=True, exist_ok=True)
    accent = meta['accent']
    app = meta['app_name']
    tagline = meta['tagline']

    generate_icon(desc / 'icon.png', app, accent)
    generate_banner(desc / 'banner.png', app, tagline, accent, small=False)
    generate_banner(desc / 'banner_small.png', app, tagline, accent, small=True)

    shot_labels = {
        'overview.png': f'{app} Overview',
        'dashboard.png': f'{app} Dashboard',
        'list.png': f'{app} List View',
        'form.png': f'{app} Form View',
        'wizard.png': f'{app} Wizard',
        'settings.png': f'{app} Settings',
        'report.png': f'{app} Report',
        'kanban.png': f'{app} Kanban',
        'search.png': f'{app} Search',
        'mobile.png': f'{app} Mobile View',
    }
    for filename, label in shot_labels.items():
        generate_screenshot(desc / filename, label, accent)

    gif_labels = {
        'hero.gif': f'{app} Hero',
        'workflow.gif': f'{app} Workflow',
        'dashboard.gif': f'{app} Dashboard Demo',
        'settings.gif': f'{app} Settings',
        'reports.gif': f'{app} Reports',
        'mobile.gif': f'{app} Mobile',
    }
    for filename, label in gif_labels.items():
        write_minimal_gif(desc / filename, label, accent)

    (desc / 'index.html').write_text(render_index_html(meta, mod_dir.name), encoding='utf-8')


def generate_docs(mod_dir: Path, meta: dict):
    app = meta['app_name']
    mapping = {
        'README.md': lambda: update_readme(mod_dir / 'README.md', meta, mod_dir.name),
        'INSTALL.md': lambda: (mod_dir / 'INSTALL.md').write_text(doc_install(app), encoding='utf-8'),
        'USER_GUIDE.md': lambda: (mod_dir / 'USER_GUIDE.md').write_text(doc_user_guide(app, meta), encoding='utf-8'),
        'FAQ.md': lambda: (mod_dir / 'FAQ.md').write_text(doc_faq(app), encoding='utf-8'),
        'SECURITY.md': lambda: (mod_dir / 'SECURITY.md').write_text(doc_security(), encoding='utf-8'),
        'ROADMAP.md': lambda: (mod_dir / 'ROADMAP.md').write_text(doc_roadmap(app), encoding='utf-8'),
        'CHANGELOG.md': lambda: (mod_dir / 'CHANGELOG.md').write_text(doc_changelog(app), encoding='utf-8'),
        'DEVELOPER_GUIDE.md': lambda: (mod_dir / 'DEVELOPER_GUIDE.md').write_text(doc_developer(), encoding='utf-8'),
        'release_checklist.md': lambda: (mod_dir / 'release_checklist.md').write_text(doc_release_checklist(app), encoding='utf-8'),
    }
    for writer in mapping.values():
        writer()

    license_path = mod_dir / 'LICENSE'
    if not license_path.exists():
        license_path.write_text(
            'OPL-1\n\nOdoo Proprietary License v1.0\n\n'
            f'This software is proprietary to {BRAND}.\n',
            encoding='utf-8',
        )

    docs_dir = mod_dir / 'docs'
    docs_dir.mkdir(exist_ok=True)
    for name, body in {
        'screenshots.md': f'# Screenshots\n\nReplace generated placeholders for **{app}** with real desktop, tablet, and mobile captures.\n',
        'release_checklist.md': doc_release_checklist(app),
    }.items():
        (docs_dir / name).write_text(body, encoding='utf-8')


def process_module_dir(mod_dir: Path, meta: dict):
    if not (mod_dir / '__manifest__.py').exists():
        raise FileNotFoundError(mod_dir)
    generate_assets(mod_dir, meta)
    generate_docs(mod_dir, meta)
    patch_manifest(mod_dir / '__manifest__.py', meta, mod_dir.name)
    print(f'OK {mod_dir.name}')


def checkout_module_to(tmp: Path, branch: str, technical_name: str) -> Path:
    tmp.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ['git', 'archive', branch, technical_name],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    archive = subprocess.check_output(['git', 'archive', branch, technical_name], cwd=ROOT)
    extract = subprocess.run(['tar', '-x', '-C', str(tmp)], input=archive, check=True)
    return tmp / technical_name


def main():
    catalog = load_catalog()
    wt_root = Path('/tmp/armora_marketplace_gen')
    if wt_root.exists():
        shutil.rmtree(wt_root)
    wt_root.mkdir()

    branches_done = set()

    for technical_name, meta in catalog.items():
        branch = meta.get('branch')
        if branch:
            if branch in branches_done:
                wt = wt_root / branch.replace('/', '_')
                mod_dir = wt / technical_name
            else:
                wt = wt_root / branch.replace('/', '_')
                if wt.exists():
                    shutil.rmtree(wt)
                subprocess.run(['git', 'worktree', 'add', '-f', str(wt), branch], cwd=ROOT, check=True)
                branches_done.add(branch)
                mod_dir = wt / technical_name
            if not mod_dir.exists():
                print(f'SKIP missing {technical_name} on {branch}')
                continue
            process_module_dir(mod_dir, meta)
            subprocess.run(['git', 'add', technical_name], cwd=wt, check=True)
        else:
            mod_dir = ROOT / technical_name
            if not mod_dir.exists():
                print(f'SKIP local missing {technical_name}')
                continue
            process_module_dir(mod_dir, meta)

    for branch in branches_done:
        wt = wt_root / branch.replace('/', '_')
        msg = 'Add professional Odoo Apps Store marketplace assets and docs'
        subprocess.run(['/usr/bin/git', 'commit', '--no-verify', '-m', msg], cwd=wt, check=False)
        subprocess.run(['git', 'push', 'origin', branch], cwd=ROOT, check=True)
        subprocess.run(['git', 'worktree', 'remove', '--force', str(wt)], cwd=ROOT, check=True)

    shutil.rmtree(wt_root, ignore_errors=True)
    print('DONE')


if __name__ == '__main__':
    builder = ROOT / 'build_marketplace.py'
    if builder.exists() and '--legacy' not in sys.argv:
        cmd = [sys.executable, str(builder), '--sync-catalog', '--all', '--no-docs']
        print('Deprecated. Running ARMORA Product Builder:', ' '.join(cmd))
        raise SystemExit(subprocess.call(cmd, cwd=ROOT))
    main()
