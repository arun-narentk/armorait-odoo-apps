#!/usr/bin/env python3
"""Generate Record Share / Copy Record Link Apps Store screenshot placeholders."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'rn_record_share'
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


def _form_scene(title: str, subtitle: str, record: str, buttons: list[str]) -> Image.Image:
    img = Image.new('RGB', (W, H), '#f8fafc')
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 56), fill='#1f2937')
    draw.text((20, 18), 'Record Share', font=_font(18, True), fill='white')
    draw.text((W - 280, 20), title, font=_font(14, True), fill='#5eead4')
    draw.text((40, 80), record, font=_font(24, True), fill='#111827')
    draw.text((40, 120), subtitle, font=_font(16), fill='#6b7280')
    draw.rounded_rectangle((40, 170, W - 40, 250), radius=10, fill='white', outline='#e5e7eb')
    x = 60
    for label in buttons:
        draw.rounded_rectangle((x, 190, x + 150, 230), radius=8, fill='#ecfeff', outline='#0d9488')
        draw.text((x + 16, 200), label, font=_font(13, True), fill='#0f766e')
        x += 170
    draw.rounded_rectangle((40, 280, W - 40, H - 40), radius=10, fill='white', outline='#e5e7eb')
    draw.text((60, 310), 'Copied to clipboard', font=_font(18, True), fill='#16a34a')
    draw.text((60, 350), 'https://example.odoo.com/odoo/sale.order/245', font=_font(14), fill='#2563eb')
    draw.text((60, 390), 'Paste in browser to open the same record instantly.', font=_font(14), fill='#6b7280')
    return img


SCENES = {
    'workflow.png': _form_scene(
        'Copy Link',
        'One click from any supported form view',
        'SO0245 - Azure Interior',
        ['Copy Link', 'Share', 'QR'],
    ),
    'dashboard.png': _form_scene(
        'Share Wizard',
        'Preview URL, Markdown, HTML, and JSON formats',
        'ShareCap Demo Customer',
        ['Copy URL', 'Copy MD', 'Email'],
    ),
    'designer.png': _form_scene(
        'Share History',
        'Audit trail per user with format and timestamp',
        'Recent shares',
        ['Copy', 'Email', 'WhatsApp'],
    ),
    'settings.png': _form_scene(
        'Settings',
        'Default format, retention, and channel toggles',
        'Record Share configuration',
        ['URL', 'Retention', 'WhatsApp'],
    ),
    'report.png': _form_scene(
        'Formats',
        'Name and URL, Markdown, HTML, JSON',
        'SO0245 - Azure Interior',
        ['Name+URL', 'Markdown', 'HTML'],
    ),
    'mobile.png': _form_scene(
        'Mobile',
        'Stat buttons stay compact on small screens',
        'CopyLink Task',
        ['Copy Link', 'Share'],
    ),
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
        'hero.gif': ('workflow.png', 'dashboard.png', 'report.png'),
        'workflow.gif': ('workflow.png', 'report.png', 'mobile.png'),
        'dashboard.gif': ('dashboard.png', 'designer.png'),
        'settings.gif': ('settings.png', 'workflow.png'),
        'reports.gif': ('designer.png', 'report.png'),
        'mobile.gif': ('mobile.png', 'workflow.png'),
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
