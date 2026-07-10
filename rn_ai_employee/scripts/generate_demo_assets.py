#!/usr/bin/env python3
"""Generate Apps Store screenshots and workflow GIFs for AI Copilot for Odoo."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    RESAMPLE = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
except AttributeError:
    RESAMPLE = getattr(Image, 'LANCZOS', Image.ANTIALIAS)

OUT = Path(__file__).resolve().parents[1] / 'static' / 'description'
BRAND_LOGO = OUT / 'armorait_brand_logo.png'

# Odoo 19 / ARMORA palette
PURPLE = '#714B67'
PURPLE_DARK = '#5B21B6'
PURPLE_LIGHT = '#8B5CF6'
ACCENT = '#017E84'
BG = '#F8F9FA'
WHITE = '#FFFFFF'
NAVY = '#1F2937'
TEXT = '#374151'
MUTED = '#6B7280'
BORDER = '#E5E7EB'
SUCCESS = '#10B981'
WARNING = '#F59E0B'
INFO_BG = '#E0F2FE'
USER_BG = '#F3F4F6'
ASSIST_BG = '#EDE9FE'


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


def _navbar(draw: ImageDraw.ImageDraw, w: int, title: str = 'AI Copilot') -> None:
    draw.rectangle((0, 0, w, 46), fill=NAVY)
    draw.text((14, 14), 'Odoo', font=_font(14, True), fill=WHITE)
    draw.text((70, 14), title, font=_font(13), fill='#D1D5DB')
    for i, icon in enumerate(('bell', 'chat', 'user')):
        x = w - 120 + i * 36
        _rounded_rect(draw, (x, 10, x + 28, 34), 6, '#374151')
        if icon == 'chat':
            draw.ellipse((x + 8, 16, x + 20, 28), fill=PURPLE_LIGHT)


def _sidebar(draw: ImageDraw.ImageDraw, h: int) -> None:
    draw.rectangle((0, 46, 200, h), fill=WHITE)
    draw.line((200, 46, 200, h), fill=BORDER, width=1)
    items = (
        ('AI Copilot', True),
        ('Ask AI Copilot', False),
        ('Audit Log', False),
        ('Skill Registry', False),
        ('Settings', False),
    )
    y = 58
    for label, active in items:
        if active:
            draw.rectangle((0, y - 4, 4, y + 22), fill=PURPLE)
            draw.rectangle((8, y - 4, 192, y + 22), fill='#F3E8FF')
        draw.text((16, y), label, font=_font(12, active), fill=PURPLE if active else TEXT)
        y += 32


def _badge(draw, xy, text, bg, fg=WHITE, font_size=11):
    x, y = xy
    tw, th = _text_size(draw, text, _font(font_size, True))
    pad_x, pad_y = 8, 4
    _rounded_rect(draw, (x, y, x + tw + pad_x * 2, y + th + pad_y * 2), 10, bg)
    draw.text((x + pad_x, y + pad_y), text, font=_font(font_size, True), fill=fg)


def _chat_bubble(draw, x, y, w, role, headline, body, actions=None):
    role_colors = {
        'user': (USER_BG, TEXT),
        'assistant': (ASSIST_BG, PURPLE_DARK),
        'system': ('#FEF3C7', '#92400E'),
    }
    bg, fg = role_colors.get(role, (WHITE, TEXT))
    font_label = _font(10, True)
    font_head = _font(13, True)
    font_body = _font(12)
    pad = 12
    lines = body.split('\n')
    line_h = 18
    body_h = len(lines) * line_h
    head_h = 20 if headline else 0
    act_h = 34 if actions else 0
    box_h = pad * 2 + 14 + head_h + body_h + act_h
    _rounded_rect(draw, (x, y, x + w, y + box_h), 10, bg, outline=BORDER)
    draw.text((x + pad, y + pad), role.upper(), font=font_label, fill=MUTED)
    cy = y + pad + 14
    if headline:
        draw.text((x + pad, cy), headline, font=font_head, fill=fg)
        cy += head_h
    for line in lines:
        draw.text((x + pad, cy), line, font=font_body, fill=fg)
        cy += line_h
    if actions:
        ax = x + pad
        for label, color in actions:
            tw, th = _text_size(draw, label, _font(11))
            _rounded_rect(draw, (ax, cy, ax + tw + 16, cy + 24), 6, WHITE, outline=color, width=2)
            draw.text((ax + 8, cy + 5), label, font=_font(11), fill=color)
            ax += tw + 28


def _step_banner(draw, w, step: str, title: str):
    draw.rectangle((200, 46, w, 92), fill=WHITE)
    draw.line((200, 92, w, 92), fill=BORDER)
    _badge(draw, (216, 56), step, PURPLE)
    draw.text((320, 58), title, font=_font(16, True), fill=NAVY)


def draw_systray_scene(step: str, title: str, messages: list, draft: str = '') -> Image.Image:
    w, h = 1280, 720
    img = Image.new('RGB', (w, h), BG)
    draw = ImageDraw.Draw(img)
    _navbar(draw, w)
    _sidebar(draw, h)
    _step_banner(draw, w, step, title)

    # Main content faded
    draw.text((220, 110), 'Sales / Quotations', font=_font(20, True), fill=NAVY)
    draw.text((220, 145), 'Working in Odoo while AI Copilot stays available in the systray.', font=_font(12), fill=MUTED)

    # Systray panel
    px, py, pw, ph = 860, 100, 390, 580
    _rounded_rect(draw, (px, py, px + pw, py + ph), 12, WHITE, outline=BORDER, width=2)
    draw.rectangle((px, py, px + pw, py + 58), fill='#F9FAFB')
    draw.text((px + 16, py + 12), 'AI Copilot for Odoo', font=_font(14, True), fill=NAVY)
    draw.text((px + 16, py + 32), 'Enterprise intelligence layer', font=_font(10), fill=MUTED)

    my = py + 72
    for msg in messages:
        payload = {k: v for k, v in msg.items() if k != 'height'}
        _chat_bubble(draw, px + 12, my, pw - 24, **payload)
        my += msg.get('height', 110)

    # Input
    iy = py + ph - 88
    _rounded_rect(draw, (px + 12, iy, px + pw - 12, iy + 44), 8, WHITE, outline=BORDER)
    placeholder = draft or 'Ask AI Copilot...'
    draw.text((px + 20, iy + 12), placeholder, font=_font(12), fill=TEXT if draft else MUTED)
    _rounded_rect(draw, (px + pw - 92, iy + 50, px + pw - 16, iy + 76), 6, PURPLE)
    draw.text((px + pw - 78, iy + 57), 'Send', font=_font(11, True), fill=WHITE)

    # Footer brand
    draw.text((20, h - 28), 'ARMORA IT Technologies | AI Copilot for Odoo', font=_font(10), fill=MUTED)
    return img


def draw_settings_scene() -> Image.Image:
    w, h = 1280, 720
    img = Image.new('RGB', (w, h), BG)
    draw = ImageDraw.Draw(img)
    _navbar(draw, w, 'Settings')
    _sidebar(draw, h)
    draw.text((220, 70), 'AI Copilot Platform', font=_font(22, True), fill=NAVY)

    cards = [
        ('Enable AI Copilot', 'Turn on the enterprise intelligence layer for this company.', True),
        ('Require write confirmation', 'Sensitive skills ask for explicit approval before changing data.', True),
        ('Morning briefing', 'Proactive executive summary delivered each morning.', False),
        ('LLM provider', 'OpenAI-compatible routing with rules fallback when no key is set.', True),
    ]
    y = 120
    for title, desc, on in cards:
        _rounded_rect(draw, (220, y, w - 40, y + 88), 10, WHITE, outline=BORDER)
        draw.text((240, y + 16), title, font=_font(14, True), fill=NAVY)
        draw.text((240, y + 42), desc, font=_font(11), fill=MUTED)
        toggle_x = w - 120
        color = SUCCESS if on else '#D1D5DB'
        _rounded_rect(draw, (toggle_x, y + 28, toggle_x + 52, y + 52), 12, color)
        knob = toggle_x + 36 if on else toggle_x + 6
        draw.ellipse((knob, y + 30, knob + 20, y + 50), fill=WHITE)
        y += 100
    return img


def draw_tools_scene() -> Image.Image:
    w, h = 1280, 720
    img = Image.new('RGB', (w, h), BG)
    draw = ImageDraw.Draw(img)
    _navbar(draw, w)
    _sidebar(draw, h)
    draw.text((220, 70), 'Skill Registry', font=_font(22, True), fill=NAVY)
    draw.text((220, 102), '28 analytics and write skills across Sales, Finance, Inventory, CRM, and Purchase.', font=_font(12), fill=MUTED)

    headers = ('Skill', 'Domain', 'Type', 'Status')
    cols = (240, 520, 720, 920)
    y = 140
    _rounded_rect(draw, (220, y, w - 40, y + 36), 6, '#F3F4F6')
    for header, cx in zip(headers, cols):
        draw.text((cx, y + 10), header, font=_font(11, True), fill=MUTED)
    y += 40

    rows = [
        ('pending_quotations', 'Sales', 'Read', 'Active'),
        ('overdue_invoices', 'Finance', 'Read', 'Active'),
        ('create_quotation', 'Sales', 'Write', 'Confirm'),
        ('send_payment_reminders', 'Finance', 'Write', 'Confirm'),
        ('create_rfq', 'Purchase', 'Write', 'Confirm'),
        ('morning_briefing', 'Executive', 'Proactive', 'Active'),
        ('reserve_stock', 'Inventory', 'Write', 'Confirm'),
    ]
    for skill, domain, typ, status in rows:
        _rounded_rect(draw, (220, y, w - 40, y + 40), 4, WHITE, outline=BORDER)
        draw.text((cols[0], y + 12), skill, font=_font(11), fill=TEXT)
        draw.text((cols[1], y + 12), domain, font=_font(11), fill=TEXT)
        draw.text((cols[2], y + 12), typ, font=_font(11), fill=TEXT)
        st_color = WARNING if status == 'Confirm' else SUCCESS
        _badge(draw, (cols[3], y + 10), status, st_color, font_size=10)
        y += 44
    return img


def draw_audit_scene() -> Image.Image:
    w, h = 1280, 720
    img = Image.new('RGB', (w, h), BG)
    draw = ImageDraw.Draw(img)
    _navbar(draw, w)
    _sidebar(draw, h)
    draw.text((220, 70), 'Audit Log', font=_font(22, True), fill=NAVY)

    headers = ('Time', 'User', 'Skill', 'Result', 'Confirmed')
    cols = (240, 380, 520, 760, 1040)
    y = 130
    _rounded_rect(draw, (220, y, w - 40, y + 34), 6, '#F3F4F6')
    for header, cx in zip(headers, cols):
        draw.text((cx, y + 9), header, font=_font(10, True), fill=MUTED)
    y += 38

    rows = [
        ('09:14', 'Arun', 'pending_quotations', '12 quotations found', 'n/a'),
        ('09:15', 'Arun', 'send_partner_email', '3 emails queued', 'Yes'),
        ('09:16', 'Arun', 'create_quotation', 'SO0042 draft created', 'Yes'),
        ('08:30', 'System', 'morning_briefing', 'Executive summary sent', 'n/a'),
    ]
    for row in rows:
        _rounded_rect(draw, (220, y, w - 40, y + 38), 4, WHITE, outline=BORDER)
        for val, cx in zip(row, cols):
            draw.text((cx, y + 11), val, font=_font(10), fill=TEXT)
        y += 42
    return img


def draw_list_scene() -> Image.Image:
    w, h = 1280, 720
    img = Image.new('RGB', (w, h), BG)
    draw = ImageDraw.Draw(img)
    _navbar(draw, w)
    _sidebar(draw, h)
    draw.text((220, 70), 'Conversations', font=_font(22, True), fill=NAVY)
    headers = ('Subject', 'User', 'Messages', 'Last preview')
    cols = (240, 520, 680, 820)
    y = 120
    _rounded_rect(draw, (220, y, w - 40, y + 34), 6, '#F3F4F6')
    for header, cx in zip(headers, cols):
        draw.text((cx, y + 9), header, font=_font(10, True), fill=MUTED)
    y += 38
    rows = [
        ('Pending quotations follow-up', 'Arun', '6', 'Email the first three customers'),
        ('Morning collections review', 'Priya', '4', 'Show overdue invoices'),
        ('RFQ for raw cotton', 'Arun', '3', 'Create RFQ for ABC Textiles'),
    ]
    for row in rows:
        _rounded_rect(draw, (220, y, w - 40, y + 40), 4, WHITE, outline=BORDER)
        for val, cx in zip(row, cols):
            draw.text((cx, y + 12), val, font=_font(11), fill=TEXT)
        y += 44
    return img


def draw_briefing_scene() -> Image.Image:
    w, h = 1280, 720
    img = Image.new('RGB', (w, h), BG)
    draw = ImageDraw.Draw(img)
    _navbar(draw, w, 'Executive Briefing')
    _sidebar(draw, h)
    draw.text((220, 70), 'Good morning, Arun', font=_font(24, True), fill=NAVY)
    draw.text((220, 108), 'Proactive intelligence from live Odoo data', font=_font(12), fill=MUTED)

    kpis = [
        ('Revenue (MTD)', '₹ 42.8L', '-8%', WARNING),
        ('Collections pending', '₹ 24.0L', '12 overdue', WARNING),
        ('PO approvals', '3 waiting', 'Action needed', PURPLE),
        ('Low stock SKUs', '7 items', 'Purchase suggested', ACCENT),
    ]
    x = 220
    for title, value, sub, color in kpis:
        _rounded_rect(draw, (x, 150, x + 230, 250), 12, WHITE, outline=BORDER, width=2)
        draw.text((x + 16, 166), title, font=_font(11), fill=MUTED)
        draw.text((x + 16, 190), value, font=_font(22, True), fill=NAVY)
        draw.text((x + 16, 222), sub, font=_font(11, True), fill=color)
        x += 250

    draw.text((220, 280), 'Suggested actions', font=_font(16, True), fill=NAVY)
    actions = [
        '1. Approve PO #521 (₹ 8.4L)',
        '2. Contact ABC Industries for overdue invoice INV/2026/0142',
        '3. Create RFQ for low-stock cotton yarn',
    ]
    y = 312
    for action in actions:
        _rounded_rect(draw, (220, y, w - 40, y + 44), 8, WHITE, outline=ACCENT, width=2)
        draw.text((236, y + 13), action, font=_font(12), fill=TEXT)
        y += 52
    return img


# Apps Store listing cover (Serpent layout + teal/black Armorait palette)
BLACK_TEAL = '#041015'
NAVY_BLACK = '#0a1628'
NAVY_DEEP = '#0f172a'
TEAL_DEEP = '#0f766e'
TEAL_MAIN = '#017E84'
TEAL_BRIGHT = '#14b8a6'
TEAL_CYAN = '#06b6d4'
TITLE_TEAL = '#017E84'
PANEL_GLOW = '#134e4a'


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _lerp_rgb(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _gradient_rgb(t: float) -> tuple[int, int, int]:
    """Teal gradient wash: deep teal -> brand teal -> bright cyan."""
    t = max(0.0, min(1.0, t))
    start, mid, end = _hex_to_rgb(TEAL_DEEP), _hex_to_rgb(TEAL_MAIN), _hex_to_rgb(TEAL_BRIGHT)
    if t <= 0.45:
        return _lerp_rgb(start, mid, t / 0.45)
    return _lerp_rgb(mid, end, (t - 0.45) / 0.55)


def _build_rich_panel_gradient(w: int, h: int) -> Image.Image:
    """Black-teal base with cyan/teal wash for a premium left panel."""
    panel = Image.new('RGB', (w, h))
    px = panel.load()
    black = _hex_to_rgb(BLACK_TEAL)
    navy = _hex_to_rgb(NAVY_BLACK)
    deep = _hex_to_rgb(NAVY_DEEP)
    for y in range(h):
        ty = y / max(h - 1, 1)
        for x in range(w):
            tx = x / max(w - 1, 1)
            glow_t = min(1.0, tx * 0.68 + (1.0 - ty) * 0.32)
            glow = _gradient_rgb(glow_t)
            base = _lerp_rgb(black, _lerp_rgb(navy, deep, ty * 0.5), tx * 0.35)
            shade = 0.64 if tx < 0.55 else 0.78
            color = tuple(int(base[i] * shade + glow[i] * (1.0 - shade)) for i in range(3))
            px[x, y] = color
    return panel


def _draw_diagonal_cover_background(img: Image.Image, w: int, h: int) -> int:
    """White right panel with rich navy gradient wedge on the left."""
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, h), fill='#F8FAFC')
    split_top = int(w * 0.54)
    split_bottom = int(w * 0.34)
    panel = _build_rich_panel_gradient(w, h)
    mask = Image.new('L', (w, h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon([
        (0, 0),
        (split_top, 0),
        (split_bottom, h),
        (0, h),
    ], fill=255)
    img.paste(panel, (0, 0), mask)
    glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.polygon([
        (0, 0),
        (split_top, 0),
        (split_bottom, h),
        (0, h),
    ], fill=(1, 126, 132, 30))
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
        color = _gradient_rgb(x / max(width - 1, 1))
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
        while tw > max_w and (not hasattr(font, 'size') or font.size > 30):
            size = font.size - 2 if hasattr(font, 'size') else 40
            font = _font(size, True)
            tw, th = _text_size(draw, line, font)
        x = left + (right - left - tw) // 2
        draw.text((x, cy), line, font=font, fill=TITLE_TEAL)
        cy += th + 6
    return cy


def _draw_cover_illustration(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int) -> None:
    """Circular AI copilot illustration on the rich navy panel."""
    glow_r = radius + 10
    draw.ellipse((cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r), fill=PANEL_GLOW)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill='#F8FAFC', outline='#99F6E4', width=4)
    inner = radius - 18
    draw.ellipse((cx - inner, cy - inner, cx + inner, cy + inner), fill='#ECFEFF')

    bubble_w, bubble_h = int(radius * 1.05), int(radius * 0.72)
    bx1, by1 = cx - bubble_w // 2, cy - bubble_h // 2 - 8
    bx2, by2 = bx1 + bubble_w, by1 + bubble_h
    _rounded_rect(draw, (bx1, by1, bx2, by2), 18, WHITE, outline=TEAL_MAIN, width=3)
    for dot_x in (cx - 22, cx, cx + 22):
        draw.ellipse((dot_x - 7, cy - 10, dot_x + 7, cy + 4), fill=TEAL_DEEP)

    for sx, sy, color in ((cx - 58, cy - 48, TEAL_CYAN), (cx + 62, cy - 36, TEAL_BRIGHT), (cx + 54, cy + 42, TEAL_MAIN)):
        draw.ellipse((sx - 10, sy - 10, sx + 10, sy + 10), fill=color)
        draw.line((sx - 14, sy, sx + 14, sy), fill=WHITE, width=2)
        draw.line((sx, sy - 14, sx, sy + 14), fill=WHITE, width=2)

    bar_y = cy + bubble_h // 2 + 8
    for i, color in enumerate((TEAL_DEEP, TEAL_MAIN, TEAL_BRIGHT)):
        draw.rounded_rectangle((cx - 36 + i * 26, bar_y, cx - 18 + i * 26, bar_y + 18), radius=4, fill=color)


def _draw_wrapped_title(draw: ImageDraw.ImageDraw, x: int, y: int, max_w: int, lines: list[str]) -> int:
    return _draw_centered_title_block(draw, x, x + max_w, y, lines)


def _diagonal_split_x(w: int, h: int, y: int) -> int:
    """X coordinate of navy/white diagonal at height y."""
    split_top = int(w * 0.54)
    split_bottom = int(w * 0.34)
    if h <= 0:
        return split_bottom
    return split_top + int((split_bottom - split_top) * (y / h))


def _paste_armorait_logo(img: Image.Image, w: int, h: int) -> tuple[int, int, int, int] | None:
    """Paste large ARMORA logo bottom-center on white panel. Returns bounding box."""
    if not BRAND_LOGO.is_file():
        return None
    logo = Image.open(BRAND_LOGO).convert('RGBA')
    pad_bottom = 16
    target_h = max(88, int(h * 0.22))
    target_w = int(logo.width * (target_h / logo.height))
    max_w = int(w * 0.40)
    if target_w > max_w:
        target_w = max_w
        target_h = int(logo.height * (target_w / logo.width))
    logo = logo.resize((target_w, target_h), RESAMPLE)

    y = h - target_h - pad_bottom
    split_x = _diagonal_split_x(w, h, y + target_h // 2)
    x = split_x + max(16, (w - split_x - target_w) // 2)
    x = min(x, w - target_w - 16)
    img.paste(logo, (x, y), logo)
    return (x, y, target_w, target_h)


def draw_banner(w: int, h: int) -> Image.Image:
    """Apps Store card cover: rich navy gradient panel, illustration, bold title."""
    img = Image.new('RGB', (w, h), '#F8FAFC')
    draw = ImageDraw.Draw(img)
    split_mid = _draw_diagonal_cover_background(img, w, h)

    radius = int(min(w, h) * 0.24)
    _draw_cover_illustration(draw, int(w * 0.27), h // 2, radius)

    _paste_armorait_logo(img, w, h)

    panel_left = split_mid - 20
    title_y = int(h * 0.26)
    _draw_centered_title_block(
        draw,
        panel_left,
        w - 24,
        title_y,
        ['AI COPILOT', 'FOR ODOO'],
    )
    sub = 'Enterprise AI Operating Layer'
    sub_font = _font(17)
    stw, sth = _text_size(draw, sub, sub_font)
    draw.text(
        (panel_left + (w - 24 - panel_left - stw) // 2, int(h * 0.58)),
        sub,
        font=sub_font,
        fill='#475569',
    )

    # Website pill top-right on white panel (avoids overlap with bottom logo)
    pill_text = 'www.armorait.com'
    pill_font = _font(13, True)
    tw, th = _text_size(draw, pill_text, pill_font)
    pill_w = tw + 36
    pill_h = th + 16
    pill_x = w - pill_w - 24
    pill_y = 20
    _draw_gradient_rounded_rect(
        img,
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        pill_h // 2,
        pill_text,
        pill_font,
    )
    return img


def draw_icon(size: int = 256) -> Image.Image:
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _rounded_rect(draw, (8, 8, size - 8, size - 8), size // 5, PURPLE_LIGHT)
    bubble = (size * 0.18, size * 0.28, size * 0.82, size * 0.72)
    _rounded_rect(draw, bubble, 24, WHITE)
    for i, cx in enumerate((0.38, 0.5, 0.62)):
        x = int(size * cx)
        y = int(size * 0.48)
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=PURPLE_DARK)
    draw.polygon(
        [(int(size * 0.28), int(size * 0.72)), (int(size * 0.36), int(size * 0.86)), (int(size * 0.42), int(size * 0.72))],
        fill=WHITE,
    )
    return img


def workflow_frames() -> list[Image.Image]:
    """Six-step demo: Observe -> Reason -> Decide -> Act -> Explain -> Audit."""
    return [
        draw_systray_scene(
            'Step 1 / 6',
            'Observe: ask from anywhere in Odoo',
            [{'role': 'user', 'headline': '', 'body': 'Show pending quotations', 'height': 72}],
            draft='Show pending quotations',
        ),
        draw_systray_scene(
            'Step 2 / 6',
            'Reason: AI maps intent to the right skill',
            [
                {'role': 'user', 'headline': '', 'body': 'Show pending quotations', 'height': 72},
                {
                    'role': 'assistant',
                    'headline': '12 quotations waiting',
                    'body': 'Total value: ₹ 18,60,000\nTop customer: ABC Textiles',
                    'actions': [('Open list', PURPLE), ('Create quotation', ACCENT)],
                    'height': 150,
                },
            ],
        ),
        draw_systray_scene(
            'Step 3 / 6',
            'Decide: session memory understands follow-ups',
            [
                {'role': 'user', 'headline': '', 'body': 'Email the first three customers', 'height': 72},
                {
                    'role': 'assistant',
                    'headline': 'Confirm email to 3 customers',
                    'body': 'ABC Textiles, Metro Fabrics, Sunrise Garments',
                    'actions': [('Confirm', SUCCESS), ('Cancel', MUTED)],
                    'height': 130,
                },
            ],
            draft='Email the first three customers',
        ),
        draw_systray_scene(
            'Step 4 / 6',
            'Act: write skills run through Odoo ORM',
            [
                {
                    'role': 'system',
                    'headline': 'Action confirmed',
                    'body': 'send_partner_email executed with your permissions.',
                    'height': 88,
                },
                {
                    'role': 'assistant',
                    'headline': '3 follow-up emails queued',
                    'body': 'Draft messages are ready in Discuss.',
                    'actions': [('Open emails', PURPLE)],
                    'height': 120,
                },
            ],
        ),
        draw_systray_scene(
            'Step 5 / 6',
            'Explain: clear answers with suggested next steps',
            [
                {
                    'role': 'assistant',
                    'headline': 'Collections update',
                    'body': '₹ 24L still pending. 12 invoices overdue.\nSuggested: send payment reminders.',
                    'actions': [('Send reminders', WARNING), ('Open invoices', PURPLE)],
                    'height': 140,
                },
            ],
        ),
        draw_audit_scene(),
    ]


def save_png(img: Image.Image, name: str, size: tuple[int, int] | None = None) -> None:
    out = img
    if size:
        out = img.resize(size, RESAMPLE)
    path = OUT / name
    if out.mode == 'RGBA' and name.endswith('.png'):
        out.save(path, 'PNG', optimize=True)
    else:
        out.convert('RGB').save(path, 'PNG', optimize=True)


def save_gif(frames: list[Image.Image], name: str, duration_ms: int = 1400) -> None:
    rgb_frames = [f.convert('RGB') for f in frames]
    path = OUT / name
    rgb_frames[0].save(
        path,
        save_all=True,
        append_images=rgb_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
    )


def save_mobile(img: Image.Image, name: str) -> None:
    w, h = img.size
    crop = img.crop((w - 420, 0, w, h))
    mobile = crop.resize((390, 720), RESAMPLE)
    # Phone chrome
    framed = Image.new('RGB', (430, 780), '#111827')
    framed.paste(mobile, (20, 30))
    draw = ImageDraw.Draw(framed)
    draw.ellipse((195, 12, 235, 20), fill='#374151')
    framed.save(OUT / name, 'PNG', optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    overview = draw_systray_scene(
        'Live demo',
        'Ask, reason, and act from the systray copilot',
        [
            {'role': 'user', 'headline': '', 'body': 'Show pending quotations', 'height': 72},
            {
                'role': 'assistant',
                'headline': '12 quotations waiting',
                'body': 'Total value: ₹ 18,60,000',
                'actions': [('Open list', PURPLE), ('Email top 3', ACCENT)],
                'height': 140,
            },
        ],
    )
    settings = draw_settings_scene()
    tools = draw_tools_scene()
    audit = draw_audit_scene()
    listing = draw_list_scene()
    briefing = draw_briefing_scene()
    banner = draw_banner(1200, 600)
    icon = draw_icon(256)

    save_png(icon, 'icon.png')
    save_png(banner, 'banner_small.png', (360, 180))
    save_png(banner, 'banner.png')
    save_png(banner, 'main_screenshot.png', (1200, 600))
    save_png(overview, 'overview.png')
    save_png(settings, 'settings.png')
    save_png(tools, 'tools.png')
    save_png(audit, 'report.png')
    save_png(listing, 'list.png')
    save_png(audit, 'form.png')
    save_png(briefing, 'dashboard.png')
    save_png(overview, 'wizard.png')
    save_png(overview, 'kanban.png')
    save_png(listing, 'search.png')
    save_mobile(overview, 'mobile.png')

    frames = workflow_frames()
    save_gif(frames, 'workflow.gif', duration_ms=1600)
    save_gif([overview, settings], 'hero.gif', duration_ms=2000)
    save_gif([briefing, overview], 'dashboard.gif', duration_ms=1800)
    save_gif([settings, tools], 'settings.gif', duration_ms=1800)
    save_gif([audit, tools], 'reports.gif', duration_ms=1800)
    save_gif(frames[:3], 'mobile.gif', duration_ms=1500)

    print(f'Generated marketplace assets in {OUT}')
    for p in sorted(OUT.glob('*')):
        if p.suffix.lower() in {'.png', '.gif'}:
            print(f'  {p.name}: {p.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
