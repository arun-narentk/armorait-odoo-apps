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
BLACK_BASE = '#081120'
NAVY_BLACK = '#0a1628'
NAVY_DEEP = '#0f172a'
TEAL_MAIN = '#0d9488'
TEAL_MID = '#14b8a6'
TEAL_LIGHT = '#2dd4bf'
TEAL_SHADOW = '#042f2e'
NAVY_SHADOW = '#0a1628'
CTA_START = '#6366f1'
CTA_MID = '#7c3aed'
CTA_END = '#0ea5e9'
TITLE_COLOR = WHITE
PANEL_GLOW = '#115e59'
TEAL_CYAN = '#06b6d4'
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


def _cta_gradient_rgb(t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    start, mid, end = _hex_to_rgb(CTA_START), _hex_to_rgb(CTA_MID), _hex_to_rgb(CTA_END)
    if t <= 0.42:
        return _lerp_rgb(start, mid, t / 0.42)
    return _lerp_rgb(mid, end, (t - 0.42) / 0.58)


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


def _build_teal_cover_background(w: int, h: int) -> Image.Image:
    """Solid teal field with navy shadow vignette (no diagonal split)."""
    panel = Image.new('RGB', (w, h))
    px = panel.load()
    teal = _hex_to_rgb(TEAL_MAIN)
    teal_mid = _hex_to_rgb(TEAL_MID)
    navy = _hex_to_rgb(NAVY_SHADOW)
    deep = _hex_to_rgb(TEAL_SHADOW)
    for y in range(h):
        ty = y / max(h - 1, 1)
        for x in range(w):
            tx = x / max(w - 1, 1)
            base = _lerp_rgb(teal_mid, teal, 0.35 + tx * 0.25)
            shadow = max((ty - 0.45) * 1.8, 0.0) * 0.55 + max((tx - 0.55) * 1.4, 0.0) * 0.35
            if shadow > 0:
                mix = _lerp_rgb(base, _lerp_rgb(navy, deep, ty * 0.6), min(1.0, shadow))
                px[x, y] = mix
            else:
                px[x, y] = base
    return panel


def _draw_cover_background(img: Image.Image, w: int, h: int) -> None:
    img.paste(_build_teal_cover_background(w, h), (0, 0))


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
    draw.text((x1 + pad_x, y1 + pad_y - 1), ODOO_VERSION_LABEL, font=label_font, fill='#1d4ed8')


def _draw_top_brand_mark(img: Image.Image, w: int, h: int, cover_logo: Path | None = None) -> None:
    """Compact ARMORA mark at top-left like Serpent logo placement."""
    logo_path = cover_logo or DEFAULT_COVER_LOGO
    mark_h = max(46, int(h * 0.085))
    mark = _load_cover_logo_mark(logo_path, mark_h)
    if mark is None:
        return
    pad_x, pad_y = 18, 14
    badge_w = mark.width + 16
    badge_h = mark.height + 10
    draw = ImageDraw.Draw(img)
    _rounded_rect(draw, (pad_x, pad_y, pad_x + badge_w, pad_y + badge_h), 8, NAVY_SHADOW)
    img.paste(mark, (pad_x + 8, pad_y + 5), mark)


def _draw_website_pill(img: Image.Image, w: int, h: int) -> None:
    """Website label for teal background."""
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
        outline=TEAL_LIGHT,
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
        color = _cta_gradient_rgb(x / max(width - 1, 1))
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


def _draw_cover_illustration(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int) -> None:
    glow_r = radius + 10
    draw.ellipse((cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r), fill=PANEL_GLOW)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=WHITE, outline=TEAL_LIGHT, width=4)
    inner = radius - 18
    draw.ellipse((cx - inner, cy - inner, cx + inner, cy + inner), fill='#ecfeff')
    bubble_w, bubble_h = int(radius * 1.05), int(radius * 0.72)
    bx1, by1 = cx - bubble_w // 2, cy - bubble_h // 2 - 8
    bx2, by2 = bx1 + bubble_w, by1 + bubble_h
    _rounded_rect(draw, (bx1, by1, bx2, by2), 18, WHITE, outline=TEAL_MAIN, width=3)
    for dot_x in (cx - 22, cx, cx + 22):
        draw.ellipse((dot_x - 7, cy - 10, dot_x + 7, cy + 4), fill=TEAL_MAIN)
    for sx, sy, color in (
        (cx - 58, cy - 48, TEAL_LIGHT),
        (cx + 62, cy - 36, TEAL_CYAN),
        (cx + 54, cy + 42, TEAL_MID),
    ):
        draw.ellipse((sx - 10, sy - 10, sx + 10, sy + 10), fill=color)
        draw.line((sx - 14, sy, sx + 14, sy), fill=WHITE, width=2)
        draw.line((sx, sy - 14, sx, sy + 14), fill=WHITE, width=2)
    bar_y = cy + bubble_h // 2 + 8
    for i, color in enumerate((TEAL_MAIN, TEAL_MID, TEAL_LIGHT)):
        draw.rounded_rectangle((cx - 36 + i * 26, bar_y, cx - 18 + i * 26, bar_y + 18), radius=4, fill=color)


def _draw_armorait_logo_badge(img: Image.Image, w: int, h: int, cover_logo: Path | None = None) -> None:
    """Bottom-center ARMORA mark on unified teal background."""
    logo_path = cover_logo or DEFAULT_COVER_LOGO
    pad_bottom = 14
    inner_h = max(82, int(h * 0.14))
    mark = _load_cover_logo_mark(logo_path, inner_h)
    if mark is None:
        return

    pad_x = 12
    badge_w = mark.width + pad_x * 2
    badge_h = mark.height + 10
    y = h - badge_h - pad_bottom
    x = max(14, (w - badge_w) // 2)

    draw = ImageDraw.Draw(img)
    _rounded_rect(draw, (x, y, x + badge_w, y + badge_h), max(8, badge_h // 8), NAVY_SHADOW)
    img.paste(mark, (x + pad_x, y + 5), mark)


def _paste_armorait_logo(img: Image.Image, w: int, h: int, cover_logo: Path | None = None) -> None:
    _draw_armorait_logo_badge(img, w, h, cover_logo=cover_logo)


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
    img = Image.new('RGB', (w, h), TEAL_MAIN)
    draw = ImageDraw.Draw(img)
    _draw_cover_background(img, w, h)
    _draw_top_brand_mark(img, w, h, cover_logo=logo_path)
    _draw_odoo_version_badge(img, w, h)
    radius = int(min(w, h) * 0.22)
    _draw_cover_illustration(draw, int(w * 0.28), int(h * 0.46), radius)

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
            fill='#ccfbf1',
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
