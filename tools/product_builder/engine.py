#!/usr/bin/env python3
"""ARMORA Product Builder - generate marketplace assets from module config."""
from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import sys
import textwrap
import zipfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ARMORA_ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK = ARMORA_ROOT / 'marketplace_framework'
BRAND_DIR = FRAMEWORK / 'static' / 'brand'
TOOLS_DIR = ARMORA_ROOT / 'tools'
LEGACY_CATALOG = ARMORA_ROOT / 'tools' / 'apps_marketplace' / 'catalog.json'
ZIP_OUT = ARMORA_ROOT / 'apps_store_zips'

COMPANY_BRAND_FILES = (
    'company_logo.png',
    'company_logo.svg',
    'company_icon.png',
    'favicon.ico',
    'armorait_brand_logo.png',
)

SCREENSHOT_MAP = {
    'overview': 'overview.png',
    'list': 'list.png',
    'form': 'form.png',
    'dashboard': 'dashboard.png',
    'wizard': 'wizard.png',
    'settings': 'settings.png',
    'report': 'report.png',
    'search': 'search.png',
    'kanban': 'kanban.png',
    'mobile': 'mobile.png',
    'workflow': 'workflow.png',
    'designer': 'designer.png',
}

GIF_MAP = {
    'hero': 'hero.gif',
    'workflow': 'workflow.gif',
    'dashboard': 'dashboard.gif',
    'settings': 'settings.gif',
    'reports': 'reports.gif',
    'mobile': 'mobile.gif',
}

SCREENSHOT_LABELS = {
    'overview.png': 'Overview',
    'list.png': 'Rules List',
    'form.png': 'Rule Form',
    'dashboard.png': 'Duplicate Matches',
    'wizard.png': 'Merge Wizard',
    'settings.png': 'Ignored Pairs',
    'report.png': 'Scan Results',
    'search.png': 'Match Review',
    'kanban.png': 'All Matches',
    'mobile.png': 'Mobile View',
    'workflow.png': 'Process Workflow',
    'designer.png': 'Rule Designer',
}

LEGACY_DESCRIPTION_FILES = frozenset({
    'main_screenshot.png',
    'ai_builder.png',
    'execution.png',
    'monitoring.png',
    'screenshot_contact_phone.png',
    'screenshot_invoice_form.png',
    'screenshot_whatsapp_message.png',
    'banner.gif',
    'banner_small.gif',
})

GIF_LABELS = {
    'hero.gif': 'Hero Demo',
    'workflow.gif': 'Workflow',
    'dashboard.gif': 'Dashboard Demo',
    'settings.gif': 'Settings',
    'reports.gif': 'Reports',
    'mobile.gif': 'Mobile',
}

CATEGORY_LABELS = {
    'ai': 'AI and automation',
    'erp': 'ERP and operations',
    'dashboard': 'Analytics and dashboards',
    'productivity': 'Productivity',
    'platform': 'Platform and integration',
    'theme': 'Website and theme',
}

MANIFEST_IMAGES = [
    'static/description/banner.png',
    'static/description/icon.png',
    'static/description/workflow.png',
    'static/description/dashboard.png',
    'static/description/designer.png',
]

SKIP_MODULE_DIRS = frozenset({
    'tools',
    'marketplace_framework',
    'apps_store_zips',
    'armorait2_site',
    'website_armorait',
})

ACCENT_PALETTE = (
    '#2563eb',
    '#16a34a',
    '#7c3aed',
    '#db2777',
    '#ea580c',
    '#0891b2',
    '#4f46e5',
    '#0d9488',
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def load_module_config(mod_dir: Path) -> dict:
    for name in ('module.yaml', 'module.yml', 'module.json'):
        path = mod_dir / 'marketplace' / name
        if path.exists():
            if path.suffix == '.json':
                return load_json(path)
            return load_yaml_simple(path)
    raise FileNotFoundError(f'No marketplace/module.yaml or module.json in {mod_dir.name}')


def load_yaml_simple(path: Path) -> dict:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text(encoding='utf-8'))
    except ImportError:
        pass
    text = path.read_text(encoding='utf-8')
    if text.strip().startswith('{'):
        return json.loads(text)
    raise RuntimeError(
        f'Install PyYAML to read {path.name}, or use marketplace/module.json instead.'
    )


def dump_module_config(mod_dir: Path, data: dict) -> Path:
    mp = mod_dir / 'marketplace'
    mp.mkdir(parents=True, exist_ok=True)
    out = mp / 'module.json'
    out.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return out


def load_catalog() -> dict:
    if LEGACY_CATALOG.exists():
        return load_json(LEGACY_CATALOG)
    return load_json(FRAMEWORK / 'catalog.json')


def save_catalog(catalog: dict) -> None:
    LEGACY_CATALOG.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )


def read_manifest(manifest_path: Path) -> dict:
    text = manifest_path.read_text(encoding='utf-8')
    match = re.search(r'\{[\s\S]*\}', text)
    if not match:
        return {}
    return ast.literal_eval(match.group())


def guess_category_type(technical_name: str, manifest: dict) -> str:
    name = technical_name.lower()
    category = str(manifest.get('category', '')).lower()
    if name.startswith('rn_ai_') or 'artificial intelligence' in category:
        return 'ai'
    if 'dashboard' in name or 'dashboard' in category or 'reporting' in category:
        return 'dashboard'
    if 'whatsapp' in name or 'messaging' in name or 'connector' in name:
        return 'platform'
    if 'theme' in name or 'website' in category:
        return 'theme'
    if 'productivity' in category or 'tools' in category:
        return 'productivity'
    return 'erp'


def guess_accent(technical_name: str) -> str:
    return ACCENT_PALETTE[sum(ord(c) for c in technical_name) % len(ACCENT_PALETTE)]


def guess_price(technical_name: str, manifest: dict, brand: dict) -> float:
    if 'price' in manifest:
        try:
            return float(manifest['price'])
        except (TypeError, ValueError):
            pass
    name = technical_name.lower()
    if 'whatsapp' in name or 'connector' in name:
        return 79.99
    if 'ai_' in name or name.startswith('rn_ai'):
        return 99.0
    if 'payroll' in name:
        return 79.0
    if 'dashboard' in name:
        return 39.0
    return float(brand.get('default_price', 9.99))


def build_catalog_entry_from_manifest(mod_dir: Path, brand: dict) -> dict:
    manifest = read_manifest(mod_dir / '__manifest__.py')
    technical_name = mod_dir.name
    app_name = str(manifest.get('name') or technical_name.replace('_', ' ').title())
    tagline = str(manifest.get('summary') or f'Commercial Odoo 19 module by {brand["company"]}.')
    category_type = guess_category_type(technical_name, manifest)
    benefits = [
        f'Streamline {app_name.lower()} workflows in Odoo',
        'Built for Odoo 19 Community',
        'Production-ready ARMORA architecture',
        'Multi-company aware where applicable',
        f'Support from {brand["company"]}',
    ]
    features = [
        {'title': 'Odoo-native', 'text': f'{app_name} extends standard Odoo models and views.'},
        {'title': 'Configurable', 'text': 'Settings, security groups, and menus included.'},
        {'title': 'Documented', 'text': 'README, INSTALL, USER_GUIDE, FAQ, and SECURITY docs.'},
        {'title': 'Commercial support', 'text': f'Contact {brand["support_email"]} for rollout help.'},
    ]
    keywords = [
        'Odoo 19',
        'Odoo Community',
        app_name,
        technical_name,
        brand['company'],
    ]
    return {
        'branch': None,
        'app_name': app_name,
        'tagline': tagline,
        'category_type': category_type,
        'price': guess_price(technical_name, manifest, brand),
        'accent': guess_accent(technical_name),
        'problem': (
            f'Teams running Odoo 19 need a reliable way to manage {app_name.lower()} '
            'without spreadsheets or disconnected tools.'
        ),
        'solution': tagline,
        'benefits': benefits,
        'features': features,
        'workflow': [
            'Install module',
            'Configure settings',
            'Assign user groups',
            'Run daily workflows',
            'Review KPIs and reports',
            'Scale across companies',
        ],
        'seo_keywords': ', '.join(keywords),
        'has_dashboard': 'dashboard' in technical_name,
        'has_reports': any(x in technical_name for x in ('report', 'gst', 'payroll', 'invoice')),
        'has_mobile': any(x in technical_name for x in ('mobile', 'portal', 'whatsapp')),
        'live_test_url': brand.get('website', 'https://www.armorait.com'),
    }


def sync_catalog_missing(catalog: dict, brand: dict) -> list[str]:
    added = []
    for mod_dir in discover_modules():
        if mod_dir.name in catalog:
            continue
        catalog[mod_dir.name] = build_catalog_entry_from_manifest(mod_dir, brand)
        added.append(mod_dir.name)
    if added:
        save_catalog(catalog)
    return added


def default_faq(brand: dict, app_name: str) -> list[dict]:
    return [
        {'q': f'Does {app_name} work on Odoo Community?', 'a': f'Yes. Built for Odoo {brand["odoo_version"]} Community.'},
        {'q': 'Multi-company support?', 'a': 'Yes, where underlying models are company-aware.'},
        {'q': 'Can we customize it?', 'a': 'Yes. Standard Odoo inheritance and service-layer patterns.'},
        {'q': 'Is documentation included?', 'a': 'README, INSTALL, USER_GUIDE, FAQ, SECURITY, and ROADMAP are included.'},
        {'q': 'How do we get support?', 'a': f'Contact {brand["support_email"]} for commercial support.'},
    ]


def related_products(technical_name: str, category_type: str, catalog: dict, limit: int = 5) -> list[dict]:
    items = []
    for name, meta in catalog.items():
        if name == technical_name:
            continue
        if meta.get('category_type') != category_type:
            continue
        items.append({'technical_name': name, 'app_name': meta['app_name'], 'tagline': meta.get('tagline', '')})
    return items[:limit]


def cleanup_description_assets(desc_dir: Path) -> None:
    """Remove stale capture files that break Apps Store index.html layouts."""
    if not desc_dir.is_dir():
        return
    for name in LEGACY_DESCRIPTION_FILES:
        path = desc_dir / name
        if path.is_file():
            path.unlink()


def sync_company_brand_assets(desc_dir: Path, brand: dict, config: dict) -> None:
    """Copy Ceres-style company logo/icon/favicon into static/description/."""
    desc_dir.mkdir(parents=True, exist_ok=True)
    for name in COMPANY_BRAND_FILES:
        src = BRAND_DIR / name
        if not src.is_file():
            continue
        shutil.copy2(src, desc_dir / name)
    cover_src = TOOLS_DIR / 'armorait_cover_logo.png'
    if cover_src.is_file():
        shutil.copy2(cover_src, desc_dir / 'armorait_cover_logo.png')
    # Keep handcrafted SCREENSHOTS.txt when a custom Apps page exists
    mod_dir = desc_dir.parent.parent
    if (mod_dir / 'marketplace' / 'custom_index.html').is_file() and (desc_dir / 'SCREENSHOTS.txt').is_file():
        return
    write_screenshots_guide(desc_dir, brand, config)


def write_screenshots_guide(desc_dir: Path, brand: dict, config: dict) -> None:
    """Write SCREENSHOTS.txt listing Apps Store description assets (Ceres pattern)."""
    app_name = config.get('app_name', desc_dir.parent.parent.name)
    technical = config.get('technical_name', desc_dir.parent.parent.name)
    lines = [
        'SCREENSHOTS for Odoo Apps listing',
        '=================================',
        '',
        f'Module: {app_name} ({technical})',
        f'Company: {brand.get("company", "ARMORA IT Technologies")}',
        f'Website: {brand.get("website", "https://www.armorait.com")}',
        f'Support: {brand.get("support_email", "info@armorait.com")}',
        '',
        'Files in this folder (static/description/):',
        '',
        'Filename                              | Purpose',
        '--------------------------------------|------------------------------------------',
        'company_logo.png / company_logo.svg   | Official ARMORA IT Technologies logo',
        'company_icon.png                      | Logo mark (square)',
        'icon.png                              | App icon for Apps Store (256x256)',
        'banner.png                            | Store banner / cover image (1200x600)',
        'banner_small.png                      | Small banner variant',
        'favicon.ico                           | Company favicon',
        'index.html                            | Apps Store description page',
        'overview.png / list.png / form.png    | Screenshot placeholders (replace with live UI)',
        'dashboard.png / wizard.png / ...      | Additional view captures',
        'hero.gif / workflow.gif / ...         | Optional GIF demos',
        '',
        'Brand colors:',
        f'  Primary:   {brand.get("primary_color", "#4f46e5")}',
        f'  Secondary: {brand.get("secondary_color", "#0f172a")}',
        f'  Accent:    {config.get("accent", brand.get("accent_default", "#2563eb"))}',
        '',
        'Current images may be UI mockups or generated covers. Replace screenshots with',
        'real Odoo 19 captures from your database before publishing when possible.',
        '',
        'Recommended capture size: about 1280 px wide (16:9 works well).',
        '',
    ]
    (desc_dir / 'SCREENSHOTS.txt').write_text('\n'.join(lines), encoding='utf-8')


def ensure_screenshot_placeholders(desc_dir: Path, config: dict) -> None:
    """Replace missing or 1x1 PNG placeholders with usable Apps Store mockups."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return

    accent = config.get('accent', '#2563eb')
    app_name = str(config.get('app_name', 'ARMORA App'))
    labels = {**SCREENSHOT_LABELS, **config.get('screenshot_labels', {})}

    def _font(size: int):
        for name in ('DejaVuSans-Bold.ttf', 'DejaVuSans.ttf'):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    def _needs_placeholder(path: Path) -> bool:
        if not path.is_file():
            return True
        try:
            with Image.open(path) as im:
                return im.size[0] < 8 or im.size[1] < 8
        except OSError:
            return True

    def _make_shot(label: str, width: int = 1440, height: int = 900) -> Image.Image:
        img = Image.new('RGB', (width, height), '#f1f5f9')
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, width, 64), fill='#0f172a')
        draw.rectangle((0, 64, 220, height), fill='#1e293b')
        draw.rectangle((220, 64, width, height), fill='#ffffff')
        draw.rectangle((220, 64, width, 68), fill=accent)
        title_font = _font(36)
        small_font = _font(20)
        draw.text((24, 18), 'ARMORA', fill='#ffffff', font=small_font)
        draw.text((248, 120), app_name, fill='#0f172a', font=title_font)
        draw.text((248, 180), label, fill='#64748b', font=small_font)
        y = 240
        for i in range(3):
            x0, y0 = 248, y + i * 180
            box = (x0, y0, width - 48, y0 + 140)
            if hasattr(draw, 'rounded_rectangle'):
                draw.rounded_rectangle(box, radius=12, fill='#f8fafc', outline='#e2e8f0', width=2)
            else:
                draw.rectangle(box, fill='#f8fafc', outline='#e2e8f0', width=2)
            draw.rectangle((x0 + 24, y0 + 28, x0 + 280, y0 + 48), fill=accent if i == 0 else '#cbd5e1')
            draw.rectangle((x0 + 24, y0 + 70, width - 96, y0 + 86), fill='#e2e8f0')
            draw.rectangle((x0 + 24, y0 + 100, width - 220, y0 + 116), fill='#e2e8f0')
        return img

    for filename in SCREENSHOT_MAP.values():
        dest = desc_dir / filename
        if not _needs_placeholder(dest):
            continue
        label = labels.get(filename, filename.replace('.png', '').replace('_', ' ').title())
        _make_shot(label).save(dest, optimize=True)


def sync_media(mod_dir: Path, config: dict, desc_dir: Path) -> tuple[dict[str, str], dict[str, str]]:
    cleanup_description_assets(desc_dir)
    mp = mod_dir / 'marketplace'
    screenshots_cfg = config.get('screenshots', {})
    gifs_cfg = config.get('gifs', {})
    screenshots: dict[str, str] = {}
    gifs: dict[str, str] = {}

    for key, filename in SCREENSHOT_MAP.items():
        dest = desc_dir / filename
        if dest.exists():
            screenshots[key] = filename
            continue
        candidates = []
        if key in screenshots_cfg:
            candidates.append(mp / screenshots_cfg[key])
        candidates.extend([
            mp / 'screenshots' / filename,
            mp / 'screenshots' / f'{key}.png',
        ])
        for src in candidates:
            if src.exists():
                if src.resolve() != dest.resolve():
                    shutil.copy2(src, dest)
                screenshots[key] = filename
                break

    for key, filename in GIF_MAP.items():
        dest = desc_dir / filename
        if dest.exists():
            gifs[key] = filename
            continue
        candidates = []
        if key in gifs_cfg:
            candidates.append(mp / gifs_cfg[key])
        candidates.extend([
            mp / 'gifs' / filename,
            mp / 'gifs' / f'{key}.gif',
        ])
        for src in candidates:
            if src.exists():
                if src.resolve() != dest.resolve():
                    shutil.copy2(src, dest)
                gifs[key] = filename
                break

    for extra in ('icon.png', 'banner.png', 'banner_small.png'):
        dest = desc_dir / extra
        asset_src = mp / 'assets' / extra
        if not dest.is_file() and asset_src.is_file():
            shutil.copy2(asset_src, dest)

    return screenshots, gifs


def render_index_html(config: dict, brand: dict, catalog: dict, mod_dir: Path) -> str:
    desc = mod_dir / 'static' / 'description'
    desc.mkdir(parents=True, exist_ok=True)
    technical_name = config.get('technical_name', mod_dir.name)
    category_type = config.get('category_type', 'erp')
    sync_company_brand_assets(desc, brand, config)
    screenshots, gifs = sync_media(mod_dir, config, desc)
    ensure_screenshot_placeholders(desc, config)
    # Refresh gallery after placeholders may have filled gaps
    screenshots = {
        key: filename
        for key, filename in SCREENSHOT_MAP.items()
        if (desc / filename).exists()
    }
    gifs = {
        key: filename
        for key, filename in GIF_MAP.items()
        if (desc / filename).exists()
    }

    # Handcrafted Apps Store pages (Ceres-quality) win over Jinja template
    custom_index = mod_dir / 'marketplace' / 'custom_index.html'
    if custom_index.is_file():
        return custom_index.read_text(encoding='utf-8')

    screenshot_labels = {**SCREENSHOT_LABELS, **config.get('screenshot_labels', {})}
    gif_labels = {**GIF_LABELS, **config.get('gif_labels', {})}

    env = Environment(
        loader=FileSystemLoader(str(FRAMEWORK / 'templates')),
        autoescape=select_autoescape(['html', 'xml']),
    )
    template = env.get_template('index.html.j2')
    return template.render(
        technical_name=technical_name,
        app_name=config['app_name'],
        tagline=config['tagline'],
        problem=config['problem'],
        solution=config['solution'],
        benefits=config.get('benefits', []),
        features=config.get('features', []),
        workflow=config.get('workflow', []),
        accent=config.get('accent', brand.get('accent_default', '#2563eb')),
        seo_keywords=config.get('seo_keywords', ''),
        version=config.get('version', '19.0.1.0.0'),
        live_test_url=config.get('live_test_url', brand.get('website')),
        has_dashboard=config.get('has_dashboard', False),
        has_reports=config.get('has_reports', False),
        has_mobile=config.get('has_mobile', False),
        faq=config.get('faq') or default_faq(brand, config['app_name']),
        testimonials=config.get('testimonials') or brand.get('testimonials_default', []),
        brand=brand,
        screenshots=screenshots,
        gifs=gifs,
        screenshot_gallery=[
            {'file': fname, 'label': label}
            for fname, label in screenshot_labels.items()
            if (desc / fname).exists()
        ],
        gif_gallery=[
            {'file': fname, 'label': label}
            for fname, label in gif_labels.items()
            if (desc / fname).exists()
        ],
        related_products=related_products(technical_name, category_type, catalog),
        category_label=CATEGORY_LABELS.get(category_type, 'ARMORA'),
        inline_css=(FRAMEWORK / 'static' / 'marketplace.css').read_text(encoding='utf-8'),
        inline_js=(FRAMEWORK / 'static' / 'marketplace.js').read_text(encoding='utf-8'),
    )


def generate_docs(mod_dir: Path, config: dict, brand: dict) -> None:
    app = config['app_name']
    (mod_dir / 'README.md').write_text(textwrap.dedent(f"""
        # {app}

        {config['tagline']}

        ## Business problem
        {config['problem']}

        ## Solution
        {config['solution']}

        ## Key benefits
        {chr(10).join('- ' + b for b in config.get('benefits', []))}

        ## Installation
        See INSTALL.md.

        ## Technical name
        `{mod_dir.name}`

        ## Support
        {brand['company']} | {brand['website']} | {brand['support_email']}

        ## License
        {brand['license']}. Proprietary to {brand['company']}.
    """).strip() + '\n', encoding='utf-8')

    faq_items = config.get('faq') or default_faq(brand, app)
    for name, body in {
        'INSTALL.md': f"# Installation\n\n1. Add module to addons path.\n2. Install **{app}**.\n3. Configure settings.\n4. Assign groups.\n",
        'FAQ.md': '\n'.join(f"## {f['q']}\n{f['a']}\n" for f in faq_items),
        'ROADMAP.md': f"# Roadmap\n\n## Shipped\n- Core release\n\nContact {brand['support_email']} for enterprise requests.\n",
        'CHANGELOG.md': f"# Changelog\n\n## {config.get('version', '19.0.1.0.0')}\n- Marketplace assets generated by ARMORA Product Builder\n",
    }.items():
        (mod_dir / name).write_text(body, encoding='utf-8')

    capture_checklist(mod_dir, config, brand)


def capture_checklist(mod_dir: Path, config: dict, brand: dict) -> None:
    app = config['app_name']
    lines = [
        f'# Capture Checklist: {app}',
        '',
        f'Technical name: `{mod_dir.name}`',
        '',
        '## Screenshots (10 minimum, 20 recommended)',
    ]
    for key, fname in SCREENSHOT_MAP.items():
        lines.append(f'- [ ] `{fname}` ({key})')
    lines += ['', '## GIFs (20-30 seconds each)']
    for key, fname in GIF_MAP.items():
        lines.append(f'- [ ] `{fname}` ({key})')
    lines += [
        '',
        '## Branding',
        '- [ ] icon.png (512x512)',
        '- [ ] banner.png (1200x600)',
        '- [ ] banner_small.png (600x300)',
        '',
        '## Publish',
        f'- [ ] Run `python build_marketplace.py {mod_dir.name}`',
        '- [ ] Review static/description/index.html',
        '- [ ] Package ZIP and upload to Odoo Apps Store',
        f'- [ ] Support contact: {brand["support_email"]}',
        '',
    ]
    content = '\n'.join(lines) + '\n'
    (mod_dir / 'marketplace' / 'CAPTURE_CHECKLIST.md').write_text(content, encoding='utf-8')
    (mod_dir / 'docs' / 'capture_checklist.md').write_text(content, encoding='utf-8')


def patch_manifest(manifest_path: Path, config: dict, brand: dict) -> None:
    text = manifest_path.read_text(encoding='utf-8')
    price = config.get('price', brand.get('default_price', 9.99))
    replacements = {
        'name': config['app_name'],
        'summary': config['tagline'],
        'author': brand['company'],
        'maintainer': brand['company'],
        'website': brand['website'],
        'support': brand['support_email'],
        'license': brand['license'],
    }
    for key, val in replacements.items():
        if f"'{key}':" in text:
            text = re.sub(rf"'{key}': '[^']*'", f"'{key}': '{val}'", text, count=1)
    if "'currency':" not in text:
        text = text.replace(
            f"'license': '{brand['license']}',",
            f"'license': '{brand['license']}',\n    'currency': '{brand['currency']}',",
            1,
        )
    if "'price':" in text:
        text = re.sub(r"'price': [^,\n]+", f"'price': {price}", text, count=1)
    else:
        text = text.replace(
            f"'currency': '{brand['currency']}',",
            f"'currency': '{brand['currency']}',\n    'price': {price},",
            1,
        )
    live = config.get('live_test_url')
    if live and "'live_test_url':" not in text:
        text = text.replace(f"'price': {price},", f"'price': {price},\n    'live_test_url': '{live}',", 1)
    desc_dir = manifest_path.parent / 'static' / 'description'
    image_paths = list(MANIFEST_IMAGES)
    if desc_dir.is_dir():
        named_shots = sorted(desc_dir.glob('screenshot_*.png'))
        if named_shots:
            image_paths = [
                'static/description/banner.png',
                'static/description/icon.png',
            ] + [f'static/description/{p.name}' for p in named_shots]
    images_block = ',\n        '.join(f"'{img}'" for img in image_paths)
    if "'images':" in text:
        text = re.sub(
            r"'images': \[[^\]]*\]",
            f"'images': [\n        {images_block},\n    ]",
            text,
            count=1,
            flags=re.S,
        )
    manifest_path.write_text(text, encoding='utf-8')


def generate_cover_assets(mod_dir: Path, animated: bool = False) -> None:
    """Regenerate icon.png and banner assets using the shared Apps Store cover generator."""
    if str(TOOLS_DIR) not in sys.path:
        sys.path.insert(0, str(TOOLS_DIR))
    from apps_store_cover import (  # noqa: WPS433
        DEFAULT_COVER_LOGO,
        read_manifest_fields,
        save_cover_assets,
        subtitle_lines_from_summary,
        title_lines_from_name,
    )

    manifest = mod_dir / '__manifest__.py'
    if not manifest.is_file():
        return
    name, summary = read_manifest_fields(manifest)
    save_cover_assets(
        mod_dir,
        title_lines_from_name(name),
        subtitle_lines_from_summary(summary),
        module_name=name,
        module_summary=summary,
        cover_logo=DEFAULT_COVER_LOGO,
        animated=animated,
    )


def build_module(
    mod_dir: Path,
    brand: dict,
    catalog: dict,
    docs: bool = True,
    covers: bool = True,
    animated_covers: bool = False,
) -> Path:
    config = load_module_config(mod_dir)
    config.setdefault('technical_name', mod_dir.name)
    (mod_dir / 'marketplace').mkdir(parents=True, exist_ok=True)
    (mod_dir / 'docs').mkdir(parents=True, exist_ok=True)

    html = render_index_html(config, brand, catalog, mod_dir)
    out = mod_dir / 'static' / 'description' / 'index.html'
    out.write_text(html, encoding='utf-8')

    if covers:
        generate_cover_assets(mod_dir, animated=animated_covers)

    if (mod_dir / '__manifest__.py').exists():
        patch_manifest(mod_dir / '__manifest__.py', config, brand)
    if docs:
        generate_docs(mod_dir, config, brand)
    return out


def init_module_from_catalog(mod_dir: Path, catalog: dict, brand: dict | None = None) -> Path:
    name = mod_dir.name
    if name not in catalog:
        if brand is None:
            brand = load_json(FRAMEWORK / 'branding.json')
        catalog[name] = build_catalog_entry_from_manifest(mod_dir, brand)
        save_catalog(catalog)
    meta = catalog[name]
    data = {
        'technical_name': name,
        'app_name': meta['app_name'],
        'tagline': meta['tagline'],
        'category_type': meta.get('category_type', 'erp'),
        'price': meta.get('price', 9.99),
        'accent': meta.get('accent', '#2563eb'),
        'problem': meta['problem'],
        'solution': meta['solution'],
        'benefits': meta.get('benefits', []),
        'features': meta.get('features', []),
        'workflow': meta.get('workflow', []),
        'seo_keywords': meta.get('seo_keywords', ''),
        'has_dashboard': meta.get('has_dashboard', False),
        'has_reports': meta.get('has_reports', False),
        'has_mobile': meta.get('has_mobile', False),
        'live_test_url': meta.get('live_test_url', 'https://www.armorait.com'),
        'version': '19.0.1.0.0',
        'branch': meta.get('branch'),
    }
    mp = mod_dir / 'marketplace'
    for sub in ('screenshots', 'gifs', 'assets'):
        (mp / sub).mkdir(parents=True, exist_ok=True)
    desc = mod_dir / 'static' / 'description'
    if desc.exists():
        for f in desc.iterdir():
            if f.suffix.lower() == '.png' and f.name in SCREENSHOT_MAP.values():
                shutil.copy2(f, mp / 'screenshots' / f.name)
            if f.suffix.lower() == '.gif' and f.name in GIF_MAP.values():
                shutil.copy2(f, mp / 'gifs' / f.name)
            if f.name in ('icon.png', 'banner.png', 'banner_small.png'):
                shutil.copy2(f, mp / 'assets' / f.name)
    return dump_module_config(mod_dir, data)


def package_zip(mod_dir: Path) -> Path:
    ZIP_OUT.mkdir(parents=True, exist_ok=True)
    zip_path = ZIP_OUT / f'{mod_dir.name}.zip'
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in mod_dir.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                zf.write(path, path.relative_to(mod_dir.parent))
    return zip_path


def discover_modules() -> list[Path]:
    return sorted(
        p for p in ARMORA_ROOT.iterdir()
        if p.is_dir()
        and p.name not in SKIP_MODULE_DIRS
        and not p.name.startswith('.')
        and (p / '__manifest__.py').exists()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='ARMORA Product Builder')
    parser.add_argument('modules', nargs='*', help='Module technical names')
    parser.add_argument('--all', action='store_true', help='Build all commercial modules')
    parser.add_argument('--init', action='store_true', help='Create marketplace/module.json from catalog')
    parser.add_argument(
        '--sync-catalog',
        action='store_true',
        help='Add missing modules to tools/apps_marketplace/catalog.json from manifests',
    )
    parser.add_argument('--zip', action='store_true', help='Package Apps Store ZIP after build')
    parser.add_argument('--no-docs', action='store_true', help='Skip README/FAQ regeneration')
    parser.add_argument(
        '--no-covers',
        action='store_true',
        help='Skip icon.png and banner regeneration (index.html only)',
    )
    parser.add_argument(
        '--animated-covers',
        action='store_true',
        help='Also generate banner.gif and banner_small.gif',
    )
    args = parser.parse_args(argv)

    brand = load_json(FRAMEWORK / 'branding.json')
    catalog = load_catalog()

    if args.sync_catalog:
        added = sync_catalog_missing(catalog, brand)
        for name in added:
            print(f'CATALOG + {name}')
        if not added:
            print('CATALOG up to date')
        if not (args.init or args.all or args.modules):
            return 0

    if args.init:
        for mod_dir in discover_modules():
            init_module_from_catalog(mod_dir, catalog, brand)
            print(f'INIT {mod_dir.name}')
        return 0

    modules = [p.name for p in discover_modules()] if (args.all or not args.modules) else args.modules

    built = []
    for name in modules:
        mod_dir = ARMORA_ROOT / name
        if not mod_dir.exists():
            print(f'SKIP missing {name}')
            continue
        if not (mod_dir / 'marketplace' / 'module.json').exists() and not (mod_dir / 'marketplace' / 'module.yaml').exists():
            init_module_from_catalog(mod_dir, catalog, brand)
        out = build_module(
            mod_dir,
            brand,
            catalog,
            docs=not args.no_docs,
            covers=not args.no_covers,
            animated_covers=args.animated_covers,
        )
        print(f'OK {name} -> {out}')
        built.append(mod_dir)
        if args.zip:
            print(f'ZIP {package_zip(mod_dir)}')

    return 0 if built else 1


if __name__ == '__main__':
    raise SystemExit(main())
