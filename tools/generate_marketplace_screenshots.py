#!/usr/bin/env python3
"""Generate Apps Store screenshot placeholders for ARMORA modules."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from apps_store_cover import read_manifest_fields
from module_app_icon import draw_module_icon

try:
    RESAMPLE = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
except AttributeError:
    RESAMPLE = getattr(Image, 'LANCZOS', Image.ANTIALIAS)

SCREEN_W = 1440
SCREEN_H = 900

PURPLE = '#714B67'
PURPLE_DARK = '#5B21B6'
PURPLE_LIGHT = '#8B5CF6'
ACCENT = '#017E84'
TEAL = '#0D9488'
BG = '#F8F9FA'
WHITE = '#FFFFFF'
NAVY = '#1F2937'
TEXT = '#374151'
MUTED = '#6B7280'
BORDER = '#E5E7EB'
SUCCESS = '#10B981'
WARNING = '#F59E0B'
INFO = '#2563EB'

PALETTES: list[tuple[str, str, str]] = [
    ('#8B5CF6', '#5B21B6', '#10B981'),
    ('#2563EB', '#1D4ED8', '#38BDF8'),
    ('#0D9488', '#047857', '#34D399'),
    ('#EA580C', '#C2410C', '#FDBA74'),
    ('#DB2777', '#9D174D', '#F9A8D4'),
    ('#0891B2', '#0E7490', '#67E8F9'),
    ('#4F46E5', '#3730A3', '#A5B4FC'),
    ('#CA8A04', '#A16207', '#FDE047'),
]


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        ('DejaVuSans-Bold.ttf', 'DejaVuSans.ttf') if bold
        else ('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf')
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def _module_palette(module_slug: str) -> tuple[str, str, str]:
    digest = hashlib.md5(module_slug.encode()).hexdigest()
    return PALETTES[int(digest[:2], 16) % len(PALETTES)]


def _short_title(name: str, max_len: int = 28) -> str:
    text = re.sub(r'\s+', ' ', name.strip())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rsplit(' ', 1)[0]


def _base_chrome(draw: ImageDraw.ImageDraw, w: int, h: int, title: str, active: str) -> tuple[int, int, int, int]:
    draw.rectangle((0, 0, w, 48), fill=PURPLE)
    draw.text((16, 14), 'Odoo', font=_font(15, True), fill=WHITE)
    draw.text((78, 15), title, font=_font(14), fill='#E9D5FF')
    for i in range(3):
        x = w - 130 + i * 38
        _rounded_rect(draw, (x, 12, x + 30, 36), 6, '#5B3A52')

    draw.rectangle((0, 48, 220, h), fill=WHITE)
    draw.line((220, 48, 220, h), fill=BORDER, width=1)
    items = [active, 'Reports', 'Configuration', 'Settings']
    y = 64
    for label in items:
        is_active = label == active
        if is_active:
            draw.rectangle((0, y - 6, 4, y + 24), fill=PURPLE_LIGHT)
            draw.rectangle((10, y - 6, 210, y + 24), fill='#F3E8FF')
        draw.text((22, y), label, font=_font(13, is_active), fill=PURPLE if is_active else TEXT)
        y += 38
    return 236, 60, w - 24, h - 24


def _footer_badge(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    label = 'ARMORA IT Technologies'
    font = _font(11)
    tw, th = _text_size(draw, label, font)
    pad_x, pad_y = 10, 5
    x = w - tw - pad_x * 2 - 18
    y = h - th - pad_y * 2 - 16
    _rounded_rect(draw, (x, y, x + tw + pad_x * 2, y + th + pad_y * 2), 10, NAVY)
    draw.text((x + pad_x, y + pad_y), label, font=font, fill=WHITE)


def draw_dashboard_scene(module_slug: str, module_name: str, summary: str) -> Image.Image:
    top, accent, _ = _module_palette(module_slug)
    title = _short_title(module_name)
    img = Image.new('RGB', (SCREEN_W, SCREEN_H), BG)
    draw = ImageDraw.Draw(img)
    left, top_y, right, bottom = _base_chrome(draw, SCREEN_W, SCREEN_H, title, title)

    draw.text((left, top_y), 'Dashboard', font=_font(24, True), fill=NAVY)
    draw.text((left, top_y + 34), summary[:72] + ('...' if len(summary) > 72 else ''), font=_font(13), fill=MUTED)

    cards = [
        ('Open', '128', top),
        ('In progress', '42', accent),
        ('Completed', '316', SUCCESS),
        ('Alerts', '7', WARNING),
    ]
    card_y = top_y + 72
    gap = 18
    card_w = (right - left - gap * 3) // 4
    for index, (label, value, color) in enumerate(cards):
        x = left + index * (card_w + gap)
        _rounded_rect(draw, (x, card_y, x + card_w, card_y + 96), 14, WHITE, outline=BORDER)
        draw.text((x + 18, card_y + 16), label, font=_font(12), fill=MUTED)
        draw.text((x + 18, card_y + 42), value, font=_font(30, True), fill=color)

    chart_y = card_y + 118
    chart_h = 250
    _rounded_rect(draw, (left, chart_y, right, chart_y + chart_h), 14, WHITE, outline=BORDER)
    draw.text((left + 18, chart_y + 16), 'Weekly activity', font=_font(14, True), fill=NAVY)
    bar_base = chart_y + chart_h - 36
    bar_w = 34
    for index, height in enumerate((120, 170, 95, 210, 160, 190, 140)):
        x = left + 36 + index * (bar_w + 24)
        _rounded_rect(draw, (x, bar_base - height, x + bar_w, bar_base), 8, accent if index % 2 else top)

    list_y = chart_y + chart_h + 20
    _rounded_rect(draw, (left, list_y, right, bottom), 14, WHITE, outline=BORDER)
    draw.text((left + 18, list_y + 16), 'Recent records', font=_font(14, True), fill=NAVY)
    row_y = list_y + 52
    for index in range(4):
        _rounded_rect(draw, (left + 18, row_y, right - 18, row_y + 34), 8, '#F9FAFB', outline=BORDER)
        draw.text((left + 30, row_y + 9), f'REC/{202600 + index:04d}', font=_font(12, True), fill=NAVY)
        draw.text((left + 180, row_y + 9), title, font=_font(12), fill=TEXT)
        status = ('Confirmed', 'Draft', 'Done', 'Pending')[index]
        color = (SUCCESS, MUTED, INFO, WARNING)[index]
        draw.text((right - 120, row_y + 9), status, font=_font(12, True), fill=color)
        row_y += 42

    _footer_badge(draw, SCREEN_W, SCREEN_H)
    return img


def draw_workflow_scene(module_slug: str, module_name: str, summary: str) -> Image.Image:
    top, accent, highlight = _module_palette(module_slug)
    title = _short_title(module_name)
    img = Image.new('RGB', (SCREEN_W, SCREEN_H), BG)
    draw = ImageDraw.Draw(img)
    left, top_y, right, bottom = _base_chrome(draw, SCREEN_W, SCREEN_H, title, 'Workflow')

    draw.text((left, top_y), 'Workflow overview', font=_font(24, True), fill=NAVY)
    draw.text((left, top_y + 34), 'Automated steps configured for this module', font=_font(13), fill=MUTED)

    steps = [
        ('Trigger', 'Event or schedule starts the flow'),
        ('Validate', 'Rules and data checks run first'),
        ('Approve', 'Managers review when required'),
        ('Execute', 'Odoo actions run with audit trail'),
        ('Notify', 'Teams get updates in Discuss'),
    ]
    node_w = 210
    node_h = 118
    gap = 34
    total_w = len(steps) * node_w + (len(steps) - 1) * gap
    start_x = left + max((right - left - total_w) // 2, 0)
    node_y = top_y + 110
    for index, (label, detail) in enumerate(steps):
        x = start_x + index * (node_w + gap)
        color = (top, accent, highlight, SUCCESS, INFO)[index % 5]
        _rounded_rect(draw, (x, node_y, x + node_w, node_y + node_h), 16, WHITE, outline=color, width=2)
        _rounded_rect(draw, (x + 16, node_y + 16, x + 52, node_y + 52), 12, color)
        draw.text((x + 64, node_y + 22), f'{index + 1}', font=_font(18, True), fill=WHITE)
        draw.text((x + 16, node_y + 64), label, font=_font(15, True), fill=NAVY)
        wrapped = detail if len(detail) <= 28 else detail[:27] + '...'
        draw.text((x + 16, node_y + 88), wrapped, font=_font(11), fill=MUTED)
        if index < len(steps) - 1:
            ax = x + node_w + 4
            ay = node_y + node_h // 2
            draw.line((ax, ay, ax + gap - 8, ay), fill=color, width=3)
            draw.polygon([(ax + gap - 8, ay), (ax + gap - 18, ay - 7), (ax + gap - 18, ay + 7)], fill=color)

    panel_y = node_y + node_h + 48
    _rounded_rect(draw, (left, panel_y, right, bottom), 14, WHITE, outline=BORDER)
    draw.text((left + 18, panel_y + 16), 'Execution log', font=_font(14, True), fill=NAVY)
    log_y = panel_y + 52
    for index, message in enumerate(
        (
            'Trigger matched: new record created',
            'Validation passed: required fields complete',
            'Approval granted by Operations Manager',
            'Action completed: notification sent',
        )
    ):
        _rounded_rect(draw, (left + 18, log_y, right - 18, log_y + 38), 8, '#F9FAFB', outline=BORDER)
        draw.ellipse((left + 30, log_y + 14, left + 42, log_y + 26), fill=SUCCESS)
        draw.text((left + 54, log_y + 10), message, font=_font(12), fill=TEXT)
        draw.text((right - 110, log_y + 10), f'0{index + 1}:0{index + 2}', font=_font(11), fill=MUTED)
        log_y += 46

    _footer_badge(draw, SCREEN_W, SCREEN_H)
    return img


def draw_designer_scene(module_slug: str, module_name: str, summary: str) -> Image.Image:
    top, accent, _ = _module_palette(module_slug)
    title = _short_title(module_name)
    img = Image.new('RGB', (SCREEN_W, SCREEN_H), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, SCREEN_W, 48), fill=PURPLE)
    draw.text((16, 14), 'Odoo', font=_font(15, True), fill=WHITE)
    draw.text((78, 15), f'{title} Designer', font=_font(14), fill='#E9D5FF')

    palette_w = 240
    props_w = 280
    draw.rectangle((0, 48, palette_w, SCREEN_H), fill=WHITE)
    draw.rectangle((SCREEN_W - props_w, 48, SCREEN_W, SCREEN_H), fill=WHITE)
    draw.line((palette_w, 48, palette_w, SCREEN_H), fill=BORDER, width=1)
    draw.line((SCREEN_W - props_w, 48, SCREEN_W - props_w, SCREEN_H), fill=BORDER, width=1)

    draw.text((18, 64), 'Components', font=_font(13, True), fill=NAVY)
    comp_y = 94
    for label in ('Text field', 'Selection', 'Checkbox', 'Notebook', 'Button', 'Smart button'):
        _rounded_rect(draw, (14, comp_y, palette_w - 14, comp_y + 34), 8, '#F9FAFB', outline=BORDER)
        draw.text((26, comp_y + 9), label, font=_font(12), fill=TEXT)
        comp_y += 42

    canvas_left = palette_w + 24
    canvas_right = SCREEN_W - props_w - 24
    canvas_top = 72
    canvas_bottom = SCREEN_H - 24
    _rounded_rect(draw, (canvas_left, canvas_top, canvas_right, canvas_bottom), 16, WHITE, outline=BORDER)
    draw.text((canvas_left + 20, canvas_top + 18), 'Form layout', font=_font(18, True), fill=NAVY)
    draw.text((canvas_left + 20, canvas_top + 48), summary[:64] + ('...' if len(summary) > 64 else ''), font=_font(12), fill=MUTED)

    field_y = canvas_top + 88
    fields = [
        ('Name', 'Customer reference'),
        ('Status', 'Draft / Confirmed / Done'),
        ('Owner', 'Assigned user'),
        ('Notes', 'Internal comments'),
    ]
    for label, hint in fields:
        _rounded_rect(draw, (canvas_left + 20, field_y, canvas_right - 20, field_y + 72), 12, '#F9FAFB', outline=top, width=2)
        draw.text((canvas_left + 34, field_y + 14), label, font=_font(12, True), fill=NAVY)
        draw.text((canvas_left + 34, field_y + 36), hint, font=_font(12), fill=MUTED)
        field_y += 84

    draw.text((SCREEN_W - props_w + 18, 64), 'Properties', font=_font(13, True), fill=NAVY)
    prop_y = 94
    for label, value in (
        ('Label', 'Customer reference'),
        ('Widget', 'Char'),
        ('Required', 'Yes'),
        ('Tracking', 'Enabled'),
        ('Groups', 'Sales / User'),
    ):
        draw.text((SCREEN_W - props_w + 18, prop_y), label, font=_font(11, True), fill=MUTED)
        _rounded_rect(draw, (SCREEN_W - props_w + 18, prop_y + 18, SCREEN_W - 18, prop_y + 46), 8, '#F9FAFB', outline=BORDER)
        draw.text((SCREEN_W - props_w + 28, prop_y + 26), value, font=_font(12), fill=TEXT)
        prop_y += 58

    _rounded_rect(draw, (canvas_left + 20, canvas_bottom - 58, canvas_left + 180, canvas_bottom - 18), 10, accent)
    draw.text((canvas_left + 52, canvas_bottom - 46), 'Save layout', font=_font(12, True), fill=WHITE)

    _footer_badge(draw, SCREEN_W, SCREEN_H)
    return img


def save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert('RGB').save(path, 'PNG', optimize=True)


def generate_for_module(
    module_dir: Path,
    *,
    skip_existing: bool = False,
    force: bool = False,
    include_icon: bool = True,
) -> list[str]:
    manifest = module_dir / '__manifest__.py'
    if not manifest.is_file():
        return []
    module_slug = module_dir.name
    module_name, summary = read_manifest_fields(manifest)
    out = module_dir / 'static' / 'description'
    out.mkdir(parents=True, exist_ok=True)

    assets = {
        'dashboard.png': draw_dashboard_scene(module_slug, module_name, summary),
        'workflow.png': draw_workflow_scene(module_slug, module_name, summary),
        'designer.png': draw_designer_scene(module_slug, module_name, summary),
    }
    written: list[str] = []
    for filename, image in assets.items():
        path = out / filename
        if skip_existing and path.is_file() and not force:
            continue
        save_png(image, path)
        written.append(filename)

    icon_path = out / 'icon.png'
    if include_icon and (not skip_existing or not icon_path.is_file()):
        icon = draw_module_icon(module_slug, module_name, summary)
        icon.save(icon_path, 'PNG', optimize=True)
        written.append('icon.png')
    return written


def generate_for_repo(repo_root: Path, skip_existing: bool = False, force: bool = False, include_icon: bool = True) -> dict[str, list[str]]:
    skip_dirs = {'tools', 'armorait2_site', '.git', '.github', '.tmp'}
    results: dict[str, list[str]] = {}
    for manifest in sorted(repo_root.glob('*/__manifest__.py')):
        module_dir = manifest.parent
        if module_dir.name in skip_dirs:
            continue
        written = generate_for_module(module_dir, skip_existing=skip_existing, force=force, include_icon=include_icon)
        if written:
            results[module_dir.name] = written
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate Apps Store screenshot placeholders.')
    parser.add_argument(
        'repo_root',
        nargs='?',
        default=str(Path(__file__).resolve().parents[1]),
        help='Path to armora repo root (default: parent of tools/)',
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Do not overwrite files that already exist',
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite workflow, dashboard, and designer PNG files',
    )
    parser.add_argument(
        '--no-icon',
        action='store_true',
        help='Skip icon.png generation',
    )
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        raise SystemExit(f'Repo not found: {repo_root}')

    results = generate_for_repo(
        repo_root,
        skip_existing=args.skip_existing,
        force=args.force,
        include_icon=not args.no_icon,
    )
    print(f'Generated marketplace screenshots for {len(results)} modules in {repo_root}')
    for module_name, files in results.items():
        print(f'  {module_name}: {", ".join(files)}')


if __name__ == '__main__':
    main()
