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
CTA_START = '#6366f1'
CTA_MID = '#7c3aed'
CTA_END = '#0ea5e9'
TITLE_INDIGO = '#4f46e5'
PANEL_GLOW = '#312e81'
TEAL_CYAN = '#06b6d4'
WEBSITE_PILL = 'www.armorait.com'

DEFAULT_BRAND_LOGO = (
    Path(__file__).resolve().parents[1]
    / 'rn_ai_employee'
    / 'static'
    / 'description'
    / 'armorait_brand_logo.png'
)


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


def subtitle_from_summary(summary: str, max_len: int = 52) -> str:
    text = re.sub(r'\s+', ' ', summary.strip())
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(' ', 1)[0]
    return cut or text[:max_len]


def read_manifest_fields(manifest_path: Path) -> tuple[str, str]:
    text = manifest_path.read_text(encoding='utf-8')
    name_match = re.search(r"'name'\s*:\s*'((?:\\'|[^'])*)'", text)
    summary_match = re.search(r"'summary'\s*:\s*'((?:\\'|[^'])*)'", text)
    name = name_match.group(1).replace("\\'", "'") if name_match else manifest_path.parent.name
    summary = summary_match.group(1).replace("\\'", "'") if summary_match else name
    return name, summary


def _build_rich_panel_gradient(w: int, h: int) -> Image.Image:
    panel = Image.new('RGB', (w, h))
    px = panel.load()
    black = _hex_to_rgb(BLACK_BASE)
    navy = _hex_to_rgb(NAVY_BLACK)
    deep = _hex_to_rgb(NAVY_DEEP)
    for y in range(h):
        ty = y / max(h - 1, 1)
        for x in range(w):
            tx = x / max(w - 1, 1)
            glow_t = min(1.0, tx * 0.72 + (1.0 - ty) * 0.28)
            glow = _cta_gradient_rgb(glow_t)
            base = _lerp_rgb(black, _lerp_rgb(navy, deep, ty * 0.55), 0.25)
            shade = 0.56 if tx < 0.55 else 0.70
            color = tuple(int(base[i] * shade + glow[i] * (1.0 - shade)) for i in range(3))
            px[x, y] = color
    return panel


def _draw_diagonal_cover_background(img: Image.Image, w: int, h: int) -> int:
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, h), fill='#F8FAFC')
    split_top = int(w * 0.54)
    split_bottom = int(w * 0.34)
    panel = _build_rich_panel_gradient(w, h)
    mask = Image.new('L', (w, h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon([(0, 0), (split_top, 0), (split_bottom, h), (0, h)], fill=255)
    img.paste(panel, (0, 0), mask)
    glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.polygon([(0, 0), (split_top, 0), (split_bottom, h), (0, h)], fill=(99, 102, 241, 32))
    img.paste(glow, (0, 0), glow)
    return (split_top + split_bottom) // 2


def _draw_gradient_rounded_rect(
    img: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
    text: str,
    font,
    text_color: str = WHITE,
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
    tx = x1 + (width - tw) // 2
    ty = y1 + (height - th) // 2
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
        draw.text((x, cy), line, font=font, fill=TITLE_INDIGO)
        cy += th + 6
    return cy


def _draw_cover_illustration(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int) -> None:
    glow_r = radius + 10
    draw.ellipse((cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r), fill=PANEL_GLOW)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill='#F8FAFC', outline='#C7D2FE', width=4)
    inner = radius - 18
    draw.ellipse((cx - inner, cy - inner, cx + inner, cy + inner), fill='#EEF2FF')
    bubble_w, bubble_h = int(radius * 1.05), int(radius * 0.72)
    bx1, by1 = cx - bubble_w // 2, cy - bubble_h // 2 - 8
    bx2, by2 = bx1 + bubble_w, by1 + bubble_h
    _rounded_rect(draw, (bx1, by1, bx2, by2), 18, WHITE, outline=CTA_START, width=3)
    for dot_x in (cx - 22, cx, cx + 22):
        draw.ellipse((dot_x - 7, cy - 10, dot_x + 7, cy + 4), fill=CTA_MID)
    for sx, sy, color in (
        (cx - 58, cy - 48, CTA_END),
        (cx + 62, cy - 36, TEAL_CYAN),
        (cx + 54, cy + 42, CTA_MID),
    ):
        draw.ellipse((sx - 10, sy - 10, sx + 10, sy + 10), fill=color)
        draw.line((sx - 14, sy, sx + 14, sy), fill=WHITE, width=2)
        draw.line((sx, sy - 14, sx, sy + 14), fill=WHITE, width=2)
    bar_y = cy + bubble_h // 2 + 8
    for i, color in enumerate((CTA_START, CTA_MID, CTA_END)):
        draw.rounded_rectangle((cx - 36 + i * 26, bar_y, cx - 18 + i * 26, bar_y + 18), radius=4, fill=color)


def _diagonal_split_x(w: int, h: int, y: int) -> int:
    split_top = int(w * 0.54)
    split_bottom = int(w * 0.34)
    if h <= 0:
        return split_bottom
    return split_top + int((split_bottom - split_top) * (y / h))


def _draw_armorait_logo_badge(img: Image.Image, w: int, h: int) -> None:
    """Draw high-contrast ARMORA badge (IT TECHNOLOGIES readable on dark bar)."""
    draw = ImageDraw.Draw(img)
    pad_bottom = 16
    badge_h = max(92, int(h * 0.22))
    icon_size = int(badge_h * 0.46)
    badge_w = int(badge_h * 3.15)

    y = h - badge_h - pad_bottom
    split_x = _diagonal_split_x(w, h, y + badge_h // 2)
    x = split_x + max(16, (w - split_x - badge_w) // 2)
    x = min(x, w - badge_w - 16)

    _rounded_rect(draw, (x, y, x + badge_w, y + badge_h), max(10, badge_h // 8), '#0a1628')

    ix = x + int(badge_h * 0.20)
    iy = y + (badge_h - icon_size) // 2
    half = icon_size // 2
    draw.polygon([(ix, iy + icon_size), (ix + half, iy), (ix + half, iy + icon_size)], fill=CTA_MID)
    draw.polygon([(ix + half, iy), (ix + icon_size, iy + icon_size), (ix + half, iy + icon_size)], fill=WHITE)

    tx = ix + icon_size + int(badge_h * 0.16)
    armora_font = _font(max(22, int(badge_h * 0.34)), True)
    sub_font = _font(max(11, int(badge_h * 0.145)), True)
    draw.text((tx, y + int(badge_h * 0.22)), 'ARMORA', font=armora_font, fill=WHITE)
    draw.text((tx, y + int(badge_h * 0.56)), 'IT TECHNOLOGIES', font=sub_font, fill='#E2E8F0')


def _paste_armorait_logo(img: Image.Image, w: int, h: int, brand_logo: Path | None = None) -> None:
    """Draw ARMORA logo badge on cover (vector, not low-contrast PNG)."""
    _draw_armorait_logo_badge(img, w, h)


def draw_app_cover(
    title_lines: list[str],
    subtitle: str,
    w: int = 1200,
    h: int = 600,
    brand_logo: Path | None = None,
) -> Image.Image:
    """Render loempia_app_cover style banner for one module."""
    logo_path = brand_logo or DEFAULT_BRAND_LOGO
    img = Image.new('RGB', (w, h), '#F8FAFC')
    draw = ImageDraw.Draw(img)
    split_mid = _draw_diagonal_cover_background(img, w, h)
    radius = int(min(w, h) * 0.24)
    _draw_cover_illustration(draw, int(w * 0.27), h // 2, radius)
    _paste_armorait_logo(img, w, h)

    panel_left = split_mid - 20
    title_y = int(h * 0.26)
    _draw_centered_title_block(draw, panel_left, w - 24, title_y, title_lines)

    sub_font = _font(17)
    stw, sth = _text_size(draw, subtitle, sub_font)
    draw.text(
        (panel_left + (w - 24 - panel_left - stw) // 2, int(h * 0.58)),
        subtitle,
        font=sub_font,
        fill='#475569',
    )

    pill_font = _font(13, True)
    tw, th = _text_size(draw, WEBSITE_PILL, pill_font)
    pill_w = tw + 36
    pill_h = th + 16
    pill_x = w - pill_w - 24
    pill_y = 20
    _draw_gradient_rounded_rect(
        img,
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        pill_h // 2,
        WEBSITE_PILL,
        pill_font,
    )
    return img


def save_cover_assets(
    module_dir: Path,
    title_lines: list[str],
    subtitle: str,
    brand_logo: Path | None = None,
) -> None:
    """Write banner.png, banner_small.png, and brand logo into module static/description."""
    out = module_dir / 'static' / 'description'
    out.mkdir(parents=True, exist_ok=True)
    logo_src = brand_logo or DEFAULT_BRAND_LOGO
    if logo_src.is_file():
        dest = out / 'armorait_brand_logo.png'
        if logo_src.resolve() != dest.resolve():
            shutil.copy2(logo_src, dest)
    banner = draw_app_cover(title_lines, subtitle)
    banner.save(out / 'banner.png', 'PNG', optimize=True)
    banner.resize((360, 180), RESAMPLE).save(out / 'banner_small.png', 'PNG', optimize=True)


def generate_covers_for_repo(repo_root: Path, brand_logo: Path | None = None) -> list[str]:
    """Generate covers for every Odoo module folder under repo_root."""
    generated: list[str] = []
    skip = {'tools', 'armorait2_site', '.git', '.github', '.tmp'}
    for manifest in sorted(repo_root.glob('*/__manifest__.py')):
        module_dir = manifest.parent
        if module_dir.name in skip:
            continue
        name, summary = read_manifest_fields(manifest)
        title_lines = title_lines_from_name(name)
        subtitle = subtitle_from_summary(summary)
        save_cover_assets(module_dir, title_lines, subtitle, brand_logo=brand_logo)
        generated.append(module_dir.name)
    return generated
