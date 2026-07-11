#!/usr/bin/env python3
"""Shared Apps Store loempia_app_cover banner generator for ARMORA modules."""

from __future__ import annotations

import math
import re
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from module_app_icon import draw_module_icon, module_icon_for_disc, ImageFont

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
WEBSITE_URL = 'https://www.armorait.com/'

DEFAULT_BRAND_LOGO = Path(__file__).resolve().parent / 'armorait_brand_logo.png'
DEFAULT_COVER_LOGO = Path(__file__).resolve().parent / 'armorait_cover_logo.png'
LOGO_MARK_CROP = (0.16, 0.02, 0.84, 0.78)
LOGO_LEFT_CROP = (0.18, 0.02, 0.82, 0.56)
COVER_GIF_FRAMES = 18
COVER_GIF_FRAME_MS = 90
COVER_STATIC_DISC_PHASE = 0.70
SHIMMER_BASE = (229, 231, 235, 255)
SHIMMER_BAR = (209, 213, 219, 210)
SHIMMER_BAND = (255, 255, 255, 165)

_BACKGROUND_CACHE: dict[tuple[int, int], Image.Image] = {}


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


def _ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def _apply_alpha_rgba(image: Image.Image, alpha: float) -> Image.Image:
    """Scale overall alpha of an RGBA image."""
    if alpha >= 1.0:
        return image
    out = image.convert('RGBA')
    if alpha <= 0.0:
        return Image.new('RGBA', out.size, (0, 0, 0, 0))
    r, g, b, a = out.split()
    a = a.point(lambda value: int(value * alpha))
    out.putalpha(a)
    return out


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
    key = (w, h)
    cached = _BACKGROUND_CACHE.get(key)
    if cached is not None:
        return cached.copy()
    panel = Image.new('RGB', (w, h))
    px = panel.load()
    for y in range(h):
        ty = y / max(h - 1, 1)
        for x in range(w):
            tx = x / max(w - 1, 1)
            px[x, y] = _peacock_gradient_rgb(tx, ty)
    _BACKGROUND_CACHE[key] = panel
    return panel.copy()


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


def _trim_brand_logo_underline(source: Image.Image) -> Image.Image:
    """Drop the bottom white decorative strip from armorait_brand_logo.png."""
    img = source.convert('RGBA')
    w, h = img.size
    if h < 8:
        return img
    pixels = img.load()
    cutoff = h
    for y in range(h - 1, -1, -1):
        bright = sum(
            1 for x in range(w)
            if pixels[x, y][3] > 32
            and pixels[x, y][0] > 200
            and pixels[x, y][1] > 200
            and pixels[x, y][2] > 200
        )
        if bright >= w * 0.55:
            cutoff = y
            continue
        break
    if cutoff < h:
        cutoff = max(1, cutoff - 1)
        img = img.crop((0, 0, w, cutoff))
    return img


def _load_brand_logo_for_badge(logo_path: Path, target_h: int) -> Image.Image | None:
    """Load ARMORA wordmark for the bottom-right badge without the white underline."""
    if not logo_path.is_file():
        return None
    source = _trim_brand_logo_underline(Image.open(logo_path))
    scale = target_h / max(source.height, 1)
    target_w = max(1, int(source.width * scale))
    return source.resize((target_w, target_h), RESAMPLE)


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


def _disc_geometry(w: int, h: int) -> tuple[int, int, int, int]:
    """Center, outer radius, and inner radius for the left cover disc."""
    cx = int(w * 0.28)
    cy = int(h * 0.48)
    radius = int(min(w, h) * 0.22)
    inner = radius - 16
    return cx, cy, radius, inner


def _draw_disc_shell(img: Image.Image, w: int, h: int) -> tuple[int, int, int, int]:
    """Shadow-sm rings around the left disc. Returns cx, cy, radius, inner."""
    cx, cy, radius, inner = _disc_geometry(w, h)

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
    return cx, cy, radius, inner


def _make_shimmer_tile(size: int, sweep_phase: float) -> Image.Image:
    """POS self-order style grey skeleton tile with a moving shimmer band."""
    size = max(32, size)
    corner = max(8, size // 10)
    tile = Image.new('RGBA', (size, size), SHIMMER_BASE)
    draw = ImageDraw.Draw(tile)

    bar_h = max(4, size // 12)
    for index, y_frac in enumerate((0.34, 0.50, 0.66)):
        y = int(size * y_frac)
        bar_w = int(size * (0.58 - index * 0.07))
        x1 = (size - bar_w) // 2
        draw.rounded_rectangle((x1, y, x1 + bar_w, y + bar_h), radius=2, fill=SHIMMER_BAR)

    shimmer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    shimmer_draw = ImageDraw.Draw(shimmer)
    band_w = max(size // 3, 28)
    sweep = max(0.0, min(1.0, sweep_phase))
    x = int((size + band_w * 2) * sweep) - band_w
    shimmer_draw.rectangle((x, 0, x + band_w, size), fill=SHIMMER_BAND)
    tile = Image.alpha_composite(tile, shimmer)

    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=corner, fill=255)
    tile.putalpha(mask)
    return tile


def _disc_animation_state(
    phase: float,
) -> tuple[float, float, float, float]:
    """
    Map loop phase 0..1 to shimmer sweep, shimmer alpha, logo alpha, logo scale.

    Mimics POS self-order product thumbnails: skeleton shimmer, then fade-in.
    """
    phase = max(0.0, min(1.0, phase))
    if phase < 0.28:
        local = phase / 0.28
        return (local * 1.35) % 1.0, 1.0, 0.0, 0.95
    if phase < 0.52:
        local = (phase - 0.28) / 0.24
        eased = _ease_out_cubic(local)
        return 1.0, 1.0 - eased, eased, 0.95 + 0.05 * eased
    if phase < 0.88:
        local = (phase - 0.52) / 0.36
        pulse = 1.0 + 0.012 * math.sin(local * math.pi * 2)
        return 0.0, 0.0, 1.0, pulse
    local = (phase - 0.88) / 0.12
    eased = _ease_out_cubic(local)
    return eased * 0.4, eased, 1.0 - eased, 1.0


def _draw_disc_content(
    img: Image.Image,
    w: int,
    h: int,
    disc_phase: float,
    module_mark: Image.Image | None = None,
) -> None:
    """Shimmer placeholder and module icon reveal inside an existing disc shell."""
    cx, cy, _, inner = _disc_geometry(w, h)
    tile_size = inner * 2 - 24

    sweep, shimmer_alpha, logo_alpha, logo_scale = _disc_animation_state(disc_phase)

    if shimmer_alpha > 0.01:
        shimmer = _make_shimmer_tile(tile_size, sweep)
        shimmer = _apply_alpha_rgba(shimmer, shimmer_alpha)
        img.paste(shimmer, (cx - tile_size // 2, cy - tile_size // 2), shimmer)

    if logo_alpha > 0.01 and module_mark is not None:
        mark = module_mark
        if logo_scale != 1.0 and abs(logo_scale - 1.0) > 0.005:
            target_w = max(1, int(mark.width * logo_scale))
            target_h = max(1, int(mark.height * logo_scale))
            mark = mark.resize((target_w, target_h), RESAMPLE)
        faded = _apply_alpha_rgba(mark, logo_alpha)
        img.paste(faded, (cx - faded.width // 2, cy - faded.height // 2), faded)


def _draw_left_logo_disc(
    img: Image.Image,
    w: int,
    h: int,
    disc_phase: float = COVER_STATIC_DISC_PHASE,
    module_mark: Image.Image | None = None,
    shell_only: bool = False,
) -> None:
    """loempia_app_cover shadow-sm left panel with shimmer-to-module-icon reveal."""
    _draw_disc_shell(img, w, h)
    if not shell_only:
        _draw_disc_content(img, w, h, disc_phase, module_mark=module_mark)


def _draw_website_pill(img: Image.Image, w: int, h: int) -> None:
    """Website label in the top-right corner."""
    draw = ImageDraw.Draw(img)
    pill_font = _font(max(12, int(h * 0.022)), True)
    tw, th = _text_size(draw, WEBSITE_PILL, pill_font)
    pad_x, pad_y = 14, 7
    pill_w = tw + pad_x * 2
    pill_h = th + pad_y * 2
    pill_x = w - pill_w - 18
    pill_y = 16
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


def _draw_company_logo_badge(
    img: Image.Image,
    w: int,
    h: int,
    brand_logo: Path | None = None,
) -> None:
    """Bottom-right ARMORA company logo strip on every loempia_app_cover."""
    logo_path = brand_logo or DEFAULT_BRAND_LOGO
    target_h = max(40, int(h * 0.105))
    mark = _load_brand_logo_for_badge(logo_path, target_h)
    if mark is None:
        return
    target_w = mark.width

    pad_x, pad_y = 14, 10
    badge_x2 = w - 18
    badge_x1 = badge_x2 - target_w - pad_x * 2
    badge_y2 = h - 16
    badge_y1 = badge_y2 - target_h - pad_y * 2

    draw = ImageDraw.Draw(img)
    _rounded_rect(
        draw,
        (badge_x1, badge_y1, badge_x2, badge_y2),
        10,
        NAVY_SHADOW,
        outline=PEACOCK_CYAN,
        width=2,
    )
    img.paste(mark, (badge_x1 + pad_x, badge_y1 + pad_y), mark)


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


def _draw_app_cover_layout(
    title_lines: list[str],
    subtitle: str | list[str],
    w: int = 1200,
    h: int = 600,
    brand_logo: Path | None = None,
) -> Image.Image:
    """Cover art with disc shell only (no shimmer or module icon). Used as GIF base."""
    subtitle_lines = subtitle if isinstance(subtitle, list) else [subtitle]
    img = Image.new('RGB', (w, h), PEACOCK_TEAL)
    draw = ImageDraw.Draw(img)
    _draw_cover_background(img, w, h)
    _draw_odoo_version_badge(img, w, h)
    _draw_website_pill(img, w, h)
    _draw_left_logo_disc(img, w, h, shell_only=True)

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

    _draw_company_logo_badge(img, w, h, brand_logo=brand_logo)
    return img


def draw_app_cover(
    title_lines: list[str],
    subtitle: str | list[str],
    w: int = 1200,
    h: int = 600,
    brand_logo: Path | None = None,
    cover_logo: Path | None = None,
    disc_phase: float = COVER_STATIC_DISC_PHASE,
    module_mark: Image.Image | None = None,
) -> Image.Image:
    """Render loempia_app_cover style banner for one module."""
    brand_path = brand_logo or DEFAULT_BRAND_LOGO
    img = _draw_app_cover_layout(title_lines, subtitle, w=w, h=h, brand_logo=brand_path)
    _draw_disc_content(img, w, h, disc_phase, module_mark=module_mark)
    return img


def draw_app_cover_gif_frames(
    title_lines: list[str],
    subtitle: str | list[str],
    w: int = 1200,
    h: int = 600,
    brand_logo: Path | None = None,
    cover_logo: Path | None = None,
    frame_count: int = COVER_GIF_FRAMES,
    module_mark: Image.Image | None = None,
) -> list[Image.Image]:
    """Build looping cover frames with POS-style shimmer then module icon reveal."""
    _, _, _, inner = _disc_geometry(w, h)
    if module_mark is None:
        module_mark = Image.new('RGBA', (inner * 2, inner * 2), (0, 0, 0, 0))
    brand_path = brand_logo or DEFAULT_BRAND_LOGO
    layout = _draw_app_cover_layout(title_lines, subtitle, w=w, h=h, brand_logo=brand_path)
    frames: list[Image.Image] = []
    for index in range(frame_count):
        phase = index / max(frame_count - 1, 1)
        frame = layout.copy()
        _draw_disc_content(frame, w, h, phase, module_mark=module_mark)
        frames.append(frame)
    return frames


def save_cover_gif(frames: list[Image.Image], path: Path, duration_ms: int = COVER_GIF_FRAME_MS) -> None:
    """Write an optimized looping GIF from RGB frames."""
    if not frames:
        return
    rgb_frames = [frame.convert('RGB') for frame in frames]
    rgb_frames[0].save(
        path,
        save_all=True,
        append_images=rgb_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
    )


def save_cover_assets(
    module_dir: Path,
    title_lines: list[str],
    subtitle: str | list[str],
    module_name: str,
    module_summary: str,
    cover_logo: Path | None = None,
    animated: bool = True,
) -> None:
    """Write icon.png, banner assets, and cover logo into static/description."""
    out = module_dir / 'static' / 'description'
    out.mkdir(parents=True, exist_ok=True)
    module_slug = module_dir.name
    logo_src = cover_logo or DEFAULT_COVER_LOGO
    brand_src = DEFAULT_BRAND_LOGO
    if logo_src.is_file():
        dest = out / 'armorait_cover_logo.png'
        if logo_src.resolve() != dest.resolve():
            shutil.copy2(logo_src, dest)
    if brand_src.is_file():
        brand_dest = out / 'armorait_brand_logo.png'
        if brand_src.resolve() != brand_dest.resolve():
            shutil.copy2(brand_src, brand_dest)

    icon = draw_module_icon(module_slug, module_name, module_summary)
    icon.save(out / 'icon.png', 'PNG', optimize=True)

    _, _, _, inner = _disc_geometry(1200, 600)
    module_mark = module_icon_for_disc(module_slug, module_name, module_summary, inner * 2 - 28)

    banner = draw_app_cover(
        title_lines,
        subtitle,
        brand_logo=brand_src,
        module_mark=module_mark,
    )
    banner.save(out / 'banner.png', 'PNG', optimize=True)
    banner_small = banner.resize((360, 180), RESAMPLE)
    banner_small.save(out / 'banner_small.png', 'PNG', optimize=True)
    mp_assets = module_dir / 'marketplace' / 'assets'
    mp_assets.mkdir(parents=True, exist_ok=True)
    for asset_name in ('icon.png', 'banner.png', 'banner_small.png'):
        shutil.copy2(out / asset_name, mp_assets / asset_name)
    if animated:
        frames = draw_app_cover_gif_frames(
            title_lines,
            subtitle,
            brand_logo=brand_src,
            module_mark=module_mark,
        )
        save_cover_gif(frames, out / 'banner.gif')
        small_frames = [frame.resize((360, 180), RESAMPLE) for frame in frames]
        save_cover_gif(small_frames, out / 'banner_small.gif')


def generate_covers_for_repo(
    repo_root: Path,
    cover_logo: Path | None = None,
    animated: bool = True,
) -> list[str]:
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
        save_cover_assets(
            module_dir,
            title_lines,
            subtitle,
            module_name=name,
            module_summary=summary,
            cover_logo=cover_logo,
            animated=animated,
        )
        generated.append(module_dir.name)
    return generated
