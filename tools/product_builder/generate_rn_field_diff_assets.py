#!/usr/bin/env python3
"""Generate Field Difference Viewer Apps Store screenshot placeholders."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_field_diff'
MOD_DIR = ROOT / MODULE
DESC = MOD_DIR / 'static' / 'description'
MP_SHOTS = MOD_DIR / 'marketplace' / 'screenshots'
MP_GIFS = MOD_DIR / 'marketplace' / 'gifs'

W, H = 1440, 900


def _font(size: int, bold: bool = False):
    names = ('DejaVuSans-Bold.ttf', 'DejaVuSans.ttf') if bold else ('DejaVuSans.ttf',)
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _diff_card(draw, y, field, before, after, diff, color='#2563eb'):
    draw.rounded_rectangle((40, y, W - 40, y + 110), radius=8, fill='white', outline='#e5e7eb')
    draw.text((56, y + 12), field, font=_font(16, True), fill='#111827')
    draw.text((56, y + 40), 'Before', font=_font(11), fill='#6b7280')
    draw.text((56, y + 56), before, font=_font(14), fill='#111827')
    draw.text((W // 2 - 20, y + 48), 'v', font=_font(16, True), fill=color)
    draw.text((W // 2 + 20, y + 40), 'After', font=_font(11), fill='#6b7280')
    draw.text((W // 2 + 20, y + 56), after, font=_font(14), fill='#111827')
    if diff:
        draw.text((56, y + 82), 'Difference: %s' % diff, font=_font(12, True), fill=color)


def _scene(title: str, subtitle: str, cards: list[tuple[str, str, str, str, str]]) -> Image.Image:
    img = Image.new('RGB', (W, H), '#f8fafc')
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 56), fill='#1f2937')
    draw.text((20, 18), 'Field Difference Viewer', font=_font(18, True), fill='white')
    draw.text((W - 280, 20), title, font=_font(14, True), fill='#93c5fd')
    draw.text((40, 80), subtitle, font=_font(22, True), fill='#111827')
    y = 140
    for field, before, after, diff, color in cards:
        _diff_card(draw, y, field, before, after, diff, color)
        y += 125
    return img


SCENES = {
    'overview.png': _scene('Overview', 'Readable before/after comparisons', [
        ('Amount Total', '1000', '1800', '+800', '#2563eb'),
        ('Customer', 'ABC Ltd', 'XYZ Ltd', '', '#2563eb'),
    ]),
    'list.png': _scene('Change Log', 'All field changes in one list', [
        ('Partner', 'Azure Interiors', 'Gemini Furniture', '', '#2563eb'),
        ('Status', 'Draft', 'Confirmed', '', '#16a34a'),
    ]),
    'form.png': _scene('Diff Detail', 'Full comparison for one change', [
        ('Expected Revenue', '1000.00', '1800.00', '+800 (+80%)', '#2563eb'),
    ]),
    'dashboard.png': _scene('Sale Order History', 'Smart button opens change viewer', [
        ('Order Partner', 'COLORTAG A', 'COLORTAG B', '', '#2563eb'),
        ('Locked', 'Disabled', 'Enabled', '', '#16a34a'),
    ]),
    'wizard.png': _scene('Comparison Dialog', 'GitHub-style diff popup', [
        ('Discount', '5%', '10%', '+5%', '#2563eb'),
        ('Quantity', '20', '15', '-5', '#dc2626'),
    ]),
    'settings.png': _scene('Filters', 'Numeric, date, text, and user filters', [
        ('Filter', 'Numeric only', '3 changes', '', '#6b7280'),
        ('Filter', 'My changes', '1 change', '', '#6b7280'),
    ]),
    'report.png': _scene('PDF Export', 'Audit-ready change reports', [
        ('Export', 'CSV', '12 rows', '', '#2563eb'),
        ('Export', 'PDF', '4 pages', '', '#2563eb'),
    ]),
    'search.png': _scene('CRM Diffs', 'Opportunity revenue and stage changes', [
        ('Expected Revenue', '25000', '32000', '+7000', '#2563eb'),
        ('Stage', 'Qualified', 'Proposition', '', '#7c3aed'),
    ]),
    'kanban.png': _scene('Timeline Mode', 'Changes grouped by day', [
        ('Today - Price', '100', '150', '+50', '#2563eb'),
        ('Yesterday - Discount', '5%', '10%', '+5%', '#2563eb'),
    ]),
    'mobile.png': _scene('Mobile History', 'Readable on small screens', [
        ('Partner', 'Before A', 'After B', '', '#2563eb'),
    ]),
    'workflow.png': _scene('Workflow', 'Edit, compare, filter, export', [
        ('Step 1', 'Edit record', 'Tracked write', '', '#2563eb'),
        ('Step 2', 'View diff', 'History button', '', '#16a34a'),
    ]),
    'designer.png': _scene('Numeric Comparison', 'Delta and percent change', [
        ('Subtotal', '10250', '11800', '+1550', '#2563eb'),
        ('Tax', '820', '944', '+124', '#2563eb'),
    ]),
}


def frames_to_gif(frames: list[Path], out: Path) -> None:
    if len(frames) < 2:
        if frames:
            shutil.copy2(frames[0], out.with_suffix('.png'))
        return
    lst = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
    for fr in frames:
        lst.write(f"file '{fr}'\nduration 2\n")
    lst.close()
    subprocess.run(
        ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst.name,
         '-vf', 'fps=6,scale=1100:-1:flags=lanczos', str(out)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    Path(lst.name).unlink(missing_ok=True)


def main() -> int:
    for folder in (DESC, MP_SHOTS, MP_GIFS):
        folder.mkdir(parents=True, exist_ok=True)
    for name, image in SCENES.items():
        image.save(DESC / name, 'PNG')
        image.save(MP_SHOTS / name, 'PNG')
    for gif_name, keys in {
        'hero.gif': ('overview.png', 'list.png', 'dashboard.png', 'wizard.png'),
        'workflow.gif': ('workflow.png', 'form.png', 'designer.png'),
        'dashboard.gif': ('dashboard.png', 'kanban.png', 'search.png'),
        'settings.gif': ('settings.png', 'list.png'),
        'reports.gif': ('report.png', 'dashboard.png'),
        'mobile.gif': ('mobile.png', 'overview.png'),
    }.items():
        frames = []
        for key in keys:
            tmp = Path(tempfile.mkstemp(suffix='.png')[1])
            SCENES[key].save(tmp, 'PNG')
            frames.append(tmp)
        out = DESC / gif_name
        frames_to_gif(frames, out)
        if out.exists():
            shutil.copy2(out, MP_GIFS / gif_name)
        for fr in frames:
            fr.unlink(missing_ok=True)
    subprocess.run(
        [sys.executable, str(ROOT / 'build_marketplace.py'), MODULE, '--no-docs'],
        cwd=str(ROOT), check=True,
    )
    print('Generated synthetic assets for', MODULE)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
