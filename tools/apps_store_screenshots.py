#!/usr/bin/env python3
"""Generate Apps Store screenshot placeholders for ARMORA modules."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from apps_store_cover import read_manifest_fields

try:
    RESAMPLE = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
except AttributeError:
    RESAMPLE = getattr(Image, 'LANCZOS', Image.ANTIALIAS)

WIDTH = 1280
HEIGHT = 800

PURPLE = '#714B67'
PURPLE_LIGHT = '#8B5CF6'
ACCENT = '#017E84'
ACCENT_LIGHT = '#14B8A6'
BG = '#F8F9FA'
WHITE = '#FFFFFF'
NAVY = '#1F2937'
TEXT = '#374151'
MUTED = '#6B7280'
BORDER = '#E5E7EB'
SUCCESS = '#10B981'
WARNING = '#F59E0B'
DANGER = '#EF4444'
INFO = '#3B82F6'

SCREENSHOT_FILES = (
    'workflow.png',
    'dashboard.png',
    'monitoring.png',
    'ai_builder.png',
    'execution.png',
)

SCREENSHOT_LABELS = {
    'workflow.png': 'Workflow',
    'dashboard.png': 'Dashboard',
    'monitoring.png': 'Monitoring',
    'ai_builder.png': 'AI Builder',
    'execution.png': 'Execution',
}


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


def _chrome(draw: ImageDraw.ImageDraw, module_name: str, screen_title: str) -> None:
    draw.rectangle((0, 0, WIDTH, 48), fill=NAVY)
    draw.text((16, 15), 'Odoo', font=_font(15, True), fill=WHITE)
    draw.text((78, 16), module_name, font=_font(13), fill='#D1D5DB')
    draw.text((WIDTH - 220, 16), screen_title, font=_font(12, True), fill=ACCENT_LIGHT)
    draw.rectangle((0, 48, 220, HEIGHT), fill=WHITE)
    draw.line((220, 48, 220, HEIGHT), fill=BORDER, width=1)
    y = 68
    for label, active in (
        ('Overview', False),
        ('Workflow', screen_title == 'Workflow'),
        ('Dashboard', screen_title == 'Dashboard'),
        ('Monitoring', screen_title == 'Monitoring'),
        ('AI Builder', screen_title == 'AI Builder'),
        ('Execution', screen_title == 'Execution'),
        ('Settings', False),
    ):
        if active:
            draw.rectangle((0, y - 6, 4, y + 24), fill=PURPLE)
            draw.rectangle((10, y - 6, 210, y + 24), fill='#F3E8FF')
        draw.text((22, y), label, font=_font(12, active), fill=PURPLE if active else TEXT)
        y += 34


def _content_panel(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, title: str) -> tuple[int, int, int, int]:
    _rounded_rect(draw, (x, y, x + w, y + h), 12, WHITE, outline=BORDER)
    draw.text((x + 16, y + 14), title, font=_font(13, True), fill=TEXT)
    return x + 16, y + 44, w - 32, h - 58


def _draw_workflow(draw: ImageDraw.ImageDraw, module_name: str) -> None:
    _chrome(draw, module_name, 'Workflow')
    nodes = [
        (360, 180, 'Trigger', ACCENT),
        (560, 140, 'Condition', WARNING),
        (760, 180, 'Action', SUCCESS),
        (960, 220, 'Notify', INFO),
    ]
    for index, (x, y, label, color) in enumerate(nodes):
        _rounded_rect(draw, (x, y, x + 150, y + 72), 14, color)
        draw.text((x + 18, y + 24), label, font=_font(14, True), fill=WHITE)
        if index < len(nodes) - 1:
            nx = nodes[index + 1][0]
            ny = nodes[index + 1][1] + 36
            draw.line((x + 150, y + 36, nx, ny), fill=MUTED, width=3)
    _content_panel(draw, 250, 360, 990, 360, 'Automation Flow')
    for row, line in enumerate(
        (
            'When sales order is confirmed',
            'If amount is above threshold',
            'Create approval request and send email',
            'Log execution in monitoring timeline',
        )
    ):
        draw.text((280, 430 + row * 34), f'{row + 1}. {line}', font=_font(13), fill=TEXT)


def _draw_dashboard(draw: ImageDraw.ImageDraw, module_name: str) -> None:
    _chrome(draw, module_name, 'Dashboard')
    cards = (
        ('Runs Today', '128', SUCCESS),
        ('Success Rate', '97%', ACCENT),
        ('Failures', '4', DANGER),
        ('Queue', '12', WARNING),
    )
    x = 250
    for title, value, color in cards:
        _rounded_rect(draw, (x, 100, x + 220, 190), 14, WHITE, outline=BORDER)
        draw.text((x + 18, 118), title, font=_font(12), fill=MUTED)
        draw.text((x + 18, 142), value, font=_font(28, True), fill=color)
        x += 240
    _content_panel(draw, 250, 220, 470, 500, 'Performance')
    for bar, width in ((120, 360), (180, 280), (240, 420), (300, 220), (360, 340)):
        _rounded_rect(draw, (280, bar, 280 + width, bar + 22), 8, ACCENT_LIGHT)
    _content_panel(draw, 740, 220, 500, 500, 'Recent Activity')
    for row, line in enumerate(
        (
            'SO/1042 automation completed',
            'PO/883 webhook delivered',
            'HR leave workflow scheduled',
            'Invoice OCR action retried',
        )
    ):
        draw.text((760, 290 + row * 48), line, font=_font(12), fill=TEXT)


def _draw_monitoring(draw: ImageDraw.ImageDraw, module_name: str) -> None:
    _chrome(draw, module_name, 'Monitoring')
    _content_panel(draw, 250, 100, 990, 620, 'Execution Monitor')
    headers = ('Run', 'Workflow', 'Status', 'Duration', 'Started')
    hx = 280
    for header in headers:
        draw.text((hx, 170), header, font=_font(11, True), fill=MUTED)
        hx += 170
    rows = (
        ('#10482', 'SO Approval', 'Success', '1.2s', '10:42'),
        ('#10481', 'PO Notify', 'Success', '0.8s', '10:39'),
        ('#10480', 'Stock Alert', 'Failed', '2.4s', '10:35'),
        ('#10479', 'HR Onboarding', 'Retry', '3.1s', '10:31'),
    )
    y = 210
    for run_id, workflow, status, duration, started in rows:
        color = SUCCESS if status == 'Success' else DANGER if status == 'Failed' else WARNING
        draw.text((280, y), run_id, font=_font(12), fill=TEXT)
        draw.text((450, y), workflow, font=_font(12), fill=TEXT)
        _rounded_rect(draw, (620, y - 4, 700, y + 20), 10, color)
        draw.text((632, y), status, font=_font(10, True), fill=WHITE)
        draw.text((790, y), duration, font=_font(12), fill=TEXT)
        draw.text((960, y), started, font=_font(12), fill=TEXT)
        y += 52


def _draw_ai_builder(draw: ImageDraw.ImageDraw, module_name: str) -> None:
    _chrome(draw, module_name, 'AI Builder')
    _content_panel(draw, 250, 100, 520, 620, 'Describe Your Workflow')
    draw.text(
        (280, 170),
        'When a sales order is confirmed and total is above 5000,',
        font=_font(13),
        fill=TEXT,
    )
    draw.text(
        (280, 200),
        'start approval, notify sales manager, and update CRM stage.',
        font=_font(13),
        fill=TEXT,
    )
    _rounded_rect(draw, (280, 250, 720, 310), 12, PURPLE)
    draw.text((310, 270), 'Generate Workflow', font=_font(14, True), fill=WHITE)
    _content_panel(draw, 790, 100, 450, 620, 'AI Draft Preview')
    steps = (
        'Trigger: Sales Order confirmed',
        'Condition: amount > 5000',
        'Action: Start approval workflow',
        'Action: Send email to manager',
        'Action: Update CRM opportunity stage',
    )
    y = 180
    for step in steps:
        _rounded_rect(draw, (820, y, 1180, y + 44), 10, '#EDE9FE')
        draw.text((836, y + 12), step, font=_font(11), fill=PURPLE)
        y += 58


def _draw_execution(draw: ImageDraw.ImageDraw, module_name: str) -> None:
    _chrome(draw, module_name, 'Execution')
    _content_panel(draw, 250, 100, 620, 620, 'Run Timeline')
    points = (
        (300, 180, 'Trigger received', SUCCESS),
        (300, 250, 'Conditions evaluated', SUCCESS),
        (300, 320, 'Approval request created', ACCENT),
        (300, 390, 'Email queued', WARNING),
        (300, 460, 'Webhook dispatched', INFO),
    )
    for x, y, label, color in points:
        draw.ellipse((x, y, x + 18, y + 18), fill=color)
        draw.text((x + 30, y - 2), label, font=_font(12), fill=TEXT)
        if y < 460:
            draw.line((309, y + 18, 309, y + 52), fill=BORDER, width=3)
    _content_panel(draw, 890, 100, 350, 620, 'Error Log')
    draw.text((920, 180), 'No blocking errors', font=_font(12, True), fill=SUCCESS)
    draw.text((920, 220), 'Last run completed in 1.8s', font=_font(12), fill=MUTED)
    draw.text((920, 260), 'Retry queue empty', font=_font(12), fill=MUTED)


DRAWERS = {
    'workflow.png': _draw_workflow,
    'dashboard.png': _draw_dashboard,
    'monitoring.png': _draw_monitoring,
    'ai_builder.png': _draw_ai_builder,
    'execution.png': _draw_execution,
}


def draw_screenshot(module_name: str, filename: str) -> Image.Image:
    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    drawer = DRAWERS[filename]
    drawer(draw, module_name)
    label = SCREENSHOT_LABELS[filename]
    tw, th = _text_size(draw, label, _font(11))
    _rounded_rect(draw, (WIDTH - tw - 36, HEIGHT - 42, WIDTH - 12, HEIGHT - 12), 8, NAVY)
    draw.text((WIDTH - tw - 24, HEIGHT - 36), label, font=_font(11), fill=WHITE)
    return img


def save_screenshot_assets(
    module_dir: Path,
    module_name: str,
    *,
    force: bool = False,
) -> list[str]:
    out = module_dir / 'static' / 'description'
    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for filename in SCREENSHOT_FILES:
        target = out / filename
        if target.is_file() and not force:
            continue
        image = draw_screenshot(module_name, filename)
        image.save(target, 'PNG', optimize=True)
        written.append(filename)
    return written


def generate_screenshots_for_repo(
    repo_root: Path,
    *,
    force: bool = False,
) -> dict[str, list[str]]:
    skip = {'tools', 'armorait2_site', '.git', '.github', '.tmp', 'apps_store_zips', 'ai_employee'}
    generated: dict[str, list[str]] = {}
    for manifest in sorted(repo_root.glob('*/__manifest__.py')):
        module_dir = manifest.parent
        if module_dir.name in skip:
            continue
        name, _summary = read_manifest_fields(manifest)
        files = save_screenshot_assets(module_dir, name, force=force)
        if files:
            generated[module_dir.name] = files
    return generated


def standard_images_manifest_block() -> str:
    lines = [
        "    'images': [",
        "        'static/description/banner.png',",
        "        'static/description/icon.png',",
        "        'static/description/workflow.png',",
        "        'static/description/dashboard.png',",
        "        'static/description/monitoring.png',",
        "        'static/description/ai_builder.png',",
        "        'static/description/execution.png',",
        "    ],",
    ]
    return '\n'.join(lines)


def update_manifest_images(manifest_path: Path) -> bool:
    text = manifest_path.read_text(encoding='utf-8')
    pattern = re.compile(
        r"    'images': \[\n(?:        'static/description/[^']+',\n)+    \],",
        re.MULTILINE,
    )
    replacement = standard_images_manifest_block()
    if not pattern.search(text):
        return False
    updated = pattern.sub(replacement, text, count=1)
    if updated == text:
        return False
    manifest_path.write_text(updated, encoding='utf-8')
    return True


def update_all_manifest_images(repo_root: Path) -> list[str]:
    skip = {'tools', 'armorait2_site', '.git', '.github', '.tmp', 'apps_store_zips', 'ai_employee'}
    updated: list[str] = []
    for manifest in sorted(repo_root.glob('*/__manifest__.py')):
        if manifest.parent.name in skip:
            continue
        if update_manifest_images(manifest):
            updated.append(manifest.parent.name)
    return updated
