#!/usr/bin/env python3
"""Generate per-module Apps Store icons from technical name and manifest text."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

try:
    RESAMPLE = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
except AttributeError:
    RESAMPLE = getattr(Image, 'LANCZOS', Image.ANTIALIAS)

ICON_SIZE = 256
CORNER_RADIUS = 52


@dataclass(frozen=True)
class IconSpec:
    top_color: str
    bottom_color: str
    accent: str
    glyph: str


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


def _slug_palette(module_slug: str) -> tuple[str, str, str]:
    digest = hashlib.md5(module_slug.encode()).hexdigest()
    index = int(digest[:2], 16) % len(PALETTES)
    return PALETTES[index]


def _match_glyph(module_slug: str, name: str, summary: str) -> str:
    blob = f'{module_slug} {name} {summary}'.lower()
    rules: list[tuple[str, str]] = [
        (r'arabic|tooltip', 'document'),
        (r'saudi_dashboard|saudi finance', 'gauge'),
        (r'ai_employee|copilot|conversational', 'chatbot'),
        (r'workflow_builder|workflow', 'workflow'),
        (r'approval_engine|approval', 'approval'),
        (r'invoice_ocr|invoice', 'invoice_scan'),
        (r'email_intelligence|email', 'email'),
        (r'document_generator|document_automation', 'document'),
        (r'document_idp|document_processing|document_platform', 'documents'),
        (r'ai_site|business_launch', 'rocket'),
        (r'school', 'school'),
        (r'payroll', 'payslip'),
        (r'attendance_face|face', 'face_scan'),
        (r'resume', 'resume'),
        (r'hr_intelligence|hrms|workforce', 'org_chart'),
        (r'bi_sales|sales_dashboard', 'bar_chart'),
        (r'dashboard', 'gauge'),
        (r'booking|appointment', 'calendar'),
        (r'cloud_platform|cloud', 'cloud'),
        (r'construction', 'building'),
        (r'crm', 'users'),
        (r'customer_engagement|customer_experience', 'heart_users'),
        (r'dental|hospital|hms|medical', 'medical'),
        (r'erp_health|health_analyzer', 'heartbeat'),
        (r'fleet|gps', 'truck_map'),
        (r'hall|temple', 'temple'),
        (r'hotel', 'hotel'),
        (r'inventory|forecast', 'boxes'),
        (r'jewellery', 'diamond'),
        (r'gst|l10n', 'tax'),
        (r'mes|mrp|manufacturing|textile', 'factory'),
        (r'mobile', 'mobile'),
        (r'realestate|rental', 'house_key'),
        (r'restaurant', 'utensils'),
        (r'theme|website', 'palette'),
        (r'veterinary', 'paw'),
    ]
    for pattern, glyph in rules:
        if re.search(pattern, blob):
            return glyph
    return 'puzzle'


def resolve_icon_spec(module_slug: str, name: str, summary: str) -> IconSpec:
    top, bottom, accent = _slug_palette(module_slug)
    return IconSpec(top, bottom, accent, _match_glyph(module_slug, name, summary))


def _lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def _hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _gradient_bg(size: int, top: str, bottom: str) -> Image.Image:
    img = Image.new('RGB', (size, size))
    top_rgb = _hex_rgb(top)
    bottom_rgb = _hex_rgb(bottom)
    px = img.load()
    for y in range(size):
        t = y / max(size - 1, 1)
        color = tuple(_lerp(top_rgb[i], bottom_rgb[i], t) for i in range(3))
        for x in range(size):
            px[x, y] = color
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=CORNER_RADIUS, fill=255)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def _center(draw: ImageDraw.ImageDraw, size: int) -> tuple[int, int]:
    return size // 2, size // 2


def _label_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype('DejaVuSans-Bold.ttf', size)
    except OSError:
        return ImageFont.load_default()


def _glyph_chatbot(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    w, h = int(size * 0.46), int(size * 0.34)
    x1, y1 = cx - w // 2, cy - h // 2 - 8
    x2, y2 = x1 + w, y1 + h
    draw.rounded_rectangle((x1, y1, x2, y2), radius=18, fill='white')
    draw.polygon([(x1 + 18, y2), (x1 + 8, y2 + 18), (x1 + 34, y2)], fill='white')
    for dx in (-28, 0, 28):
        draw.ellipse((cx + dx - 7, cy - 8, cx + dx + 7, cy + 6), fill=accent)
    draw.polygon(
        [(size - 54, 44), (size - 38, 44), (size - 46, 60)],
        fill='#34D399',
    )


def _glyph_document(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    w, h = int(size * 0.38), int(size * 0.48)
    x1, y1 = cx - w // 2, cy - h // 2
    x2, y2 = x1 + w, y1 + h
    draw.rounded_rectangle((x1, y1, x2, y2), radius=10, fill='white')
    fold = 28
    draw.polygon([(x2 - fold, y1), (x2, y1 + fold), (x2 - fold, y1 + fold)], fill=accent)
    for i, lw in enumerate((0.62, 0.48, 0.55)):
        y = y1 + 52 + i * 24
        draw.rounded_rectangle((x1 + 20, y, x1 + int(w * lw), y + 8), radius=4, fill=accent)


def _glyph_documents(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    for ox, oy in ((-18, -10), (0, 0), (18, 10)):
        x1, y1 = cx - 52 + ox, cy - 66 + oy
        draw.rounded_rectangle((x1, y1, x1 + 84, y1 + 104), radius=10, fill='white')
        draw.rounded_rectangle((x1 + 16, y1 + 24, x1 + 64, y1 + 32), radius=3, fill=accent)
        draw.rounded_rectangle((x1 + 16, y1 + 42, x1 + 52, y1 + 50), radius=3, fill=accent)


def _glyph_email(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    w, h = int(size * 0.52), int(size * 0.36)
    x1, y1 = cx - w // 2, cy - h // 2
    x2, y2 = x1 + w, y1 + h
    draw.rounded_rectangle((x1, y1, x2, y2), radius=12, fill='white')
    draw.polygon([(x1 + 12, y1 + 18), (cx, cy + 8), (x2 - 12, y1 + 18)], fill=accent)
    draw.line([(x1 + 12, y2 - 18), (cx, cy - 4), (x2 - 12, y2 - 18)], fill=accent, width=4)


def _glyph_invoice_scan(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    _glyph_document(draw, size, accent)
    cx, cy = _center(draw, size)
    draw.arc((cx - 70, cy - 70, cx + 70, cy + 70), 300, 60, fill='#34D399', width=6)
    draw.line([(cx + 42, cy - 58), (cx + 58, cy - 42)], fill='#34D399', width=6)


def _glyph_rocket(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.polygon([(cx, cy - 70), (cx + 34, cy + 20), (cx, cy + 6), (cx - 34, cy + 20)], fill='white')
    draw.ellipse((cx - 16, cy - 10, cx + 16, cy + 22), fill=accent)
    draw.polygon([(cx - 34, cy + 16), (cx - 58, cy + 44), (cx - 20, cy + 28)], fill='#FDE047')
    draw.polygon([(cx + 34, cy + 16), (cx + 58, cy + 44), (cx + 20, cy + 28)], fill='#FDE047')


def _glyph_workflow(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    nodes = [(cx - 58, cy - 40), (cx + 58, cy - 40), (cx, cy + 44)]
    for nx, ny in nodes:
        draw.ellipse((nx - 22, ny - 22, nx + 22, ny + 22), fill='white')
    draw.line([nodes[0], nodes[2]], fill='white', width=6)
    draw.line([nodes[1], nodes[2]], fill='white', width=6)
    draw.ellipse((cx - 8, cy + 36, cx + 8, cy + 52), fill=accent)


def _glyph_approval(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rounded_rectangle((cx - 56, cy - 68, cx + 56, cy + 68), radius=18, fill='white')
    draw.line([(cx - 24, cy + 4), (cx - 4, cy + 28), (cx + 34, cy - 24)], fill=accent, width=10)


def _glyph_bar_chart(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    base = cy + 54
    for i, (h, color) in enumerate(((58, 'white'), (88, accent), (44, '#BFDBFE'))):
        x = cx - 52 + i * 36
        draw.rounded_rectangle((x, base - h, x + 28, base), radius=6, fill=color)


def _glyph_gauge(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.arc((cx - 64, cy - 64, cx + 64, cy + 64), 200, 340, fill='white', width=14)
    draw.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=accent)
    draw.line([(cx, cy), (cx + 42, cy - 28)], fill=accent, width=8)


def _glyph_calendar(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rounded_rectangle((cx - 62, cy - 52, cx + 62, cy + 62), radius=14, fill='white')
    draw.rectangle((cx - 62, cy - 52, cx + 62, cy - 18), fill=accent)
    for i in range(3):
        for j in range(3):
            x = cx - 36 + j * 28
            y = cy - 2 + i * 24
            draw.rounded_rectangle((x, y, x + 16, y + 14), radius=3, fill=accent)


def _glyph_cloud(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.ellipse((cx - 72, cy - 18, cx - 8, cy + 42), fill='white')
    draw.ellipse((cx - 34, cy - 42, cx + 38, cy + 30), fill='white')
    draw.ellipse((cx + 8, cy - 10, cx + 72, cy + 42), fill='white')
    draw.rounded_rectangle((cx - 76, cy + 18, cx + 76, cy + 48), radius=8, fill='white')
    draw.ellipse((cx - 8, cy + 28, cx + 8, cy + 44), fill=accent)


def _glyph_building(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rectangle((cx - 58, cy - 58, cx + 58, cy + 62), fill='white')
    for row in range(4):
        for col in range(3):
            x = cx - 40 + col * 28
            y = cy - 42 + row * 24
            draw.rectangle((x, y, x + 16, y + 14), fill=accent)


def _glyph_users(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    for dx in (-34, 34):
        draw.ellipse((cx + dx - 18, cy - 54, cx + dx + 18, cy - 18), fill='white')
        draw.ellipse((cx + dx - 28, cy - 4, cx + dx + 28, cy + 52), fill='white')
    draw.ellipse((cx - 22, cy - 44, cx + 22, cy), fill=accent)
    draw.ellipse((cx - 34, cy + 8, cx + 34, cy + 72), fill=accent)


def _glyph_heart_users(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.ellipse((cx - 18, cy - 52, cx + 18, cy - 16), fill='white')
    draw.ellipse((cx - 30, cy - 4, cx + 30, cy + 56), fill='white')
    draw.ellipse((cx + 30, cy - 10, cx + 54, cy + 14), fill='#FCA5A5')
    draw.ellipse((cx + 42, cy - 10, cx + 66, cy + 14), fill='#FCA5A5')
    draw.polygon([(cx + 48, cy + 34), (cx + 30, cy + 16), (cx + 66, cy + 16)], fill='#EF4444')


def _glyph_medical(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rounded_rectangle((cx - 44, cy - 64, cx + 44, cy + 64), radius=16, fill='white')
    draw.rectangle((cx - 12, cy - 36, cx + 12, cy + 36), fill=accent)
    draw.rectangle((cx - 36, cy - 12, cx + 36, cy + 12), fill=accent)


def _glyph_heartbeat(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    points = []
    for x in range(cx - 72, cx + 74, 8):
        t = (x - cx) / 72
        y = cy + (12 if abs(t) < 0.15 else (-34 if 0.35 < t < 0.55 else (-10 if 0.55 < t < 0.75 else 8)))
        points.append((x, y))
    draw.line(points, fill='white', width=8)
    draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=accent)


def _glyph_truck_map(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rounded_rectangle((cx - 68, cy - 20, cx + 68, cy + 48), radius=10, fill='white')
    draw.rounded_rectangle((cx + 10, cy - 44, cx + 58, cy + 10), radius=8, fill='white')
    draw.ellipse((cx - 48, cy + 28, cx - 20, cy + 56), fill=accent)
    draw.ellipse((cx + 24, cy + 28, cx + 52, cy + 56), fill=accent)
    draw.ellipse((cx - 8, cy - 58, cx + 8, cy - 42), fill='#34D399')


def _glyph_temple(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.polygon([(cx, cy - 68), (cx - 68, cy + 10), (cx + 68, cy + 10)], fill='white')
    draw.rectangle((cx - 52, cy + 10, cx + 52, cy + 62), fill='white')
    draw.rectangle((cx - 14, cy + 18, cx + 14, cy + 62), fill=accent)


def _glyph_hotel(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rounded_rectangle((cx - 58, cy - 52, cx + 58, cy + 62), radius=12, fill='white')
    draw.rectangle((cx - 34, cy - 10, cx + 34, cy + 34), fill=accent)
    draw.rectangle((cx - 48, cy - 34, cx - 28, cy - 14), fill=accent)
    draw.rectangle((cx + 28, cy - 34, cx + 48, cy - 14), fill=accent)


def _glyph_face_scan(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.ellipse((cx - 48, cy - 58, cx + 48, cy + 38), fill='white')
    draw.ellipse((cx - 16, cy - 20, cx - 4, cy - 8), fill=accent)
    draw.ellipse((cx + 4, cy - 20, cx + 16, cy - 8), fill=accent)
    draw.arc((cx - 18, cy + 2, cx + 18, cy + 24), 20, 160, fill=accent, width=4)
    draw.rectangle((cx - 62, cy - 62, cx + 62, cy + 50), outline='#34D399', width=5)


def _glyph_resume(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    _glyph_document(draw, size, accent)
    cx, cy = _center(draw, size)
    draw.ellipse((cx - 48, cy - 48, cx - 12, cy - 12), fill=accent)


def _glyph_org_chart(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    nodes = [(cx, cy - 52), (cx - 50, cy + 18), (cx + 50, cy + 18), (cx, cy + 58)]
    for nx, ny in nodes:
        draw.ellipse((nx - 18, ny - 18, nx + 18, ny + 18), fill='white')
    draw.line([nodes[0], nodes[1]], fill='white', width=5)
    draw.line([nodes[0], nodes[2]], fill='white', width=5)
    draw.line([nodes[1], nodes[3]], fill='white', width=5)
    draw.line([nodes[2], nodes[3]], fill='white', width=5)
    draw.ellipse((cx - 6, cy - 58, cx + 6, cy - 46), fill=accent)


def _glyph_boxes(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rectangle((cx - 58, cy - 10, cx - 8, cy + 40), fill='white')
    draw.rectangle((cx - 8, cy - 40, cx + 42, cy + 10), fill='white')
    draw.line([(cx - 58, cy - 10), (cx - 8, cy - 40), (cx + 42, cy - 40)], fill=accent, width=4)
    draw.line([(cx - 8, cy - 40), (cx - 8, cy + 10)], fill=accent, width=4)


def _glyph_diamond(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.polygon([(cx, cy - 62), (cx + 54, cy - 8), (cx, cy + 62), (cx - 54, cy - 8)], fill='white')
    draw.polygon([(cx, cy - 62), (cx + 20, cy - 8), (cx, cy + 20), (cx - 20, cy - 8)], fill=accent)


def _glyph_tax(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    _glyph_document(draw, size, accent)
    cx, cy = _center(draw, size)
    draw.text((cx - 20, cy - 22), '%', fill=accent, font=_label_font(42))


def _glyph_payslip(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    _glyph_document(draw, size, accent)
    cx, cy = _center(draw, size)
    draw.text((cx - 14, cy - 22), '$', fill=accent, font=_label_font(42))


def _glyph_factory(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rectangle((cx - 62, cy - 10, cx + 62, cy + 58), fill='white')
    draw.polygon([(cx - 20, cy - 10), (cx - 20, cy - 54), (cx + 8, cy - 30), (cx + 8, cy - 10)], fill='white')
    draw.ellipse((cx - 44, cy + 18, cx - 18, cy + 44), fill=accent)
    draw.ellipse((cx + 18, cy + 18, cx + 44, cy + 44), fill=accent)


def _glyph_mobile(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rounded_rectangle((cx - 34, cy - 68, cx + 34, cy + 68), radius=16, fill='white')
    draw.rounded_rectangle((cx - 24, cy - 52, cx + 24, cy + 48), radius=8, fill=accent)
    draw.ellipse((cx - 8, cy + 54, cx + 8, cy + 64), fill=accent)


def _glyph_house_key(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.polygon([(cx - 8, cy - 58), (cx - 48, cy - 10), (cx + 32, cy - 10)], fill='white')
    draw.rectangle((cx - 48, cy - 10, cx + 48, cy + 52), fill='white')
    draw.ellipse((cx + 24, cy + 18, cx + 52, cy + 46), outline=accent, width=8)
    draw.line([(cx + 52, cy + 32), (cx + 68, cy + 32)], fill=accent, width=8)


def _glyph_utensils(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rounded_rectangle((cx - 58, cy + 18, cx + 58, cy + 58), radius=10, fill='white')
    draw.line([(cx - 24, cy - 58), (cx - 24, cy + 10)], fill='white', width=8)
    draw.line([(cx + 24, cy - 58), (cx + 24, cy + 10)], fill='white', width=8)
    draw.arc((cx - 34, cy - 58, cx - 14, cy - 18), 0, 180, fill='white', width=8)
    draw.ellipse((cx + 14, cy - 30, cx + 34, cy - 10), fill=accent)


def _glyph_school(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.polygon([(cx, cy - 64), (cx - 68, cy - 16), (cx + 68, cy - 16)], fill='white')
    draw.rectangle((cx - 48, cy - 16, cx + 48, cy + 58), fill='white')
    draw.rectangle((cx - 10, cy + 10, cx + 10, cy + 58), fill=accent)
    draw.ellipse((cx - 68, cy - 24, cx - 44, cy), fill='#FDE047')


def _glyph_palette(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.ellipse((cx - 58, cy - 48, cx + 58, cy + 48), fill='white')
    for color, ox, oy in (('#EF4444', -20, -12), ('#3B82F6', 10, -18), ('#10B981', 24, 8), ('#F59E0B', -8, 20)):
        draw.ellipse((cx + ox - 10, cy + oy - 10, cx + ox + 10, cy + oy + 10), fill=color)
    draw.ellipse((cx + 28, cy + 18, cx + 48, cy + 38), fill=accent)


def _glyph_paw(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.ellipse((cx - 24, cy - 10, cx + 24, cy + 38), fill='white')
    for ox, oy in ((-28, -34), (0, -44), (28, -34), (-14, -18)):
        draw.ellipse((cx + ox - 14, cy + oy - 14, cx + ox + 14, cy + oy + 14), fill='white')
    draw.ellipse((cx - 8, cy + 4, cx + 8, cy + 20), fill=accent)


def _glyph_whatsapp(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.ellipse((cx - 58, cy - 58, cx + 58, cy + 58), fill='white')
    draw.ellipse((cx - 44, cy - 44, cx + 44, cy + 44), fill='#25D366')
    draw.arc((cx - 18, cy - 8, cx + 18, cy + 20), 200, 340, fill='white', width=6)
    draw.ellipse((cx - 44, cy + 24, cx - 20, cy + 48), fill='white')


def _glyph_puzzle(draw: ImageDraw.ImageDraw, size: int, accent: str) -> None:
    cx, cy = _center(draw, size)
    draw.rounded_rectangle((cx - 48, cy - 48, cx + 48, cy + 48), radius=14, fill='white')
    draw.rectangle((cx - 8, cy - 48, cx + 8, cy - 24), fill=accent)
    draw.rectangle((cx + 24, cy - 8, cx + 48, cy + 8), fill=accent)


GLYPHS: dict[str, Callable[[ImageDraw.ImageDraw, int, str], None]] = {
    'chatbot': _glyph_chatbot,
    'document': _glyph_document,
    'documents': _glyph_documents,
    'email': _glyph_email,
    'invoice_scan': _glyph_invoice_scan,
    'rocket': _glyph_rocket,
    'workflow': _glyph_workflow,
    'approval': _glyph_approval,
    'bar_chart': _glyph_bar_chart,
    'gauge': _glyph_gauge,
    'calendar': _glyph_calendar,
    'cloud': _glyph_cloud,
    'building': _glyph_building,
    'users': _glyph_users,
    'heart_users': _glyph_heart_users,
    'medical': _glyph_medical,
    'heartbeat': _glyph_heartbeat,
    'truck_map': _glyph_truck_map,
    'temple': _glyph_temple,
    'hotel': _glyph_hotel,
    'face_scan': _glyph_face_scan,
    'resume': _glyph_resume,
    'org_chart': _glyph_org_chart,
    'boxes': _glyph_boxes,
    'diamond': _glyph_diamond,
    'tax': _glyph_tax,
    'factory': _glyph_factory,
    'mobile': _glyph_mobile,
    'payslip': _glyph_payslip,
    'house_key': _glyph_house_key,
    'utensils': _glyph_utensils,
    'school': _glyph_school,
    'palette': _glyph_palette,
    'paw': _glyph_paw,
    'whatsapp': _glyph_whatsapp,
    'puzzle': _glyph_puzzle,
}


def draw_module_icon(
    module_slug: str,
    name: str,
    summary: str,
    size: int = ICON_SIZE,
) -> Image.Image:
    """Render a rounded-square module icon."""
    spec = resolve_icon_spec(module_slug, name, summary)
    image = _gradient_bg(size, spec.top_color, spec.bottom_color)
    draw = ImageDraw.Draw(image)
    painter = GLYPHS.get(spec.glyph, _glyph_puzzle)
    painter(draw, size, spec.accent)
    return image


def module_icon_for_disc(
    module_slug: str,
    name: str,
    summary: str,
    max_size: int,
) -> Image.Image:
    """Scale module icon for the cover left disc."""
    icon = draw_module_icon(module_slug, name, summary, ICON_SIZE)
    scale = min(max_size / icon.width, max_size / icon.height)
    target = max(1, int(icon.width * scale))
    return icon.resize((target, target), RESAMPLE)
