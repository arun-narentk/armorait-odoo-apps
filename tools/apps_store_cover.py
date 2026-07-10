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


DEFAULT_BRAND_STRIP = DEFAULT_BRAND_LOGO
ICON_CROP_RATIO = 0.14
ODOO_VERSION_LABEL = 'V19'


def _is_brand_mark_pixel(r: int, g: int, b: int, a: int) -> bool:
    """Keep only purple/white logo strokes from the brand strip."""
    if a < 20:
        return False
    if r > 185 and g > 185 and b > 185:
        return True
    return r > 75 and b > 75 and g < 145


def _clean_brand_icon(icon: Image.Image) -> Image.Image:
    """Remove dark strip background so only the A mark remains."""
    cleaned = icon.copy()
    px = cleaned.load()
    for y in range(cleaned.height):
        for x in range(cleaned.width):
            r, g, b, a = px[x, y]
            if _is_brand_mark_pixel(r, g, b, a):
                continue
            px[x, y] = (0, 0, 0, 0)
    return cleaned


def _trim_brand_icon(icon: Image.Image) -> Image.Image:
    """Trim transparent margins around the logo mark."""
    px = icon.load()
    xs: list[int] = []
    ys: list[int] = []
    for y in range(icon.height):
        for x in range(icon.width):
            if px[x, y][3] > 20:
                xs.append(x)
                ys.append(y)
    if not xs:
        return icon
    return icon.crop((min(xs), min(ys), max(xs) + 1, max(ys) + 1))


def _extract_brand_icon(brand_logo: Path, target_h: int) -> Image.Image | None:
    """Crop original ARMORA A mark from brand strip (old design icon)."""
    if not brand_logo.is_file():
        return None
    strip = Image.open(brand_logo).convert('RGBA')
    crop_w = max(1, int(strip.width * ICON_CROP_RATIO))
    icon = _trim_brand_icon(_clean_brand_icon(strip.crop((0, 0, crop_w, strip.height))))
    target_w = max(1, int(icon.width * (target_h / icon.height)))
    return icon.resize((target_w, target_h), RESAMPLE)


def _draw_odoo_version_badge(img: Image.Image, w: int, h: int) -> None:
    """Top-left Odoo 19 version tag on the gradient panel."""
    draw = ImageDraw.Draw(img)
    label_font = _font(max(15, int(h * 0.034)), True)
    hint_font = _font(max(9, int(h * 0.018)), True)
    lw, lh = _text_size(draw, ODOO_VERSION_LABEL, label_font)
    hw, hh = _text_size(draw, 'Odoo 19', hint_font)
    inner_w = max(lw, hw)
    pad_x, pad_y = 14, 10
    box_w = inner_w + pad_x * 2
    box_h = lh + hh + pad_y * 2 + 4
    x1, y1 = 18, 16
    x2, y2 = x1 + box_w, y1 + box_h
    _rounded_rect(draw, (x1, y1, x2, y2), 10, '#0a1628', outline='#C7D2FE', width=2)
    draw.text((x1 + (box_w - lw) // 2, y1 + pad_y - 1), ODOO_VERSION_LABEL, font=label_font, fill=WHITE)
    draw.text((x1 + (box_w - hw) // 2, y1 + pad_y + lh + 2), 'Odoo 19', font=hint_font, fill='#CBD5E1')


def _draw_website_pill(img: Image.Image, w: int, h: int, panel_left: int) -> None:
    """Clean website label aligned to the white content column."""
    draw = ImageDraw.Draw(img)
    pill_font = _font(max(15, int(h * 0.026)), True)
    tw, th = _text_size(draw, WEBSITE_PILL, pill_font)
    pad_x, pad_y = 18, 9
    pill_w = tw + pad_x * 2
    pill_h = th + pad_y * 2
    content_right = w - 28
    pill_x = content_right - pill_w
    pill_y = 22
    _rounded_rect(
        draw,
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        max(8, pill_h // 2),
        '#EEF2FF',
        outline=CTA_START,
        width=2,
    )
    draw.text(
        (pill_x + pad_x, pill_y + (pill_h - th) // 2 - 1),
        WEBSITE_PILL,
        font=pill_font,
        fill=CTA_MID,
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


def _draw_armorait_logo_badge(img: Image.Image, w: int, h: int, brand_logo: Path | None = None) -> None:
    """ARMORA badge: original A icon + readable vector text."""
    draw = ImageDraw.Draw(img)
    logo_path = brand_logo or DEFAULT_BRAND_LOGO
    pad_bottom = 20
    badge_h = max(76, int(h * 0.15))
    icon_size = int(badge_h * 0.84)
    badge_w = int(badge_h * 2.88)

    y = h - badge_h - pad_bottom
    split_x = _diagonal_split_x(w, h, y + badge_h // 2)
    x = split_x + max(20, (w - split_x - badge_w) // 2)
    x = min(x, w - badge_w - 20)

    _rounded_rect(draw, (x, y, x + badge_w, y + badge_h), max(8, badge_h // 7), '#0a1628')

    icon = _extract_brand_icon(logo_path, icon_size)
    ix = x + int(badge_h * 0.12)
    iy = y + (badge_h - icon_size) // 2
    if icon is not None:
        img.paste(icon, (ix, iy), icon)
        tx = ix + icon_size + int(badge_h * 0.08)
    else:
        tx = x + int(badge_h * 0.18)

    armora_font = _font(max(18, int(badge_h * 0.36)), True)
    sub_font = _font(max(9, int(badge_h * 0.16)), True)
    draw.text((tx, y + int(badge_h * 0.20)), 'ARMORA', font=armora_font, fill=WHITE)
    draw.text((tx, y + int(badge_h * 0.54)), 'IT TECHNOLOGIES', font=sub_font, fill='#E2E8F0')


def _paste_armorait_logo(img: Image.Image, w: int, h: int, brand_logo: Path | None = None) -> None:
    _draw_armorait_logo_badge(img, w, h, brand_logo=brand_logo)


def draw_app_cover(
    title_lines: list[str],
    subtitle: str | list[str],
    w: int = 1200,
    h: int = 600,
    brand_logo: Path | None = None,
) -> Image.Image:
    """Render loempia_app_cover style banner for one module."""
    logo_path = brand_logo or DEFAULT_BRAND_LOGO
    subtitle_lines = subtitle if isinstance(subtitle, list) else [subtitle]
    img = Image.new('RGB', (w, h), '#F8FAFC')
    draw = ImageDraw.Draw(img)
    split_mid = _draw_diagonal_cover_background(img, w, h)
    _draw_odoo_version_badge(img, w, h)
    radius = int(min(w, h) * 0.24)
    _draw_cover_illustration(draw, int(w * 0.27), h // 2, radius)
    _paste_armorait_logo(img, w, h, brand_logo=logo_path)

    content_left = split_mid + 8
    content_right = w - 28
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
    title_y = max(72, int((h - block_h) * 0.42))
    title_end_y = _draw_centered_title_block(draw, content_left, content_right, title_y, title_lines)

    sub_y = title_end_y + 10
    for line in subtitle_lines:
        stw, sth = _text_size(draw, line, sub_font)
        draw.text(
            (content_left + (content_w - stw) // 2, sub_y),
            line,
            font=sub_font,
            fill='#475569',
        )
        sub_y += sub_line_h

    _draw_website_pill(img, w, h, content_left)
    return img


def save_cover_assets(
    module_dir: Path,
    title_lines: list[str],
    subtitle: str | list[str],
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
        subtitle = subtitle_lines_from_summary(summary)
        save_cover_assets(module_dir, title_lines, subtitle, brand_logo=brand_logo)
        generated.append(module_dir.name)
    return generated
