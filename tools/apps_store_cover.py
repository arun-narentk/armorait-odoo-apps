#!/usr/bin/env python3
"""Shared Apps Store loempia_app_cover banner generator for ARMORA modules."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    RESAMPLE = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
except AttributeError:
    RESAMPLE = getattr(Image, 'LANCZOS', Image.ANTIALIAS)

WHITE = '#FFFFFF'
NAVY_SHADOW = '#0a1628'
PEACOCK_TEAL = '#0d9488'
PEACOCK_TEAL_LIGHT = '#14b8a6'
PEACOCK_CYAN = '#06b6d4'
PEACOCK_BLUE = '#1d4ed8'
PEACOCK_BLUE_LIGHT = '#2563eb'
PEACOCK_INDIGO = '#1e3a8a'
PEACOCK_DEEP = '#042f2e'
PEACOCK_EMERALD = '#10b981'
TITLE_COLOR = WHITE
PANEL_GLOW = '#1e40af'
WEBSITE_PILL = 'www.armorait.com'

DEFAULT_BRAND_LOGO = (
    Path(__file__).resolve().parents[1]
    / 'rn_ai_employee'
    / 'static'
    / 'description'
    / 'armorait_brand_logo.png'
)
DEFAULT_COVER_LOGO = Path(__file__).resolve().parent / 'armorait_cover_logo.png'
LOGO_MARK_CROP = (0.16, 0.02, 0.84, 0.78)
LOGO_LEFT_CROP = (0.18, 0.02, 0.82, 0.56)


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


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _lerp_rgb(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _peacock_gradient_rgb(tx: float, ty: float) -> tuple[int, int, int]:
    """Teal-to-blue peacock blend with navy shadow toward bottom-right."""
    tx = max(0.0, min(1.0, tx))
    ty = max(0.0, min(1.0, ty))
    teal = _hex_to_rgb(PEACOCK_TEAL_LIGHT)
    blue = _hex_to_rgb(PEACOCK_BLUE_LIGHT)
    indigo = _hex_to_rgb(PEACOCK_INDIGO)
    navy = _hex_to_rgb(NAVY_SHADOW)
    deep = _hex_to_rgb(PEACOCK_DEEP)
    base = _lerp_rgb(teal, blue, tx ** 0.82)
    base = _lerp_rgb(base, _lerp_rgb(indigo, blue, 0.35), ty * 0.18)
    shadow = max((ty - 0.42) * 1.55, 0.0) * 0.48 + max((tx - 0.58) * 1.25, 0.0) * 0.32
    if shadow > 0:
        return _lerp_rgb(base, _lerp_rgb(navy, deep, ty * 0.65), min(1.0, shadow))
    return base


def _build_peacock_cover_background(w: int, h: int) -> Image.Image:
    """Unified peacock teal + blue field with navy shadow (no diagonal split)."""
    panel = Image.new('RGB', (w, h))
    px = panel.load()
    for y in range(h):
        ty = y / max(h - 1, 1)
        for x in range(w):
            tx = x / max(w - 1, 1)
            px[x, y] = _peacock_gradient_rgb(tx, ty)
    return panel


def _draw_cover_background(img: Image.Image, w: int, h: int) -> None:
    img.paste(_build_peacock_cover_background(w, h), (0, 0))


def title_lines_from_name(name: str) -> list[str]:
    """Split manifest app name into 1-2 uppercase cover title lines."""
    upper = re.sub(r'\s+', ' ', name.strip()).upper()
    for_odoo = re.search(r'\bFOR\s+ODOO\b', upper)
    if for_odoo:
        return [upper[:for_odoo.start()].strip(), upper[for_odoo.start():].strip()]
    words = upper.split()
    if len(words) <= 2:
        return [upper]
    if len(words) == 3:
        return [' '.join(words[:2]), words[2]]
    mid = (len(words) + 1) // 2
    return [' '.join(words[:mid]), ' '.join(words[mid:])]


def subtitle_lines_from_summary(
    summary: str,
    max_lines: int = 2,
    max_chars: int = 46,
) -> list[str]:
    """Wrap manifest summary into 1-2 readable lines (no mid-phrase comma cuts)."""
    text = re.sub(r'\s+', ' ', summary.strip())
    if not text:
        return ['']

    if len(text) <= max_chars:
        return [text]

    if ':' in text:
        head, tail = text.split(':', 1)
        line1 = f'{head.strip()}:'
        line2 = tail.strip()
        if line1 and line2 and len(line1) <= max_chars:
            if len(line2) > max_chars:
                cut = line2[: max_chars - 1].rsplit(' ', 1)[0]
                line2 = cut.rstrip(',:;') if cut else line2[:max_chars]
            return [line1, line2][:max_lines]

    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = ' '.join(current + [word])
        if len(trial) <= max_chars or not current:
            current.append(word)
            continue
        lines.append(' '.join(current))
        current = [word]
        if len(lines) >= max_lines:
            break
    if len(lines) < max_lines and current:
        lines.append(' '.join(current))
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if lines:
        last = lines[-1].rstrip(',:;')
        if last != lines[-1]:
            lines[-1] = last
        return lines
    return [text[:max_chars].rsplit(' ', 1)[0].rstrip(',:;')]


def subtitle_from_summary(summary: str, max_len: int = 52) -> str:
    """Single-line subtitle helper (legacy callers)."""
    return subtitle_lines_from_summary(summary, max_lines=1, max_chars=max_len)[0]


def read_manifest_fields(manifest_path: Path) -> tuple[str, str]:
    text = manifest_path.read_text(encoding='utf-8')
    name_match = re.search(r"'name'\s*:\s*'((?:\\'|[^'])*)'", text)
    summary_match = re.search(r"'summary'\s*:\s*'((?:\\'|[^'])*)'", text)
    name = name_match.group(1).replace("\\'", "'") if name_match else manifest_path.parent.name
    summary = summary_match.group(1).replace("\\'", "'") if summary_match else name
    return name, summary


DEFAULT_BRAND_STRIP = DEFAULT_BRAND_LOGO
ODOO_VERSION_LABEL = 'V19'


def _load_cover_logo_mark(cover_logo: Path, target_h: int) -> Image.Image | None:
    """Crop and scale the 3D ARMORA mark (icon + wordmark) for the cover badge."""
    if not cover_logo.is_file():
        return None
    source = Image.open(cover_logo).convert('RGBA')
    sw, sh = source.size
    left, top, right, bottom = LOGO_MARK_CROP
    mark = source.crop((int(sw * left), int(sh * top), int(sw * right), int(sh * bottom)))
    target_w = max(1, int(mark.width * (target_h / mark.height)))
    return mark.resize((target_w, target_h), RESAMPLE)


def _load_cover_logo_left(cover_logo: Path, max_size: int) -> Image.Image | None:
    """Crop ARMORA puzzle icon + wordmark for the left disc panel."""
    if not cover_logo.is_file():
        return None
    source = Image.open(cover_logo).convert('RGBA')
    sw, sh = source.size
    left, top, right, bottom = LOGO_LEFT_CROP
    mark = source.crop((int(sw * left), int(sh * top), int(sw * right), int(sh * bottom)))
    scale = min(max_size / max(mark.width, 1), max_size / max(mark.height, 1))
    target_w = max(1, int(mark.width * scale))
    target_h = max(1, int(mark.height * scale))
    return mark.resize((target_w, target_h), RESAMPLE)


def _draw_odoo_version_badge(img: Image.Image, w: int, h: int) -> None:
    """Top-right Odoo 19 version tag (Serpent-style ribbon)."""
    draw = ImageDraw.Draw(img)
    label_font = _font(max(16, int(h * 0.036)), True)
    lw, lh = _text_size(draw, ODOO_VERSION_LABEL, label_font)
    pad_x, pad_y = 16, 8
    box_w = lw + pad_x * 2
    box_h = lh + pad_y * 2
    x2 = w - 18
    x1 = x2 - box_w
    y1 = 16
    y2 = y1 + box_h
    _rounded_rect(draw, (x1, y1, x2, y2), 6, WHITE)
    draw.text((x1 + pad_x, y1 + pad_y - 1), ODOO_VERSION_LABEL, font=label_font, fill=PEACOCK_BLUE)


def _draw_left_logo_disc(
    img: Image.Image,
    w: int,
    h: int,
    cover_logo: Path | None = None,
) -> None:
    """loempia_app_cover shadow-sm left panel with the ARMORA 3D logo."""
    logo_path = cover_logo or DEFAULT_COVER_LOGO
    cx = int(w * 0.28)
    cy = int(h * 0.48)
    radius = int(min(w, h) * 0.22)
    inner = radius - 16

    shadow_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    for offset, alpha in ((6, 42), (10, 24), (14, 12)):
        shadow_draw.ellipse(
            (cx - radius + offset, cy - radius + offset + 3, cx + radius + offset, cy + radius + offset + 3),
            fill=(8, 18, 38, alpha),
        )
    img.paste(shadow_layer, (0, 0), shadow_layer)

    draw = ImageDraw.Draw(img)
    draw.ellipse((cx - radius - 3, cy - radius - 3, cx + radius + 3, cy + radius + 3), fill=PANEL_GLOW)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=WHITE, outline=PEACOCK_CYAN, width=4)
    draw.ellipse((cx - inner, cy - inner, cx + inner, cy + inner), fill='#e0f2fe')

    mark = _load_cover_logo_left(logo_path, inner * 2 - 20)
    if mark is not None:
        img.paste(mark, (cx - mark.width // 2, cy - mark.height // 2), mark)


def _draw_website_pill(img: Image.Image, w: int, h: int) -> None:
    """Website label on peacock background."""
    draw = ImageDraw.Draw(img)
    pill_font = _font(max(14, int(h * 0.024)), True)
    tw, th = _text_size(draw, WEBSITE_PILL, pill_font)
    pad_x, pad_y = 16, 8
    pill_w = tw + pad_x * 2
    pill_h = th + pad_y * 2
    pill_x = w - pill_w - 22
    pill_y = 62
    _rounded_rect(
        draw,
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        max(8, pill_h // 2),
        NAVY_SHADOW,
        outline=PEACOCK_CYAN,
        width=2,
    )
    draw.text(
        (pill_x + pad_x, pill_y + (pill_h - th) // 2 - 1),
        WEBSITE_PILL,
        font=pill_font,
        fill=WHITE,
    )


def _draw_gradient_rounded_rect(
    img: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
    text: str,
    font,
    text_color: str = WHITE,
    text_x_offset: int | None = None,
) -> None:
    x1, y1, x2, y2 = box
    width = max(2, x2 - x1)
    height = max(2, y2 - y1)
    grad = Image.new('RGB', (width, height))
    px = grad.load()
    for x in range(width):
        color = _peacock_gradient_rgb(x / max(width - 1, 1), 0.35)
        for y in range(height):
            px[x, y] = color
    mask = Image.new('L', (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
    img.paste(grad, (x1, y1), mask)
    draw = ImageDraw.Draw(img)
    tw, th = _text_size(draw, text, font)
    tx = x1 + (text_x_offset if text_x_offset is not None else (width - tw) // 2)
    ty = y1 + (height - th) // 2 - 1
    draw.text((tx, ty), text, font=font, fill=text_color)


def _draw_centered_title_block(
    draw: ImageDraw.ImageDraw,
    left: int,
    right: int,
    y: int,
    lines: list[str],
) -> int:
    cy = y
    for line in lines:
        font = _font(48, True)
        max_w = right - left - 24
        tw, th = _text_size(draw, line, font)
        while tw > max_w and (not hasattr(font, 'size') or font.size > 28):
            size = font.size - 2 if hasattr(font, 'size') else 38
            font = _font(size, True)
            tw, th = _text_size(draw, line, font)
        x = left + (right - left - tw) // 2
        draw.text((x, cy), line, font=font, fill=TITLE_COLOR)
        cy += th + 6
    return cy


def draw_app_cover(
    title_lines: list[str],
    subtitle: str | list[str],
    w: int = 1200,
    h: int = 600,
    brand_logo: Path | None = None,
    cover_logo: Path | None = None,
) -> Image.Image:
    """Render loempia_app_cover style banner for one module."""
    logo_path = cover_logo or DEFAULT_COVER_LOGO
    subtitle_lines = subtitle if isinstance(subtitle, list) else [subtitle]
    img = Image.new('RGB', (w, h), PEACOCK_TEAL)
    draw = ImageDraw.Draw(img)
    _draw_cover_background(img, w, h)
    _draw_odoo_version_badge(img, w, h)
    _draw_left_logo_disc(img, w, h, cover_logo=logo_path)

    content_left = int(w * 0.50)
    content_right = w - 32
    content_w = content_right - content_left

    sub_font = _font(16)
    sub_line_h = _text_size(draw, 'Ag', sub_font)[1] + 4
    title_block_h = 0
    for line in title_lines:
        font = _font(48, True)
        tw, th = _text_size(draw, line, font)
        while tw > content_w and (not hasattr(font, 'size') or font.size > 28):
            size = font.size - 2 if hasattr(font, 'size') else 38
            font = _font(size, True)
            tw, th = _text_size(draw, line, font)
        title_block_h += th + 6
    subtitle_block_h = len(subtitle_lines) * sub_line_h
    block_h = title_block_h + 12 + subtitle_block_h
    title_y = max(96, int((h - block_h) * 0.40))
    title_end_y = _draw_centered_title_block(draw, content_left, content_right, title_y, title_lines)

    sub_y = title_end_y + 10
    for line in subtitle_lines:
        stw, sth = _text_size(draw, line, sub_font)
        draw.text(
            (content_left + (content_w - stw) // 2, sub_y),
            line,
            font=sub_font,
            fill='#dbeafe',
        )
        sub_y += sub_line_h

    _draw_website_pill(img, w, h)
    return img


def save_cover_assets(
    module_dir: Path,
    title_lines: list[str],
    subtitle: str | list[str],
    cover_logo: Path | None = None,
) -> None:
    """Write banner.png, banner_small.png, and cover logo into module static/description."""
    out = module_dir / 'static' / 'description'
    out.mkdir(parents=True, exist_ok=True)
    logo_src = cover_logo or DEFAULT_COVER_LOGO
    if logo_src.is_file():
        dest = out / 'armorait_cover_logo.png'
        if logo_src.resolve() != dest.resolve():
            shutil.copy2(logo_src, dest)
    banner = draw_app_cover(title_lines, subtitle, cover_logo=logo_src)
    banner.save(out / 'banner.png', 'PNG', optimize=True)
    banner.resize((360, 180), RESAMPLE).save(out / 'banner_small.png', 'PNG', optimize=True)


def generate_covers_for_repo(repo_root: Path, cover_logo: Path | None = None) -> list[str]:
    """Generate covers for every Odoo module folder under repo_root."""
    generated: list[str] = []
    skip = {'tools', 'armorait2_site', '.git', '.github', '.tmp'}
    for manifest in sorted(repo_root.glob('*/__manifest__.py')):
        module_dir = manifest.parent
        if module_dir.name in skip:
            continue
        name, summary = read_manifest_fields(manifest)
        title_lines = title_lines_from_name(name)
        subtitle = subtitle_lines_from_summary(summary)
        save_cover_assets(module_dir, title_lines, subtitle, cover_logo=cover_logo)
        generated.append(module_dir.name)
    return generated
