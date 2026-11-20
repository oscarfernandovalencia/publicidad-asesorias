#!/usr/bin/env python3
"""
Generador Maestro de Identidad, Avisos Publicitarios y Videos Promocionales (MP4)
Proyecto: publicidad-asesorias — Marca: Asesorías en Ingeniería
Contacto en avisos: Celular / WhatsApp 300 408 3940 • Web: asesoriaseningenieria.github.io • Facebook Messenger
"""

import math
import subprocess
import wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

BASE_DIR = Path("/home/v1rr3eor/IAs/projects/publicidad-asesorias")
ID_DIR = BASE_DIR / "identidad_marca"
RES_DIR = BASE_DIR / "recursos_visuales"
OUT_AVISOS = BASE_DIR / "avisos_publicitarios"
OUT_VIDEOS = BASE_DIR / "videos_campana"

OUT_AVISOS.mkdir(parents=True, exist_ok=True)
OUT_VIDEOS.mkdir(parents=True, exist_ok=True)

# Fonts
FONT_BLACK = "/usr/share/fonts/TTF/AriBlk.TTF"
FONT_COND = "/usr/share/fonts/TTF/UbuntuNerdFont-Condensed.ttf"
FONT_BOLD = "/usr/share/fonts/TTF/Arialbd.TTF"
FONT_REG = "/usr/share/fonts/TTF/Arial.TTF"
FONT_ITAL = "/usr/share/fonts/TTF/Georgiai.TTF"
FONT_ROUNDED = "/usr/share/fonts/TTF/UbuntuNerdFont-Bold.ttf"
FONT_CASUAL = "/usr/share/fonts/TTF/Comicbd.TTF"

# Brand Palette
NAVY = (15, 37, 71)
NAVY_DARK = (9, 22, 46)
ROYAL = (29, 99, 220)
GOLD = (245, 166, 35)
CYAN = (56, 189, 248)
WHITE = (255, 255, 255)
SLATE = (226, 232, 240)
MESSENGER_BLUE = (0, 132, 255)
WA_GREEN = (37, 211, 102)
WA_DARK = (12, 92, 48)

PHONE_DISPLAY = "300 408 3940"
WEB_DISPLAY = "asesoriaseningenieria.github.io"


def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def prepare_brand_logos():
    """Creates transparent PNG logo variants from the brand assets."""
    white_logo_jpg = ID_DIR / "Logo_Principal_Blanco_Asesorias_en_Ingenieria.jpg"
    square_logo_jpg = ID_DIR / "Logo_Perfil_Cuadrado_Facebook_Asesorias_en_Ingenieria.jpg"

    with Image.open(white_logo_jpg) as im:
        rgba = im.convert("RGBA")
        arr = np.array(rgba)
        is_white = (arr[:, :, 0] > 238) & (arr[:, :, 1] > 238) & (arr[:, :, 2] > 238)
        arr[is_white, 3] = 0
        trans_main = Image.fromarray(arr, mode="RGBA")
        bbox = trans_main.getbbox()
        if bbox:
            trans_main = trans_main.crop(bbox)
        trans_main.save(ID_DIR / "Logo_Principal_Transparente.png")

    with Image.open(square_logo_jpg) as im:
        sq = im.convert("RGBA")
        w, h = sq.size
        ss = 2
        mask = Image.new("L", (w * ss, h * ss), 0)
        ImageDraw.Draw(mask).ellipse((6, 6, w * ss - 7, h * ss - 7), fill=255)
        mask = mask.resize((w, h), Image.Resampling.LANCZOS)
        badge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        badge.paste(sq, (0, 0), mask)
        bdraw = ImageDraw.Draw(badge)
        bdraw.ellipse((4, 4, w - 5, h - 5), outline=GOLD + (255,), width=10)
        badge.save(ID_DIR / "Logo_Badge_Transparente.png")

    return (
        Image.open(ID_DIR / "Logo_Principal_Transparente.png").convert("RGBA"),
        Image.open(ID_DIR / "Logo_Badge_Transparente.png").convert("RGBA"),
    )


def load_fit(img_path: Path, w: int, h: int, contrast: float = 1.06) -> Image.Image:
    with Image.open(img_path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        if contrast != 1.0:
            im = ImageEnhance.Contrast(im).enhance(contrast)
            im = ImageEnhance.Color(im).enhance(1.06)
        return ImageOps.fit(im, (w, h), method=Image.Resampling.LANCZOS)


def draw_messenger_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 24, bg=WHITE, fg=MESSENGER_BLUE):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    draw.polygon([
        (cx - int(r * 0.65), cy + int(r * 0.55)),
        (cx - int(r * 0.20), cy + int(r * 0.85)),
        (cx - int(r * 0.72), cy + int(r * 0.98)),
    ], fill=bg)
    bolt = [
        (cx - int(r * 0.48), cy + int(r * 0.14)),
        (cx - int(r * 0.08), cy - int(r * 0.28)),
        (cx + int(r * 0.06), cy - int(r * 0.02)),
        (cx + int(r * 0.48), cy - int(r * 0.14)),
        (cx + int(r * 0.08), cy + int(r * 0.28)),
        (cx - int(r * 0.06), cy + int(r * 0.02)),
    ]
    draw.polygon(bolt, fill=fg)


def draw_phone_whatsapp_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 24, bg=WA_GREEN, fg=WHITE):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg, outline=WHITE + (255,), width=2)
    draw.polygon([
        (cx - int(r * 0.70), cy + int(r * 0.52)),
        (cx - int(r * 0.24), cy + int(r * 0.82)),
        (cx - int(r * 0.82), cy + int(r * 0.98)),
    ], fill=bg)
    # Minimalist phone receiver
    draw.arc(
        (cx - int(r * 0.48), cy - int(r * 0.48), cx + int(r * 0.48), cy + int(r * 0.48)),
        start=20,
        end=220,
        fill=fg,
        width=max(3, int(r * 0.22)),
    )
    draw.ellipse((cx - int(r * 0.46), cy - int(r * 0.34), cx - int(r * 0.14), cy - int(r * 0.02)), fill=fg)
    draw.ellipse((cx + int(r * 0.12), cy + int(r * 0.16), cx + int(r * 0.44), cy + int(r * 0.48)), fill=fg)


def draw_globe_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 20, fg=CYAN, bg=NAVY_DARK):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg + (255,), outline=fg + (255,), width=3)
    draw.ellipse((cx - int(r * 0.48), cy - r, cx + int(r * 0.48), cy + r), outline=fg + (255,), width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=fg + (255,), width=2)
    draw.line([(cx - int(r * 0.85), cy - int(r * 0.45)), (cx + int(r * 0.85), cy - int(r * 0.45))], fill=fg + (255,), width=2)
    draw.line([(cx - int(r * 0.85), cy + int(r * 0.45)), (cx + int(r * 0.85), cy + int(r * 0.45))], fill=fg + (255,), width=2)


def draw_check_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 18, bg=GOLD, fg=NAVY_DARK):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    p1 = (cx - int(r * 0.42), cy + int(r * 0.05))
    p2 = (cx - int(r * 0.10), cy + int(r * 0.38))
    p3 = (cx + int(r * 0.48), cy - int(r * 0.34))
    draw.line([p1, p2, p3], fill=fg, width=4, joint="curve")


def draw_centered_text(draw: ImageDraw.ImageDraw, y: int, text: str, font, fill, canvas_w: int, x_offset: int = 0):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((x_offset + (canvas_w - tw) // 2, y), text, font=font, fill=fill)


def paste_rounded_photo(canvas: Image.Image, photo_path: Path, box: tuple, radius: int = 28, border_px: int = 5, border_col=GOLD):
    x0, y0, x1, y1 = box
    pw, ph = x1 - x0, y1 - y0
    im = load_fit(photo_path, pw, ph)
    paste_rounded_image(canvas, im, box, radius=radius, border_px=border_px, border_col=border_col)


def paste_rounded_image(canvas: Image.Image, im: Image.Image, box: tuple, radius: int = 28, border_px: int = 5, border_col=GOLD):
    x0, y0, x1, y1 = box
    pw, ph = x1 - x0, y1 - y0
    if im.size != (pw, ph):
        im = ImageOps.fit(im, (pw, ph), method=Image.Resampling.LANCZOS)
    ss = 2
    mask = Image.new("L", (pw * ss, ph * ss), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw * ss - 1, ph * ss - 1), radius=radius * ss, fill=255)
    mask = mask.resize((pw, ph), Image.Resampling.LANCZOS)

    if border_px > 0:
        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle(
            (x0 - border_px, y0 - border_px, x1 + border_px, y1 + border_px),
            radius=radius + border_px,
            fill=border_col + (255,),
        )
    canvas.paste(im, (x0, y0), mask)


def draw_dual_contact_bar(
    canvas: Image.Image,
    box: tuple,
    phone_label: str = "CEL / WHATSAPP: 300 408 3940",
    web_label: str = WEB_DISPLAY,
    sub_note: str = "Clases Online y Presenciales • También por Facebook Messenger",
    bg=NAVY,
    outline=CYAN,
    lang: str = "es",
):
    """High-contrast contact bar featuring phone 300 408 3940, website URL, and Messenger note."""
    draw = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0

    draw.rounded_rectangle(box, radius=24, fill=bg + (248,), outline=outline + (255,), width=3)

    if h >= 130:
        # Upper row: split Phone pill + Web pill
        pad = 16
        gap = 14
        col_w = (w - 2 * pad - gap) // 2
        pill_y0 = y0 + 14
        pill_y1 = y0 + int(h * 0.62)
        cy_p = (pill_y0 + pill_y1) // 2

        # Left pill: Phone / WhatsApp
        draw.rounded_rectangle((x0 + pad, pill_y0, x0 + pad + col_w, pill_y1), radius=16, fill=WA_DARK + (255,), outline=WA_GREEN + (255,), width=2)
        draw_phone_whatsapp_icon(draw, x0 + pad + 34, cy_p, r=20, bg=WA_GREEN, fg=WHITE)
        f_lbl = get_font(FONT_BOLD, 16 if w < 900 else 17)
        f_val = get_font(FONT_BLACK, 26 if w < 900 else 30)
        lbl_phone = "PHONE / WHATSAPP" if lang == "en" else "CELULAR / WHATSAPP"
        lbl_web = "INTERACTIVE STUDY GUIDES" if lang == "en" else "MATERIAL Y TEORÍA INTERACTIVA"
        draw.text((x0 + pad + 64, pill_y0 + 8), lbl_phone, font=f_lbl, fill=(185, 255, 210, 255))
        draw.text((x0 + pad + 64, pill_y0 + 30), PHONE_DISPLAY, font=f_val, fill=WHITE + (255,))

        # Right pill: Website
        wx0 = x0 + pad + col_w + gap
        draw.rounded_rectangle((wx0, pill_y0, x1 - pad, pill_y1), radius=16, fill=(16, 52, 108, 255), outline=CYAN + (255,), width=2)
        draw_globe_icon(draw, wx0 + 32, cy_p, r=19, fg=CYAN, bg=NAVY_DARK)
        f_web_lbl = get_font(FONT_BOLD, 15 if w < 900 else 17)
        f_web = get_font(FONT_BLACK, 19 if w < 900 else 22)
        draw.text((wx0 + 60, pill_y0 + 9), lbl_web, font=f_web_lbl, fill=GOLD + (255,))
        draw.text((wx0 + 60, pill_y0 + 34), web_label, font=f_web, fill=WHITE + (255,))

        # Bottom subnote row with Messenger icon
        bot_cy = (pill_y1 + y1) // 2
        f_sub = get_font(FONT_BOLD, 19 if w >= 900 else 17)
        bb = draw.textbbox((0, 0), sub_note, font=f_sub)
        tw = bb[2] - bb[0]
        sx = x0 + (w - tw - 36) // 2
        draw_messenger_icon(draw, sx + 12, bot_cy, r=13, bg=WHITE, fg=MESSENGER_BLUE)
        draw.text((sx + 34, bot_cy - 11), sub_note, font=f_sub, fill=GOLD + (255,))
    else:
        # Compact banner version (for Facebook cover 796x120)
        draw_phone_whatsapp_icon(draw, x0 + 46, y0 + h // 2, r=24, bg=WA_GREEN, fg=WHITE)
        draw.text((x0 + 84, y0 + 16), phone_label, font=get_font(FONT_BLACK, 26), fill=WHITE + (255,))
        draw_globe_icon(draw, x0 + 46 + 440, y0 + 31, r=14, fg=CYAN, bg=NAVY_DARK)
        draw.text((x0 + 46 + 464, y0 + 18), web_label, font=get_font(FONT_BLACK, 21), fill=CYAN + (255,))
        draw_messenger_icon(draw, x0 + 95, y0 + 78, r=13, bg=WHITE, fg=MESSENGER_BLUE)
        draw.text((x0 + 118, y0 + 65), sub_note, font=get_font(FONT_BOLD, 19), fill=GOLD + (255,))


def make_facebook_cover(badge_logo: Image.Image):
    """Generates 1640x624 Facebook Page Cover Banner."""
    W, H = 1640, 624
    canvas = Image.new("RGBA", (W, H), NAVY_DARK + (255,))
    draw = ImageDraw.Draw(canvas)

    for gx in range(0, W, 60):
        draw.line([(gx, 0), (gx, H)], fill=(22, 48, 90, 255), width=1)
    for gy in range(0, H, 60):
        draw.line([(0, gy), (W, gy)], fill=(22, 48, 90, 255), width=1)

    photo = load_fit(RES_DIR / "hero_escritorio_ingenieria.jpg", 940, H)
    canvas.paste(photo, (700, 0))
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad)
    for x in range(680, 1280):
        alpha = int(255 * (1.0 - (x - 680) / 600.0))
        gdraw.line([(x, 0), (x, H)], fill=NAVY_DARK + (max(0, min(255, alpha)),))
    gdraw.rectangle((0, 0, 680, H), fill=NAVY_DARK + (255,))
    canvas = Image.alpha_composite(canvas, grad)
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, W, 10), fill=GOLD + (255,))

    b_rs = badge_logo.resize((170, 170), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (64, 48), b_rs)

    draw.text((260, 62), "ASESORÍAS EN", font=get_font(FONT_BLACK, 52), fill=WHITE + (255,))
    draw.text((260, 122), "INGENIERÍA", font=get_font(FONT_BLACK, 64), fill=GOLD + (255,))
    draw.text((260, 200), "Clases Particulares • Tutorías Online • Material Interactivo", font=get_font(FONT_BOLD, 24), fill=CYAN + (255,))

    pills = [
        "Matemáticas y Cálculo",
        "Física y Estática",
        "Estructuras NSR-10",
        "Python & Programación",
    ]
    px, py = 64, 276
    f_pill = get_font(FONT_BOLD, 23)
    for ptxt in pills:
        bb = draw.textbbox((0, 0), ptxt, font=f_pill)
        pw = (bb[2] - bb[0]) + 42
        if px + pw > 920:
            px = 64
            py += 60
        draw.rounded_rectangle((px, py, px + pw, py + 46), radius=23, fill=NAVY + (235,), outline=CYAN + (255,), width=2)
        draw.text((px + 21, py + 10), ptxt, font=f_pill, fill=WHITE + (255,))
        px += pw + 16

    draw_dual_contact_bar(
        canvas,
        (64, 444, 960, 566),
        phone_label=f"CEL / WHATSAPP: {PHONE_DISPLAY}",
        web_label=WEB_DISPLAY,
        sub_note="Atención rápida por WhatsApp y Facebook Messenger • Horarios flexibles",
        bg=ROYAL,
    )

    out_path = ID_DIR / "Banner_Portada_Facebook_Asesorias_en_Ingenieria.png"
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def make_ad_4x5_or_1x1(
    out_name: str,
    size: tuple,
    badge_txt: str,
    title_l1: str,
    title_l2: str,
    subtitle: str,
    bullets: list,
    photo_path: Path,
    badge_logo: Image.Image,
    accent_color=GOLD,
    sub_note="Escríbenos por WhatsApp o Facebook Messenger • Online y Presencial",
):
    W, H = size
    canvas = Image.new("RGBA", (W, H), NAVY_DARK + (255,))
    draw = ImageDraw.Draw(canvas)

    for gx in range(0, W, 54):
        draw.line([(gx, 0), (gx, H)], fill=(18, 42, 82, 255), width=1)
    for gy in range(0, H, 54):
        draw.line([(0, gy), (W, gy)], fill=(18, 42, 82, 255), width=1)

    draw.rectangle((0, 0, W, 12), fill=accent_color + (255,))

    f_badge = get_font(FONT_BLACK, 24)
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge)
    bw = (bb[2] - bb[0]) + 46
    draw.rounded_rectangle((54, 38, 54 + bw, 86), radius=24, fill=accent_color + (255,))
    draw.text((77, 48), badge_txt, font=f_badge, fill=NAVY_DARK + (255,))

    l_size = 132
    b_rs = badge_logo.resize((l_size, l_size), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (W - l_size - 48, 28), b_rs)

    draw.text((54, 108), title_l1, font=get_font(FONT_BLACK, 52), fill=WHITE + (255,))
    draw.text((54, 170), title_l2, font=get_font(FONT_BLACK, 52), fill=accent_color + (255,))
    draw.text((54, 238), subtitle, font=get_font(FONT_BOLD, 25), fill=CYAN + (255,))

    photo_y0 = 286
    photo_h = 370 if H >= 1300 else 230
    paste_rounded_photo(canvas, photo_path, (54, photo_y0, W - 54, photo_y0 + photo_h), radius=28, border_px=4, border_col=accent_color)

    list_y0 = photo_y0 + photo_h + 24
    cta_h = 148
    cta_y0 = H - cta_h - 32
    draw.rounded_rectangle((54, list_y0, W - 54, cta_y0 - 20), radius=24, fill=NAVY + (235,), outline=(44, 82, 140, 255), width=2)

    cy = list_y0 + 24
    f_bul = get_font(FONT_BOLD, 26 if H >= 1300 else 23)
    step_y = 66 if H >= 1300 else 50
    for item in bullets:
        draw_check_circle(draw, 98, cy + 16, r=16, bg=accent_color, fg=NAVY_DARK)
        draw.text((132, cy), item, font=f_bul, fill=WHITE + (255,))
        cy += step_y

    draw_dual_contact_bar(canvas, (54, cta_y0, W - 54, cta_y0 + cta_h), sub_note=sub_note, bg=NAVY, outline=accent_color)

    out_path = OUT_AVISOS / out_name
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def make_vertical_story_9x16(
    out_name: str,
    badge_txt: str,
    title_l1: str,
    title_l2: str,
    subtitle: str,
    bullets: list,
    photo_top: Path,
    photo_bottom_left: Path,
    photo_bottom_right: Path,
    badge_logo: Image.Image,
    accent_color=GOLD,
):
    W, H = 1080, 1920
    canvas = Image.new("RGBA", (W, H), NAVY_DARK + (255,))
    draw = ImageDraw.Draw(canvas)

    for gx in range(0, W, 60):
        draw.line([(gx, 0), (gx, H)], fill=(18, 42, 82, 255), width=1)
    for gy in range(0, H, 60):
        draw.line([(0, gy), (W, gy)], fill=(18, 42, 82, 255), width=1)

    draw.rectangle((0, 0, W, 16), fill=accent_color + (255,))

    b_rs = badge_logo.resize((176, 176), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (W - 226, 44), b_rs)

    f_badge = get_font(FONT_BLACK, 28)
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge)
    bw = (bb[2] - bb[0]) + 48
    draw.rounded_rectangle((56, 56, 56 + bw, 114), radius=29, fill=accent_color + (255,))
    draw.text((80, 68), badge_txt, font=f_badge, fill=NAVY_DARK + (255,))

    draw.text((56, 146), "ASESORÍAS EN INGENIERÍA", font=get_font(FONT_BOLD, 30), fill=CYAN + (255,))
    draw.text((56, 232), title_l1, font=get_font(FONT_BLACK, 64), fill=WHITE + (255,))
    draw.text((56, 308), title_l2, font=get_font(FONT_BLACK, 64), fill=accent_color + (255,))
    draw.text((56, 396), subtitle, font=get_font(FONT_BOLD, 31), fill=SLATE + (255,))

    paste_rounded_photo(canvas, photo_top, (56, 465, W - 56, 975), radius=34, border_px=5, border_col=accent_color)
    paste_rounded_photo(canvas, photo_bottom_left, (56, 1005, 522, 1270), radius=26, border_px=4, border_col=CYAN)
    paste_rounded_photo(canvas, photo_bottom_right, (558, 1005, W - 56, 1270), radius=26, border_px=4, border_col=CYAN)

    cy = 1310
    f_bul = get_font(FONT_BOLD, 31)
    for b in bullets:
        draw_check_circle(draw, 94, cy + 18, r=18, bg=accent_color, fg=NAVY_DARK)
        draw.text((134, cy), b, font=f_bul, fill=WHITE + (255,))
        cy += 74

    draw_dual_contact_bar(
        canvas,
        (56, 1650, W - 56, 1858),
        sub_note="Aprende teoría en la web o agenda por WhatsApp / Facebook Messenger",
        bg=NAVY,
        outline=accent_color,
    )

    out_path = OUT_AVISOS / out_name
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


# ==============================================================================
# NUEVOS AVISOS MEJORADOS A PARTIR DE `recursos_visuales/`
# ==============================================================================

def draw_isometric_channel_beam(canvas: Image.Image, box: tuple):
    """Renders crisp vector 3D isometric U-channel beam (4.0 in, 0.2 in, 12.0 in, y/z axes)."""
    draw = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=24, fill=(248, 250, 255, 255), outline=CYAN + (255,), width=4)

    # Coordinate basis inside box
    ox = x0 + 240
    oy = y0 + 298
    # Isometric projection vectors: +z (front-right), +y (up), +x_depth (back-right-up)
    z_vec = (232.0, 40.0)
    d_vec = (275.0, -186.0)
    h_vec = (0.0, -96.0)

    def pt(uz, ud, uh):
        return (
            ox + uz * z_vec[0] + ud * d_vec[0] + uh * h_vec[0],
            oy + uz * z_vec[1] + ud * d_vec[1] + uh * h_vec[1],
        )

    flange_blue = (76, 138, 206, 255)
    flange_dark = (58, 114, 178, 255)
    flange_top = (106, 164, 224, 255)
    core_gold = (254, 220, 128, 255)
    core_gold_edge = (232, 172, 48, 255)
    edge_col = (28, 56, 98, 255)

    t = 0.09  # wall thickness ratio

    # Back-top and inner core block (gold infill showing composite / web)
    core_front = [pt(t, 0, 0.14), pt(1 - t, 0, 0.14), pt(1 - t, 0, 1.0), pt(t, 0, 1.0)]
    core_top = [pt(t, 0, 1.0), pt(1 - t, 0, 1.0), pt(1 - t, 1, 1.0), pt(t, 1, 1.0)]
    draw.polygon(core_top, fill=core_gold, outline=core_gold_edge, width=2)
    draw.polygon(core_front, fill=(252, 208, 102, 255), outline=core_gold_edge, width=2)

    # Right vertical flange (outer face along d)
    r_side = [pt(1, 0, -0.18), pt(1, 1, -0.18), pt(1, 1, 1.05), pt(1, 0, 1.05)]
    draw.polygon(r_side, fill=flange_dark, outline=edge_col, width=2)
    r_top = [pt(1 - t, 0, 1.05), pt(1, 0, 1.05), pt(1, 1, 1.05), pt(1 - t, 1, 1.05)]
    draw.polygon(r_top, fill=flange_top, outline=edge_col, width=2)

    # Left vertical flange (top face along d)
    l_top = [pt(0, 0, 1.05), pt(t, 0, 1.05), pt(t, 1, 1.05), pt(0, 1, 1.05)]
    draw.polygon(l_top, fill=flange_top, outline=edge_col, width=2)

    # Horizontal web connecting flanges near bottom
    web_front = [pt(t, 0, 0.0), pt(1 - t, 0, 0.0), pt(1 - t, 0, 0.14), pt(t, 0, 0.14)]
    draw.polygon(web_front, fill=flange_blue, outline=edge_col, width=2)

    # Front faces of left and right flanges
    l_front = [pt(0, 0, -0.18), pt(t, 0, -0.18), pt(t, 0, 1.05), pt(0, 0, 1.05)]
    r_front = [pt(1 - t, 0, -0.18), pt(1, 0, -0.18), pt(1, 0, 1.05), pt(1 - t, 0, 1.05)]
    draw.polygon(l_front, fill=flange_blue, outline=edge_col, width=2)
    draw.polygon(r_front, fill=flange_blue, outline=edge_col, width=2)

    # Coordinate Axes (y upward, z along front)
    y_top = pt(0, 0, 1.78)
    z_end = pt(1.38, 0, 0)
    origin_p = pt(0, 0, 0)
    draw.line([origin_p, y_top], fill=(20, 28, 44, 255), width=3)
    draw.line([origin_p, z_end], fill=(20, 28, 44, 255), width=3)
    # Arrowheads
    draw.polygon([(y_top[0], y_top[1] - 8), (y_top[0] - 6, y_top[1] + 6), (y_top[0] + 6, y_top[1] + 6)], fill=(20, 28, 44, 255))
    draw.polygon([(z_end[0] + 8, z_end[1] + 2), (z_end[0] - 6, z_end[1] - 6), (z_end[0] - 8, z_end[1] + 7)], fill=(20, 28, 44, 255))
    f_ax = get_font(FONT_ITAL, 28)
    draw.text((y_top[0] - 28, y_top[1] - 8), "y", font=f_ax, fill=NAVY + (255,))
    draw.text((z_end[0] - 6, z_end[1] + 12), "z", font=f_ax, fill=NAVY + (255,))

    # Dimension arrows: 4.0 in, 0.2 in, 12.0 in
    def dim_arrow_v(x, ya, yb, label):
        draw.line([(x, ya), (x, yb)], fill=ROYAL + (255,), width=3)
        draw.polygon([(x, ya), (x - 6, ya + 11), (x + 6, ya + 11)], fill=ROYAL + (255,))
        draw.polygon([(x, yb), (x - 6, yb - 11), (x + 6, yb - 11)], fill=ROYAL + (255,))
        f_d = get_font(FONT_BOLD, 22)
        bb = draw.textbbox((0, 0), label, font=f_d)
        draw.text((x - (bb[2] - bb[0]) - 12, (ya + yb) // 2 - 12), label, font=f_d, fill=NAVY + (255,))

    dim_arrow_v(ox - 26, int(pt(0, 0, 1.05)[1]), int(pt(0, 0, 0.14)[1]), "4.0 in")
    dim_arrow_v(ox - 26, int(pt(0, 0, 0.14)[1]), int(pt(0, 0, -0.18)[1]), "0.2 in")

    p_bl = pt(0, 0, -0.35)
    p_br = pt(1, 0, -0.35)
    draw.line([p_bl, p_br], fill=ROYAL + (255,), width=3)
    draw.polygon([(p_bl[0], p_bl[1]), (p_bl[0] + 12, p_bl[1] - 5), (p_bl[0] + 10, p_bl[1] + 7)], fill=ROYAL + (255,))
    draw.polygon([(p_br[0], p_br[1]), (p_br[0] - 10, p_br[1] - 7), (p_br[0] - 12, p_br[1] + 5)], fill=ROYAL + (255,))
    draw.text(((p_bl[0] + p_br[0]) / 2 - 36, (p_bl[1] + p_br[1]) / 2 + 12), "12.0 in", font=get_font(FONT_BOLD, 24), fill=NAVY + (255,))

    # Technical tag inside card
    draw.rounded_rectangle((x0 + 20, y0 + 18, x0 + 422, y0 + 56), radius=10, fill=NAVY + (255,))
    draw.text((x0 + 36, y0 + 26), "ANÁLISIS DE SECCIONES E INERCIA", font=get_font(FONT_BLACK, 17), fill=GOLD + (255,))


def make_aviso_06_viga_canal(badge_logo: Image.Image) -> Path:
    """Aviso 06 (4:5): Redesigned from 273834643_... with crisp 3D U-channel CAD diagram."""
    W, H = 1080, 1350
    canvas = Image.new("RGBA", (W, H), NAVY_DARK + (255,))
    draw = ImageDraw.Draw(canvas)

    for gx in range(0, W, 48):
        draw.line([(gx, 0), (gx, H)], fill=(18, 42, 82, 255), width=1)
    for gy in range(0, H, 48):
        draw.line([(0, gy), (W, gy)], fill=(18, 42, 82, 255), width=1)
    draw.rectangle((0, 0, W, 14), fill=GOLD + (255,))

    b_rs = badge_logo.resize((136, 136), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (W - 182, 28), b_rs)

    draw.rounded_rectangle((54, 34, 490, 78), radius=22, fill=CYAN + (255,))
    draw.text((76, 43), "ASESORÍAS EN INGENIERÍA", font=get_font(FONT_BLACK, 22), fill=NAVY_DARK + (255,))
    draw.text((54, 98), "CLASES PARTICULARES", font=get_font(FONT_BLACK, 56), fill=WHITE + (255,))
    draw.text((54, 162), "MATEMÁTICAS E INGENIERÍA", font=get_font(FONT_BLACK, 44), fill=GOLD + (255,))

    # Crisp 3D U-Channel Beam Diagram Card
    draw_isometric_channel_beam(canvas, (54, 240, W - 54, 656))

    # 2-Column Subjects Card
    draw.rounded_rectangle((54, 676, W - 54, 1136), radius=24, fill=NAVY + (240,), outline=CYAN + (180,), width=2)
    draw.text((84, 700), "ÁREAS DE CLASE, TALLERES Y PARCIALES:", font=get_font(FONT_BLACK, 25), fill=GOLD + (255,))

    subjects = [
        ("Matemáticas y Cálculo", "Álgebra, Cálculo I/II/III y Ecuaciones"),
        ("Física Mecánica", "Cinemática, Dinámica, Trabajo y Energía"),
        ("Geometría Vectorial", "Vectores R2/R3, Rectas, Planos y Cónicas"),
        ("Geometría Euclidiana", "Triángulos, Congruencia y Demostraciones"),
        ("Estática Vectorial", "Equilibrio 2D/3D, Armaduras y Centroides"),
        ("Resistencia de Materiales", "Esfuerzos, Inercia, Torsión y Flexión"),
    ]
    col_w = 456
    for idx, (stitle, sdesc) in enumerate(subjects):
        col = idx % 2
        row = idx // 2
        cx = 84 + col * (col_w + 26)
        cy = 758 + row * 120
        draw.rounded_rectangle((cx, cy, cx + col_w, cy + 102), radius=16, fill=(11, 28, 56, 255), outline=(44, 86, 148, 255), width=2)
        draw_check_circle(draw, cx + 32, cy + 38, r=16, bg=GOLD, fg=NAVY_DARK)
        draw.text((cx + 60, cy + 20), stitle, font=get_font(FONT_BLACK, 24), fill=WHITE + (255,))
        draw.text((cx + 60, cy + 56), sdesc, font=get_font(FONT_REG, 19), fill=CYAN + (255,))

    draw_dual_contact_bar(
        canvas,
        (54, 1160, W - 54, 1314),
        sub_note="Aprende teoría paso a paso en la web o agenda por WhatsApp / Facebook",
        bg=NAVY,
        outline=GOLD,
    )

    out_path = OUT_AVISOS / "Aviso_06_Viga_Canal_Estatica_Resistencia_Materiales_4x5.png"
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def make_aviso_07_pizarra_formulas(badge_logo: Image.Image) -> Path:
    """Aviso 07 (4:5): Combines clean chalkboard formulas (479543451) + student at blackboard (472256570)."""
    W, H = 1080, 1350
    canvas = Image.new("RGBA", (W, H), (22, 26, 30, 255))

    # Top background: clean chalkboard formulas
    chalk_bg = load_fit(RES_DIR / "479543451_3848757458788120_113036427974149033_n.jpg", W, 620, contrast=1.15)
    canvas.paste(chalk_bg, (0, 0))
    scrim = Image.new("RGBA", (W, 620), (14, 24, 38, 175))
    canvas.paste(scrim, (0, 0), scrim)
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, W, 12), fill=GOLD + (255,))
    b_rs = badge_logo.resize((138, 138), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (W - 182, 28), b_rs)

    draw.rounded_rectangle((54, 36, 490, 80), radius=22, fill=GOLD + (255,))
    draw.text((76, 45), "ASESORÍAS EN INGENIERÍA", font=get_font(FONT_BLACK, 22), fill=NAVY_DARK + (255,))

    draw.text((54, 108), "¿PROBLEMAS CON LAS", font=get_font(FONT_BLACK, 54), fill=WHITE + (255,))
    draw.text((54, 172), "MATEMÁTICAS O FÍSICA?", font=get_font(FONT_BLACK, 54), fill=GOLD + (255,))
    draw.text((54, 246), "¡NO TE PREOCUPES! COMUNÍCATE CON NOSOTROS", font=get_font(FONT_BLACK, 32), fill=CYAN + (255,))

    # Student at blackboard cropped cleanly (x: 365..896, y: 0..455 -> removes left panel and bottom logo)
    with Image.open(RES_DIR / "472256570_3815891678741365_2097783859479767321_n.jpg") as im:
        student_crop = im.crop((364, 0, 896, 452)).convert("RGB")
        student_crop = ImageEnhance.Contrast(student_crop).enhance(1.08)
    paste_rounded_image(canvas, student_crop, (54, 314, W - 54, 830), radius=28, border_px=5, border_col=GOLD)

    # Bottom explanation & pillars card
    draw.rounded_rectangle((54, 856, W - 54, 1138), radius=24, fill=NAVY + (245,), outline=CYAN + (200,), width=2)
    bullets = [
        "Matemáticas, Álgebra, Trigonometría y Geometría",
        "Cálculo Diferencial, Integral y Ecuaciones Diferenciales",
        "Física Mecánica, Estática y Resistencia de Materiales",
        "Explicación desde cero • Parciales, talleres y trabajos",
    ]
    cy = 884
    for b in bullets:
        draw_check_circle(draw, 98, cy + 16, r=16, bg=GOLD, fg=NAVY_DARK)
        draw.text((134, cy), b, font=get_font(FONT_BOLD, 27), fill=WHITE + (255,))
        cy += 62

    draw_dual_contact_bar(
        canvas,
        (54, 1162, W - 54, 1316),
        sub_note="Clases personalizadas Online o Presenciales • Escríbenos hoy",
        bg=NAVY_DARK,
        outline=GOLD,
    )

    out_path = OUT_AVISOS / "Aviso_07_Problemas_Matematicas_Pizarra_Formulas_4x5.png"
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def make_aviso_08_flatlay_clases_trabajos(badge_logo: Image.Image) -> Path:
    """Aviso 08 (1:1): Uses desk flatlay (472579722) covering old text cleanly with sleek dark editorial cards."""
    W, H = 1080, 1080
    base = load_fit(RES_DIR / "472579722_3817370578593475_8957874031083280338_n.jpg", W, H, contrast=1.06).convert("RGBA")

    # Apply full-opacity navy editorial overlay starting cleanly above the old black text (y >= 240)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for y in range(190, 240):
        alpha = int(255 * ((y - 190) / 50.0))
        odraw.line([(0, y), (W, y)], fill=NAVY_DARK + (alpha,))
    odraw.rectangle((0, 240, W, H), fill=NAVY_DARK + (255,))
    canvas = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(canvas)

    # Top header badge & brand logo
    b_rs = badge_logo.resize((128, 128), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (W - 166, 22), b_rs)

    draw.rounded_rectangle((46, 28, 460, 70), radius=21, fill=GOLD + (255,))
    draw.text((68, 37), "ASESORÍAS EN INGENIERÍA", font=get_font(FONT_BLACK, 20), fill=NAVY_DARK + (255,))

    # Headline Card
    draw.rounded_rectangle((46, 210, W - 46, 368), radius=22, fill=NAVY + (245,), outline=GOLD + (255,), width=3)
    draw.text((74, 228), "CLASES PARTICULARES,", font=get_font(FONT_BLACK, 48), fill=WHITE + (255,))
    draw.text((74, 288), "TALLERES Y TRABAJOS ESCRITOS", font=get_font(FONT_BLACK, 42), fill=GOLD + (255,))

    # Subjects 2-column grid
    draw.rounded_rectangle((46, 392, W - 46, 868), radius=24, fill=(12, 30, 60, 245), outline=CYAN + (200,), width=2)
    draw.text((76, 414), "ASESORÍAS ACADÉMICAS Y TÉCNICAS EN:", font=get_font(FONT_BLACK, 24), fill=CYAN + (255,))

    items = [
        "Matemáticas Básicas y Razonamiento",
        "Cálculo 1, 2 y 3 (Dif., Integral, Multiv.)",
        "Física Mecánica, Ondas y Electromag.",
        "Ecuaciones Diferenciales y Métodos Num.",
        "Geometría Vectorial, Analítica y Euclid.",
        "Estática y Resistencia de Materiales",
    ]
    cy = 468
    for idx, item in enumerate(items):
        draw_check_circle(draw, 94, cy + 16, r=15, bg=GOLD, fg=NAVY_DARK)
        draw.text((126, cy), item, font=get_font(FONT_BOLD, 26), fill=WHITE + (255,))
        cy += 64

    draw_dual_contact_bar(
        canvas,
        (46, 892, W - 46, 1044),
        sub_note="Envía tu taller o agenda tu clase por WhatsApp o Facebook Messenger",
        bg=NAVY_DARK,
        outline=CYAN,
    )

    out_path = OUT_AVISOS / "Aviso_08_Clases_Talleres_Trabajos_Escritos_Flatlay_1x1.png"
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def render_spacetime_funnel_bg(W: int, H: int, line_rgb=(152, 240, 88), bg_top=(66, 72, 68), bg_bot=(34, 40, 38)) -> Image.Image:
    """Procedurally draws a razor-sharp 3D spacetime gravity-well wireframe grid at 1080x1080."""
    img = Image.new("RGB", (W, H), bg_bot)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / float(H)
        r = int(bg_top[0] * (1 - t) + bg_bot[0] * t)
        g = int(bg_top[1] * (1 - t) + bg_bot[1] * t)
        b = int(bg_top[2] * (1 - t) + bg_bot[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Radial green glow near the funnel throat
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    cx_g, cy_g = int(W * 0.44), int(H * 0.56)
    for rad in range(360, 20, -14):
        alpha = int(10 * (1.0 - rad / 360.0))
        gdraw.ellipse((cx_g - rad, cy_g - int(rad * 0.65), cx_g + rad, cy_g + int(rad * 0.65)), fill=line_rgb + (alpha,))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 3D perspective projection of funnel z(r) = -3.6 / (r + 0.55)
    cam_tilt = 0.58
    cos_t, sin_t = math.cos(cam_tilt), math.sin(cam_tilt)

    def proj(x3, y3, z3):
        yr = y3 * cos_t - z3 * sin_t
        zr = y3 * sin_t + z3 * cos_t + 6.4
        scale = 920.0 / max(0.8, zr)
        sx = W * 0.47 + x3 * scale
        sy = H * 0.43 - yr * scale
        return (sx, sy)

    # Concentric rings
    r_vals = [0.22, 0.35, 0.50, 0.68, 0.90, 1.16, 1.46, 1.82, 2.25, 2.75, 3.35, 4.05, 4.9, 5.9]
    thetas = [2 * math.pi * i / 72.0 for i in range(73)]
    for rv in r_vals:
        zv = -3.1 / (rv + 0.52)
        pts = [proj(rv * math.cos(th), rv * math.sin(th), zv) for th in thetas]
        draw.line(pts, fill=line_rgb, width=2)

    # Radial spokes
    for k in range(32):
        th = 2 * math.pi * k / 32.0
        pts = []
        for s in range(44):
            rv = 0.22 + (s / 43.0) * 5.8
            zv = -3.1 / (rv + 0.52)
            pts.append(proj(rv * math.cos(th), rv * math.sin(th), zv))
        draw.line(pts, fill=line_rgb, width=2)

    return img


def make_aviso_09_10_spacetime(badge_logo: Image.Image, lang: str = "es") -> Path:
    """Aviso 09 (ES) & Aviso 10 (EN) (1:1): Sharp 3D spacetime grid with corrected spelling and clean cards."""
    W, H = 1080, 1080
    if lang == "es":
        bg = render_spacetime_funnel_bg(W, H, line_rgb=(162, 244, 92), bg_top=(66, 74, 66), bg_bot=(32, 38, 34))
        accent = (162, 244, 92)
        badge_txt = "ASESORÍAS EN INGENIERÍA"
        h1 = "CLASES PARTICULARES Y"
        h2 = "TRABAJOS ESCRITOS"
        card_title = "MATERIAS PRINCIPALES:"
        subjects = [
            "Matemáticas y Álgebra",
            "Geometría Vectorial y Analítica",
            "Cálculo Diferencial",
            "Cálculo Integral y Vectorial",
            "Física Mecánica y Ondas",
            "Resistencia de Materiales",
        ]
        sub_note = "Material teórico y clases en vivo • También por Facebook Messenger"
        out_name = "Aviso_09_Curvatura_EspacioTiempo_Clases_y_Trabajos_ES_1x1.png"
    else:
        bg = render_spacetime_funnel_bg(W, H, line_rgb=(56, 216, 248), bg_top=(42, 62, 82), bg_bot=(16, 28, 44))
        accent = CYAN
        badge_txt = "ASESORÍAS EN INGENIERÍA • ONLINE"
        h1 = "PRIVATE CLASSES, TUTORING"
        h2 = "& WRITTEN ASSIGNMENTS"
        card_title = "CORE SUBJECTS:"
        subjects = [
            "Geometry & Linear Algebra",
            "Differential Calculus",
            "Integral & Vector Calculus",
            "Mechanics & Physics I / II",
            "Strength of Materials",
            "Solid Mechanics & Statics",
        ]
        sub_note = "Live 1-on-1 Online Tutoring Worldwide • WhatsApp & Facebook"
        out_name = "Aviso_10_Spacetime_Grid_Private_Classes_EN_1x1.png"

    canvas = bg.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Top title banner
    odraw.rounded_rectangle((42, 28, W - 42, 246), radius=24, fill=(10, 20, 36, 224), outline=accent + (255,), width=3)
    # Left subjects card
    odraw.rounded_rectangle((42, 268, W - 42, 858), radius=24, fill=(10, 20, 36, 214), outline=(255, 255, 255, 110), width=2)

    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    b_rs = badge_logo.resize((132, 132), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (W - 196, 46), b_rs)

    f_badge = get_font(FONT_BLACK, 19)
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge)
    draw.rounded_rectangle((68, 46, 68 + (bb[2] - bb[0]) + 42, 88), radius=21, fill=accent + (255,))
    draw.text((88, 55), badge_txt, font=f_badge, fill=NAVY_DARK + (255,))

    draw.text((68, 108), h1, font=get_font(FONT_BLACK, 48), fill=WHITE + (255,))
    draw.text((68, 168), h2, font=get_font(FONT_BLACK, 48), fill=GOLD + (255,))

    draw.text((74, 294), card_title, font=get_font(FONT_BLACK, 26), fill=GOLD + (255,))

    cy = 348
    for s in subjects:
        draw_check_circle(draw, 98, cy + 16, r=16, bg=accent, fg=NAVY_DARK)
        draw.text((134, cy), s, font=get_font(FONT_BOLD, 31), fill=WHITE + (255,))
        cy += 80

    # Extra info badge on right side of subject card
    draw.rounded_rectangle((630, 348, W - 70, 560), radius=18, fill=(18, 44, 82, 238), outline=GOLD + (255,), width=2)
    draw.text((654, 370), "ING. OSCAR VALENCIA", font=get_font(FONT_BLACK, 24), fill=GOLD + (255,))
    info_lines = [
        "• Explicación paso a paso",
        "• Preparación de parciales",
        "• Talleres y código Python",
        "• Modalidad Online/Presencial",
    ] if lang == "es" else [
        "• Step-by-step explanations",
        "• Exam & quiz prep",
        "• Homework & Python scripts",
        "• Live online 1-on-1 sessions",
    ]
    iy = 414
    for ln in info_lines:
        draw.text((654, iy), ln, font=get_font(FONT_BOLD, 20), fill=WHITE + (255,))
        iy += 32

    draw_dual_contact_bar(
        canvas,
        (42, 882, W - 42, 1042),
        phone_label=f"WHATSAPP: +57 {PHONE_DISPLAY}",
        sub_note=sub_note,
        bg=NAVY_DARK,
        outline=accent,
        lang=lang,
    )

    out_path = OUT_AVISOS / out_name
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def make_clean_chalkboard_frame() -> Image.Image:
    """Recovers the clean apple/pencils/books desk frame from 486575416 & 486742224 and replaces the center chalkboard cleanly."""
    a1 = np.array(Image.open(RES_DIR / "486575416_1209884887806647_7705573829757379819_n.jpg"))
    a2 = np.array(Image.open(RES_DIR / "486742224_1208931394568663_4049800346439418593_n.jpg"))
    rec = np.maximum(a1, a2)

    # Remove residual asterisk pixels (* in same positions on left pencils/ruler/apple) by
    # replacing dark outlier pixels with median of bright non-black neighbors
    patch = rec[355:950, 95:210].copy()
    h_p, w_p, _ = patch.shape
    cleaned = patch.copy()
    is_black = (patch[:, :, 0] < 65) & (patch[:, :, 1] < 65) & (patch[:, :, 2] < 65)
    # Dilate slightly to catch antialiased edges
    from PIL import ImageChops
    mask_im = Image.fromarray((is_black.astype(np.uint8) * 255))
    mask_dil = np.array(mask_im.filter(ImageFilter.MaxFilter(7))) > 128
    # Compute smooth background using bright pixels only
    for y in range(h_p):
        for x in range(w_p):
            if mask_dil[y, x]:
                y0, y1 = max(0, y - 14), min(h_p, y + 15)
                x0, x1 = max(0, x - 14), min(w_p, x + 15)
                win = patch[y0:y1, x0:x1]
                valid = ~mask_dil[y0:y1, x0:x1]
                if valid.any():
                    cleaned[y, x] = np.median(win[valid], axis=0).astype(np.uint8)
    rec[355:950, 95:210] = cleaned

    # Clean wooden plank ghost letters at bottom (y: 800..945, x: 185..920)
    wood = rec[800:950, 185:920].copy()
    # Replace dark text pixels inside wood zone with median of surrounding wood pixels
    w_dark = (wood[:, :, 0] < 78) & (wood[:, :, 1] < 65) & (wood[:, :, 2] < 65)
    w_mask = np.array(Image.fromarray((w_dark.astype(np.uint8) * 255)).filter(ImageFilter.MaxFilter(5))) > 128
    wood_clean = wood.copy()
    hw, ww, _ = wood.shape
    for y in range(hw):
        for x in range(ww):
            if w_mask[y, x]:
                y0, y1 = max(0, y - 10), min(hw, y + 11)
                x0, x1 = max(0, x - 10), min(ww, x + 11)
                win = wood[y0:y1, x0:x1]
                valid = ~w_mask[y0:y1, x0:x1]
                if valid.any():
                    wood_clean[y, x] = np.median(win[valid], axis=0).astype(np.uint8)
    rec[800:950, 185:920] = wood_clean

    # Crop inner desk photo: x in 22..1048, y in 268..954
    inner = Image.fromarray(rec[268:954, 22:1048]).convert("RGBA")

    # Paint clean textured dark chalkboard rectangle in the center (x: 158..735, y: 0..512)
    chalk_h = 512
    chalk_tex = load_fit(RES_DIR / "479543451_3848757458788120_113036427974149033_n.jpg", 577, chalk_h, contrast=0.7).convert("RGBA")
    slate_veil = Image.new("RGBA", (577, chalk_h), (28, 34, 42, 224))
    chalk_panel = Image.alpha_composite(chalk_tex, slate_veil)
    alpha_mask = Image.new("L", (577, chalk_h), 255)
    am_draw = ImageDraw.Draw(alpha_mask)
    for dx in range(18):
        val = int(255 * dx / 18.0)
        am_draw.line([(dx, 0), (dx, chalk_h)], fill=val)
        am_draw.line([(576 - dx, 0), (576 - dx, chalk_h)], fill=val)
    for dy in range(4):
        val = int(255 * (4 - dy) / 4.0)
        am_draw.line([(0, chalk_h - 1 - dy), (577, chalk_h - 1 - dy)], fill=val)

    inner.paste(chalk_panel, (158, 0), alpha_mask)
    return inner


def make_aviso_11_12_pizarra_manzana(badge_logo: Image.Image, lang: str = "es") -> Path:
    """Aviso 11 (ES) & Aviso 12 (EN) (1:1): Clean apple & chalkboard desk with white/gold chalk typography."""
    W, H = 1080, 1080
    FOREST = (22, 68, 22)
    canvas = Image.new("RGBA", (W, H), FOREST + (255,))
    draw = ImageDraw.Draw(canvas)

    # Subtle diagonal pattern in green header/footer
    for d in range(-H, W + H, 48):
        draw.line([(d, 0), (d - 220, H)], fill=(28, 82, 28, 255), width=2)

    draw.rectangle((0, 0, W, 12), fill=GOLD + (255,))

    b_rs = badge_logo.resize((126, 126), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (W - 156, 22), b_rs)

    if lang == "es":
        h1 = "CLASES PARTICULARES Y"
        h2 = "TRABAJOS ESCRITOS"
        title_board = "MATERIAS DISPONIBLES:"
        subjects = [
            "• Matemáticas y Álgebra",
            "• Geometría y Trigonometría",
            "• Cálculo Diferencial",
            "• Cálculo Integral",
            "• Física Mecánica y Estática",
            "• Resistencia de Materiales",
        ]
        sub_note = "Clases en vivo Online o Presenciales • Escríbenos por WhatsApp o Facebook"
        out_name = "Aviso_11_Pizarra_Manzana_Clases_y_Trabajos_ES_1x1.png"
    else:
        h1 = "PRIVATE CLASSES, TUTORING"
        h2 = "AND WRITTEN ASSIGNMENTS"
        title_board = "CORE SUBJECTS:"
        subjects = [
            "• Geometry & Algebra",
            "• Differential Calculus",
            "• Integral Calculus",
            "• Mechanics & Physics",
            "• Strength of Materials",
            "• Solid Mechanics & Statics",
        ]
        sub_note = "1-on-1 Live Online & In-Person Tutoring • WhatsApp & Facebook"
        out_name = "Aviso_12_Chalkboard_Desk_Private_Classes_EN_1x1.png"

    draw.rounded_rectangle((36, 26, 390, 62), radius=18, fill=GOLD + (255,))
    draw.text((54, 33), "ASESORÍAS EN INGENIERÍA", font=get_font(FONT_BLACK, 18), fill=NAVY_DARK + (255,))
    draw.text((36, 76), h1, font=get_font(FONT_BLACK, 44), fill=WHITE + (255,))
    draw.text((36, 132), h2, font=get_font(FONT_BLACK, 44), fill=GOLD + (255,))

    desk_im = make_clean_chalkboard_frame()
    paste_rounded_image(canvas, desk_im, (36, 202, W - 36, 862), radius=22, border_px=4, border_col=GOLD)

    # Chalkboard text centered in the dark chalkboard region (x: 225..735, y: 225..720)
    draw.text((238, 224), title_board, font=get_font(FONT_BLACK, 28), fill=GOLD + (255,))
    draw.line([(238, 262), (695, 262)], fill=CYAN + (200,), width=2)
    cy = 282
    f_sub_chalk = get_font(FONT_BOLD, 30)
    for s in subjects:
        draw.text((238, cy), s, font=f_sub_chalk, fill=WHITE + (255,))
        cy += 64

    # Bottom dual contact bar
    draw_dual_contact_bar(
        canvas,
        (36, 886, W - 36, 1044),
        phone_label=f"CEL / WHATSAPP: +57 {PHONE_DISPLAY}",
        sub_note=sub_note,
        bg=NAVY_DARK,
        outline=GOLD,
        lang=lang,
    )

    out_path = OUT_AVISOS / out_name
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def make_aviso_13_apoyo_escolar_amarillo(badge_logo: Image.Image) -> Path:
    """Aviso 13 (1:1): Upgrades 493809210 yellow Apoyo Escolar poster with 300 408 3940 & website."""
    W, H = 1080, 1080
    YELLOW_BG = (255, 222, 89)
    with Image.open(RES_DIR / "493809210_1239313408197128_1514469928189273813_n.jpg") as im:
        arr13 = np.array(im.convert("RGB"))

    # Remove residual "lar" black script pixels (x: 740..985, y: 148..265) without touching orange rays
    sub_lar = arr13[148:265, 740:985]
    lar_dark = (sub_lar[:, :, 0] < 170) & (sub_lar[:, :, 1] < 165) & (sub_lar[:, :, 2] < 145)
    lar_mask = np.array(Image.fromarray((lar_dark.astype(np.uint8) * 255)).filter(ImageFilter.MaxFilter(5))) > 128
    sub_lar[lar_mask] = YELLOW_BG
    arr13[148:265, 740:985] = sub_lar

    base = Image.fromarray(arr13, mode="RGB")
    draw = ImageDraw.Draw(base)

    # Clean old text regions completely while preserving corner doodles (TL <235, TR >845 y<148, BR >825 y>=869) & photo
    draw.rectangle((240, 20, 842, 488), fill=YELLOW_BG)
    draw.rectangle((562, 252, 1060, 868), fill=YELLOW_BG)
    draw.rectangle((480, 855, 822, 990), fill=YELLOW_BG)

    canvas = base.convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # Brand badge at top-center/left-next-to-title
    b_rs = badge_logo.resize((120, 120), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (242, 40), b_rs)

    draw.text((378, 46), "Apoyo Escolar y U", font=get_font(FONT_CASUAL, 52), fill=NAVY_DARK)
    draw.rounded_rectangle((378, 118, 760, 156), radius=18, fill=NAVY)
    draw.text((396, 126), "ASESORÍAS EN INGENIERÍA", font=get_font(FONT_BLACK, 20), fill=GOLD)

    draw.text((280, 186), "Profesor Oscar Fernando Valencia", font=get_font(FONT_CASUAL, 34), fill=(25, 32, 46))
    # Prominent Phone pill
    draw.rounded_rectangle((280, 244, 880, 320), radius=20, fill=WA_DARK, outline=WA_GREEN, width=3)
    draw_phone_whatsapp_icon(draw, 326, 282, r=22, bg=WA_GREEN, fg=WHITE)
    draw.text((366, 258), f"Tel / WhatsApp: {PHONE_DISPLAY}", font=get_font(FONT_BLACK, 30), fill=WHITE)

    # Prominent Website pill
    draw.rounded_rectangle((280, 336, 880, 398), radius=18, fill=NAVY, outline=ROYAL, width=3)
    draw_globe_icon(draw, 320, 367, r=17, fg=CYAN, bg=NAVY_DARK)
    draw.text((352, 351), WEB_DISPLAY, font=get_font(FONT_BLACK, 23), fill=WHITE)

    # Subjects card on the right of the photo
    draw.rounded_rectangle((574, 434, 1030, 852), radius=24, fill=(255, 246, 205, 248), outline=NAVY, width=3)
    draw.text((602, 456), "CLASES PASO A PASO EN:", font=get_font(FONT_BLACK, 24), fill=NAVY)
    subjects = [
        "MATEMÁTICAS",
        "FÍSICA",
        "CÁLCULO Y ÁLGEBRA",
        "GEOMETRÍA",
        "ESTADÍSTICA",
        "QUÍMICA BÁSICA",
    ]
    cy = 508
    for s in subjects:
        draw_check_circle(draw, 618, cy + 16, r=14, bg=NAVY, fg=GOLD)
        draw.text((646, cy), s, font=get_font(FONT_BLACK, 27), fill=NAVY_DARK)
        cy += 55

    # Bottom-left pill under photo
    draw.rounded_rectangle((36, 992, 810, 1054), radius=20, fill=NAVY_DARK, outline=ROYAL, width=2)
    draw_messenger_icon(draw, 74, 1023, r=18, bg=WHITE, fg=MESSENGER_BLUE)
    draw.text((106, 1009), f"Online o Presencial • Cel: {PHONE_DISPLAY} • {WEB_DISPLAY}", font=get_font(FONT_BOLD, 20), fill=WHITE)

    out_path = OUT_AVISOS / "Aviso_13_Apoyo_Escolar_y_Universitario_Amarillo_1x1.png"
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def make_aviso_14_meme_autopista(badge_logo: Image.Image) -> Path:
    """Aviso 14 (4:5): Highway exit meme upgraded cleanly without old 301 number / Euler logo."""
    W, H = 1080, 1350
    canvas = Image.new("RGBA", (W, H), NAVY_DARK + (255,))
    draw = ImageDraw.Draw(canvas)

    for gx in range(0, W, 54):
        draw.line([(gx, 0), (gx, H)], fill=(18, 42, 82, 255), width=1)
    for gy in range(0, H, 54):
        draw.line([(0, gy), (W, gy)], fill=(18, 42, 82, 255), width=1)
    draw.rectangle((0, 0, W, 14), fill=GOLD + (255,))

    b_rs = badge_logo.resize((140, 140), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (W - 186, 30), b_rs)

    draw.rounded_rectangle((54, 34, 490, 78), radius=22, fill=GOLD + (255,))
    draw.text((76, 43), "ASESORÍAS EN INGENIERÍA", font=get_font(FONT_BLACK, 22), fill=NAVY_DARK + (255,))
    draw.text((54, 98), "TOMA LA SALIDA CORRECTA", font=get_font(FONT_BLACK, 50), fill=WHITE + (255,))
    draw.text((54, 160), "ASEGURA TUS PARCIALES A TIEMPO", font=get_font(FONT_BLACK, 40), fill=GOLD + (255,))

    # Crop meme strictly above y=545 so old 'Euler Asesorías / 301 228 90 91' never appears!
    with Image.open(RES_DIR / "503827355_3958942054436326_718218107784753890_n.jpg") as im:
        meme_clean = im.crop((0, 0, im.width, 542)).convert("RGB")
        meme_clean = ImageEnhance.Contrast(meme_clean).enhance(1.10)
        meme_clean = ImageEnhance.Sharpness(meme_clean).enhance(1.15)
    paste_rounded_image(canvas, meme_clean, (54, 236, W - 54, 962), radius=28, border_px=5, border_col=GOLD)

    # Info strip below meme
    draw.rounded_rectangle((54, 988, W - 54, 1138), radius=22, fill=NAVY + (245,), outline=CYAN + (200,), width=2)
    draw.text((84, 1008), "MATEMÁTICAS • CÁLCULO • FÍSICA • ESTÁTICA • PROGRAMACIÓN", font=get_font(FONT_BLACK, 24), fill=GOLD + (255,))
    draw.text((84, 1052), "Explicaciones claras paso a paso, solución de talleres y preparación de", font=get_font(FONT_BOLD, 23), fill=WHITE + (255,))
    draw.text((84, 1086), "exámenes finales. Clases Online en vivo o Presenciales en Medellín.", font=get_font(FONT_BOLD, 23), fill=CYAN + (255,))

    draw_dual_contact_bar(
        canvas,
        (54, 1160, W - 54, 1316),
        sub_note="Escríbenos ahora y salva tus materias • WhatsApp o Facebook Messenger",
        bg=NAVY_DARK,
        outline=GOLD,
    )

    out_path = OUT_AVISOS / "Aviso_14_Meme_Autopista_Estudiantes_Ganar_En_5_4x5.png"
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def make_historia_03_cuadricula_verde(badge_logo: Image.Image) -> Path:
    """Historia 03 (9:16): HD recreation of 493951922 sage-green grid notebook story."""
    W, H = 1080, 1920
    SAGE_BG = (122, 145, 118)
    GRID_COL = (158, 178, 154)
    CREAM = (248, 249, 246)
    NAVY_TEXT = (14, 42, 92)
    GREEN_TITLE = (42, 74, 38)

    canvas = Image.new("RGBA", (W, H), SAGE_BG + (255,))
    draw = ImageDraw.Draw(canvas)

    # Notebook grid
    for gx in range(0, W, 68):
        draw.line([(gx, 0), (gx, H)], fill=GRID_COL + (255,), width=2)
    for gy in range(0, H, 68):
        draw.line([(0, gy), (W, gy)], fill=GRID_COL + (255,), width=2)

    # White doodle protractor top-left
    draw.arc((50, -60, 440, 310), start=0, end=180, fill=(235, 242, 234, 170), width=12)
    draw.line([(50, 125), (440, 125)], fill=(235, 242, 234, 170), width=12)
    draw.arc((125, 20, 365, 240), start=0, end=180, fill=(235, 242, 234, 170), width=8)

    # White chalk squiggles top-right and bottom-left
    draw.line([(560, -20), (610, 210), (685, 10), (745, 225), (840, 20)], fill=(255, 255, 255, 220), width=14, joint="curve")
    draw.line([(12, 1560), (140, 1650), (35, 1760), (170, 1870)], fill=(255, 255, 255, 220), width=14, joint="curve")

    # Calculator doodle bottom-right
    draw.rounded_rectangle((810, 1630, 1050, 1950), radius=24, outline=(235, 242, 234, 170), width=10)
    draw.rectangle((844, 1670, 1016, 1742), outline=(235, 242, 234, 170), width=6)
    for r in range(3):
        for c in range(3):
            bx = 846 + c * 60
            by = 1775 + r * 54
            draw.rectangle((bx, by, bx + 42, by + 34), outline=(235, 242, 234, 170), width=5)

    # Central crisp white paper card
    card_box = (96, 330, W - 96, 1525)
    draw.rounded_rectangle((card_box[0] + 8, card_box[1] + 10, card_box[2] + 8, card_box[3] + 10), radius=42, fill=(75, 92, 72, 140))
    draw.rounded_rectangle(card_box, radius=42, fill=CREAM + (255,), outline=(220, 230, 218, 255), width=3)

    # Logo centered top of card
    b_rs = badge_logo.resize((190, 190), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, ((W - 190) // 2, 210), b_rs)

    draw_centered_text(draw, 425, "CLASES", get_font(FONT_BLACK, 74), (10, 62, 156, 255), W)
    draw_centered_text(draw, 512, "PARTICULARES", get_font(FONT_BLACK, 74), (10, 62, 156, 255), W)
    draw_centered_text(draw, 612, "Matemáticas e Ingeniería", get_font(FONT_ITAL, 56), GREEN_TITLE + (255,), W)

    draw.rounded_rectangle((220, 704, W - 220, 766), radius=31, fill=NAVY + (255,))
    draw_centered_text(draw, 718, "ASESORÍAS EN INGENIERÍA", get_font(FONT_BLACK, 30), GOLD + (255,), W)

    body_lines = [
        "Clases presenciales u online",
        "para bachillerato y universidades:",
        "Cálculo I/II/III, Física, Geometría,",
        "Estática, Resistencia de",
        "Materiales y Programación",
    ]
    by = 815
    f_body = get_font(FONT_BOLD, 38)
    for ln in body_lines:
        draw_centered_text(draw, by, ln, f_body, NAVY_TEXT + (255,), W)
        by += 58

    # Phone box inside card
    draw.rounded_rectangle((176, 1148, W - 176, 1326), radius=24, fill=(238, 248, 240, 255), outline=WA_DARK + (255,), width=4)
    draw_centered_text(draw, 1168, "Más información al:", get_font(FONT_BOLD, 34), WA_DARK + (255,), W)
    draw_phone_whatsapp_icon(draw, 290, 1265, r=28, bg=WA_GREEN, fg=WHITE)
    draw.text((342, 1230), PHONE_DISPLAY, font=get_font(FONT_BLACK, 58), fill=NAVY_DARK + (255,))

    # Web pill inside card
    draw.rounded_rectangle((156, 1368, W - 156, 1468), radius=50, fill=NAVY + (255,), outline=CYAN + (255,), width=4)
    draw_globe_icon(draw, 214, 1418, r=22, fg=CYAN, bg=NAVY_DARK)
    draw.text((254, 1396), WEB_DISPLAY, font=get_font(FONT_BLACK, 34), fill=WHITE + (255,))

    # Bottom white pill CTA
    draw.rounded_rectangle((130, 1598, W - 130, 1682), radius=42, fill=WHITE + (255,), outline=NAVY + (255,), width=3)
    draw_messenger_icon(draw, 186, 1640, r=24, bg=MESSENGER_BLUE, fg=WHITE)
    draw.text((228, 1621), "Aprende en la web o escríbenos por Facebook", font=get_font(FONT_BLACK, 27), fill=NAVY_DARK + (255,))

    out_path = OUT_AVISOS / "Historia_Facebook_Reels_03_Cuadricula_Verde_Clases_9x16.png"
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


# ==============================================================================
# VIDEOS PROMOCIONALES MP4
# ==============================================================================

def generate_upbeat_audio_wav(wav_path: Path, duration_sec: float = 15.0, sample_rate: int = 22050):
    n_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    chords = [
        (349.23, 440.00, 523.25),
        (261.63, 329.63, 392.00),
        (196.00, 293.66, 392.00),
        (220.00, 329.63, 440.00),
    ]
    signal = np.zeros_like(t)
    seg_len = duration_sec / len(chords)
    for i, st in enumerate(t):
        idx = min(len(chords) - 1, int(st // seg_len))
        f1, f2, f3 = chords[idx]
        pad = 0.16 * (
            math.sin(2 * math.pi * f1 * st)
            + 0.7 * math.sin(2 * math.pi * f2 * st)
            + 0.45 * math.sin(2 * math.pi * f3 * st)
        )
        beat_phase = (st * (128.0 / 60.0)) % 1.0
        pluck = 0.18 * math.exp(-beat_phase * 7.5) * math.sin(2 * math.pi * f1 * 0.5 * st)
        signal[i] = pad + pluck

    fade_len = int(0.6 * sample_rate)
    signal[:fade_len] *= np.linspace(0, 1, fade_len)
    signal[-fade_len:] *= np.linspace(1, 0, fade_len)

    pcm = np.clip(signal * 32767 * 0.72, -32767, 32767).astype(np.int16)
    with wave.open(str(wav_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())


def render_promo_video(
    out_mp4: Path,
    slides: list,
    size: tuple,
    badge_logo: Image.Image,
    accent_color=GOLD,
    fps: int = 24,
):
    W, H = size
    sec_per_slide = 3.0
    frames_per_slide = int(sec_per_slide * fps)
    total_sec = len(slides) * sec_per_slide

    wav_path = OUT_VIDEOS / "_temp_audio_asesorias.wav"
    generate_upbeat_audio_wav(wav_path, duration_sec=total_sec)

    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(fps), "-i", "-",
        "-i", str(wav_path), "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "fast", "-crf", "22", "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(out_mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    f_top = get_font(FONT_BLACK, int(W * 0.042))
    f_badge = get_font(FONT_BOLD, int(W * 0.028))
    f_title = get_font(FONT_BLACK, int(W * 0.048))
    f_sub = get_font(FONT_BOLD, int(W * 0.032))
    f_cta = get_font(FONT_BLACK, int(W * 0.034))
    f_web = get_font(FONT_BOLD, int(W * 0.028))

    logo_s = int(W * 0.14)
    logo_rs = badge_logo.resize((logo_s, logo_s), Image.Resampling.LANCZOS)

    for img_path, kicker_txt, title_txt, sub_txt in slides:
        big_w, big_h = int(W * 1.18), int(H * 1.18)
        base_im = load_fit(img_path, big_w, big_h, contrast=1.08)

        for f_idx in range(frames_per_slide):
            prog = f_idx / float(frames_per_slide)
            cur_w = int(W * (1.16 - 0.14 * prog))
            cur_h = int(H * (1.16 - 0.14 * prog))
            x0 = (big_w - cur_w) // 2
            y0 = (big_h - cur_h) // 2
            frame = base_im.crop((x0, y0, x0 + cur_w, y0 + cur_h)).resize((W, H), Image.Resampling.BILINEAR).convert("RGBA")

            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            odraw = ImageDraw.Draw(overlay)

            hdr_h = int(H * 0.115)
            odraw.rectangle((0, 0, W, hdr_h), fill=NAVY + (232,))
            odraw.rectangle((0, hdr_h, W, hdr_h + 6), fill=accent_color + (255,))
            odraw.text((28, int(hdr_h * 0.22)), "ASESORÍAS EN INGENIERÍA", font=f_top, fill=WHITE + (255,))
            odraw.text((28, int(hdr_h * 0.58)), kicker_txt, font=f_badge, fill=CYAN + (255,))
            overlay.paste(logo_rs, (W - logo_s - 18, max(8, (hdr_h - logo_s) // 2)), logo_rs)

            slide_in = min(1.0, f_idx / 8.0)
            box_y0 = int(H * 0.69)
            odraw.rectangle((0, box_y0, W, H), fill=NAVY_DARK + (238,))
            odraw.rectangle((0, box_y0, int(W * slide_in), box_y0 + 8), fill=accent_color + (255,))
            odraw.text((32, box_y0 + 20), title_txt, font=f_title, fill=accent_color + (255,))
            odraw.text((32, box_y0 + 20 + int(W * 0.064)), sub_txt, font=f_sub, fill=WHITE + (255,))

            # Persistent bottom CTA strip with WhatsApp 300 408 3940 & Website
            cta_y = H - int(H * 0.125)
            odraw.rectangle((0, cta_y, W, H), fill=ROYAL + (255,))
            icon_r = int(H * 0.022)
            draw_phone_whatsapp_icon(odraw, 44, cta_y + int((H - cta_y) * 0.34), r=icon_r, bg=WA_GREEN, fg=WHITE)
            odraw.text((80, cta_y + int((H - cta_y) * 0.16)), f"CEL / WHATSAPP: {PHONE_DISPLAY}", font=f_cta, fill=WHITE + (255,))
            odraw.text((80, cta_y + int((H - cta_y) * 0.56)), f"Web: {WEB_DISPLAY}", font=f_web, fill=GOLD + (255,))

            comp = Image.alpha_composite(frame, overlay).convert("RGB")
            proc.stdin.write(comp.tobytes())

    proc.stdin.close()
    proc.wait()
    if wav_path.exists():
        wav_path.unlink()
    return out_mp4


def main():
    _, badge_logo = prepare_brand_logos()

    h_desk = RES_DIR / "hero_escritorio_ingenieria.jpg"
    h_tutor = RES_DIR / "hero_tutoria_presencial.jpg"
    h_night = RES_DIR / "hero_programacion_estructuras_noche.jpg"

    # 1. Facebook Cover Banner
    cov = make_facebook_cover(badge_logo)
    print("Banner generado:", cov.name)

    # 2. Aviso 01 (4:5): Cierre de Semestre / Últimas Semanas
    a1 = make_ad_4x5_or_1x1(
        "Aviso_01_Cierre_Semestre_Parciales_Finales_4x5.png",
        size=(1080, 1350),
        badge_txt="ÚLTIMAS SEMANAS DE ESTUDIO",
        title_l1="¡SALVA TU SEMESTRE",
        title_l2="Y PARCIALES FINALES!",
        subtitle="Clases y asesorías personalizadas • Online o Presencial",
        bullets=[
            "Matemáticas, Álgebra, Geometría y Cálculo I, II, III",
            "Física Mecánica, Estática y Resistencia de Materiales",
            "Preparación intensiva para exámenes finales y talleres",
            "Explicación paso a paso con Ingeniero Especialista",
        ],
        photo_path=h_tutor,
        badge_logo=badge_logo,
        accent_color=GOLD,
    )
    print("Aviso generado:", a1.name)

    # 3. Aviso 02 (1:1): Matemáticas, Cálculo y Física
    a2 = make_ad_4x5_or_1x1(
        "Aviso_02_Matematicas_Calculo_Fisica_1x1.png",
        size=(1080, 1080),
        badge_txt="BACHILLERATO Y UNIVERSIDAD",
        title_l1="MATEMÁTICAS, CÁLCULO",
        title_l2="Y FÍSICA SIN COMPLICACIONES",
        subtitle="Domina los temas clave antes de tus evaluaciones finales",
        bullets=[
            "Cálculo Diferencial, Integral, Vectorial y Ecuaciones",
            "Física I, II, III, Trigonometría y Álgebra Lineal",
            "Resolución guiada de ejercicios tipo parcial",
            "Sesiones en vivo 100% personalizadas",
        ],
        photo_path=h_desk,
        badge_logo=badge_logo,
        accent_color=CYAN,
    )
    print("Aviso generado:", a2.name)

    # 4. Aviso 03 (4:5): Ingeniería Civil, Estructuras y NSR-10
    a3 = make_ad_4x5_or_1x1(
        "Aviso_03_Ingenieria_Civil_Estructuras_NSR10_4x5.png",
        size=(1080, 1350),
        badge_txt="ASESORÍA UNIVERSITARIA Y PROFESIONAL",
        title_l1="INGENIERÍA CIVIL Y",
        title_l2="ANÁLISIS ESTRUCTURAL",
        subtitle="Acompañamiento técnico para entregas y exámenes finales",
        bullets=[
            "Estática, Resistencia de Materiales y Análisis Matricial",
            "Diseño en Concreto Reforzado y Acero (NSR-10 / AISC)",
            "Presupuestos de obra (APU), cantidades y programación",
            "Revisión de proyectos, memorias de cálculo y planos",
        ],
        photo_path=h_desk,
        badge_logo=badge_logo,
        accent_color=GOLD,
    )
    print("Aviso generado:", a3.name)

    # 5. Aviso 04 (1:1): Programación y Proyectos Técnicos
    a4 = make_ad_4x5_or_1x1(
        "Aviso_04_Programacion_Python_MATLAB_Web_1x1.png",
        size=(1080, 1080),
        badge_txt="PROYECTOS Y CÓDIGO DE CIERRE",
        title_l1="PROGRAMACIÓN PARA",
        title_l2="INGENIERÍA Y UNIVERSIDAD",
        subtitle="Tutorías prácticas y acompañamiento en entregas finales",
        bullets=[
            "Python (NumPy, SciPy, Pandas, gráficas y automatización)",
            "MATLAB, Visual Basic (Excel Macros) y scripts en Bash",
            "Desarrollo Web: HTML5, CSS y JavaScript paso a paso",
            "Depuración de código y explicación para tu sustentación",
        ],
        photo_path=h_night,
        badge_logo=badge_logo,
        accent_color=CYAN,
    )
    print("Aviso generado:", a4.name)

    # 6. Aviso 05 (4:5): Asesoría Exprés Últimos Días
    a5 = make_ad_4x5_or_1x1(
        "Aviso_05_Asesoria_Expres_Ultimos_Dias_4x5.png",
        size=(1080, 1350),
        badge_txt="CUPOS LIMITADOS ESTA SEMANA",
        title_l1="¿TIENES PARCIAL O",
        title_l2="ENTREGA ESTA SEMANA?",
        subtitle="Aprovecha las últimas semanas del periodo con apoyo experto",
        bullets=[
            "Refuerzo rápido de última hora para finales y habilitaciones",
            "Modalidad Online en vivo (toda Colombia) o Presencial",
            "Material claro, ejercicios resueltos y seguimiento real",
            "Escríbenos ya y reserva tu horario de clase hoy mismo",
        ],
        photo_path=h_night,
        badge_logo=badge_logo,
        accent_color=GOLD,
    )
    print("Aviso generado:", a5.name)

    # 7. NUEVOS AVISOS MEJORADOS A PARTIR DE recursos_visuales/ (Avisos 06 - 14 + Historia 03)
    for fn, args in [
        (make_aviso_06_viga_canal, (badge_logo,)),
        (make_aviso_07_pizarra_formulas, (badge_logo,)),
        (make_aviso_08_flatlay_clases_trabajos, (badge_logo,)),
        (make_aviso_09_10_spacetime, (badge_logo, "es")),
        (make_aviso_09_10_spacetime, (badge_logo, "en")),
        (make_aviso_11_12_pizarra_manzana, (badge_logo, "es")),
        (make_aviso_11_12_pizarra_manzana, (badge_logo, "en")),
        (make_aviso_13_apoyo_escolar_amarillo, (badge_logo,)),
        (make_aviso_14_meme_autopista, (badge_logo,)),
        (make_historia_03_cuadricula_verde, (badge_logo,)),
    ]:
        out = fn(*args)
        print("Nuevo aviso mejorado generado:", out.name)

    # 8. Historia 01 (9:16): Últimas Semanas de Estudio
    s1 = make_vertical_story_9x16(
        "Historia_Facebook_Reels_01_Ultimas_Semanas_9x16.png",
        badge_txt="ÚLTIMAS SEMANAS DE ESTUDIO",
        title_l1="¡ASEGURA TU",
        title_l2="CIERRE DE SEMESTRE!",
        subtitle="Asesorías personalizadas • Colegio, U y Profesionales",
        bullets=[
            "Cálculo I, II, III, Álgebra y Física",
            "Estática, Materiales y Estructuras NSR-10",
            "Programación en Python, MATLAB y JS",
            "Clases online en vivo o presenciales",
        ],
        photo_top=h_tutor,
        photo_bottom_left=h_desk,
        photo_bottom_right=h_night,
        badge_logo=badge_logo,
        accent_color=GOLD,
    )
    print("Historia generada:", s1.name)

    # 9. Historia 02 (9:16): Ingeniería y Programación
    s2 = make_vertical_story_9x16(
        "Historia_Facebook_Reels_02_Ingenieria_Programacion_9x16.png",
        badge_txt="PARCIALES Y ENTREGAS FINALES",
        title_l1="DOMINA CÁLCULO,",
        title_l2="ESTRUCTURAS Y CÓDIGO",
        subtitle="Aprende paso a paso con Ingeniero Civil Especialista",
        bullets=[
            "Resolución de dudas antes de tu examen",
            "Análisis estructural, concreto, acero y APU",
            "Python, MATLAB, Visual Basic y Web",
            "Horarios flexibles esta semana",
        ],
        photo_top=h_night,
        photo_bottom_left=h_tutor,
        photo_bottom_right=h_desk,
        badge_logo=badge_logo,
        accent_color=CYAN,
    )
    print("Historia generada:", s2.name)

    if "--images-only" in __import__("sys").argv:
        return

    # 10. Video 01 (9:16 Reel): Últimas Semanas — Salva Tu Semestre
    v1 = render_promo_video(
        OUT_VIDEOS / "Video_01_Reel_Ultimas_Semanas_Salva_Tu_Semestre_9x16.mp4",
        slides=[
            (h_tutor, "ÚLTIMAS SEMANAS DE ESTUDIO", "SALVA TU SEMESTRE", "Preparación intensiva para parciales y finales"),
            (h_desk, "BACHILLERATO Y UNIVERSIDAD", "MATEMÁTICAS Y CÁLCULO", "Álgebra, Cálculo I/II/III, Ecuaciones y Física"),
            (h_tutor, "EXPLICACIÓN PASO A PASO", "ESTÁTICA Y ESTRUCTURAS", "Resistencia de materiales y diseño NSR-10"),
            (h_night, "PROYECTOS Y ENTREGAS", "PYTHON, MATLAB Y WEB", "Acompañamiento real para tus trabajos técnicos"),
            (h_desk, "ONLINE O PRESENCIAL", "AGENDA TU CLASE HOY", f"Cel: {PHONE_DISPLAY} • {WEB_DISPLAY}"),
        ],
        size=(720, 1280),
        badge_logo=badge_logo,
        accent_color=GOLD,
    )
    print("Video generado:", v1.name)

    # 11. Video 02 (9:16 Reel): Ingeniería Civil y Programación
    v2 = render_promo_video(
        OUT_VIDEOS / "Video_02_Reel_Ingenieria_Estructuras_Programacion_9x16.mp4",
        slides=[
            (h_desk, "ASESORÍA TÉCNICA ESPECIALIZADA", "INGENIERÍA CIVIL", "Estática, análisis estructural y presupuestos APU"),
            (h_night, "CÓDIGO PARA INGENIERÍA", "PYTHON Y MATLAB", "Modelado numérico, gráficas y scripts listos"),
            (h_tutor, "CLASES EN VIVO 1 A 1", "ENTIENDE DE VERDAD", "Resolvemos ejercicios tipo parcial paso a paso"),
            (h_desk, "CIERRE DE PERIODO", "CUPOS ESTA SEMANA", f"WhatsApp: {PHONE_DISPLAY} • {WEB_DISPLAY}"),
        ],
        size=(720, 1280),
        badge_logo=badge_logo,
        accent_color=CYAN,
    )
    print("Video generado:", v2.name)

    # 12. Video 03 (1:1 Feed Facebook): Campaña Integral Asesorías en Ingeniería
    v3 = render_promo_video(
        OUT_VIDEOS / "Video_03_Feed_Asesorias_en_Ingenieria_1x1.mp4",
        slides=[
            (h_tutor, "ÚLTIMAS SEMANAS DE CLASE", "ASESORÍAS EN INGENIERÍA", "Clases particulares para colegio y universidad"),
            (h_desk, "CIENCIAS EXACTAS", "CÁLCULO, FÍSICA Y ÁLGEBRA", "Preparación rápida para parciales y finales"),
            (h_night, "INGENIERÍA Y CÓDIGO", "ESTRUCTURAS Y PYTHON", "Estática, materiales, NSR-10, MATLAB y JS"),
            (h_tutor, "ATENCIÓN PERSONALIZADA", "CONTÁCTANOS HOY", f"WhatsApp: {PHONE_DISPLAY} • {WEB_DISPLAY}"),
        ],
        size=(720, 720),
        badge_logo=badge_logo,
        accent_color=GOLD,
    )
    print("Video generado:", v3.name)

    # 13. Video 04 (9:16 Reel): Nuevos Avisos y Portal Interactivo de Aprendizaje
    v4 = render_promo_video(
        OUT_VIDEOS / "Video_04_Reel_Nuevos_Avisos_y_Portal_Interactivo_9x16.mp4",
        slides=[
            (OUT_AVISOS / "Aviso_06_Viga_Canal_Estatica_Resistencia_Materiales_4x5.png", "CLASES Y ASESORÍAS", "ESTÁTICA Y MATERIALES", "Aprende con guías claras y ejemplos paso a paso"),
            (OUT_AVISOS / "Aviso_09_Curvatura_EspacioTiempo_Clases_y_Trabajos_ES_1x1.png", "TEORÍA Y PRÁCTICA WEB", "MATEMÁTICAS Y CÁLCULO", "Explora temarios interactivos en nuestra web"),
            (OUT_AVISOS / "Aviso_11_Pizarra_Manzana_Clases_y_Trabajos_ES_1x1.png", "TRABAJOS Y TALLERES", "FÍSICA Y GEOMETRÍA", "Online en vivo o presencial con el Ing. Oscar Valencia"),
            (OUT_AVISOS / "Aviso_14_Meme_Autopista_Estudiantes_Ganar_En_5_4x5.png", "PORTAL INTERACTIVO", "ESTUDIA Y APRENDE", f"Visita {WEB_DISPLAY} • Cel: {PHONE_DISPLAY}"),
        ],
        size=(720, 1280),
        badge_logo=badge_logo,
        accent_color=GOLD,
    )
    print("Video generado:", v4.name)


if __name__ == "__main__":
    main()
