#!/usr/bin/env python3
"""
Generador Maestro de Identidad, Avisos Publicitarios y Videos Promocionales (MP4)
Proyecto: publicidad-asesorias — Marca: Asesorías en Ingeniería
Campaña: Últimas Semanas de Estudio / Cierre de Semestre (100% Facebook -> WhatsApp en privado)
"""

import math
import subprocess
import wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

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

# Brand Palette
NAVY = (15, 37, 71)
NAVY_DARK = (9, 22, 46)
ROYAL = (29, 99, 220)
GOLD = (245, 166, 35)
CYAN = (56, 189, 248)
WHITE = (255, 255, 255)
SLATE = (226, 232, 240)
MESSENGER_BLUE = (0, 132, 255)


def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def prepare_brand_logos():
    """Creates transparent PNG logo variants from the brand assets."""
    white_logo_jpg = ID_DIR / "Logo_Principal_Blanco_Asesorias_en_Ingenieria.jpg"
    square_logo_jpg = ID_DIR / "Logo_Perfil_Cuadrado_Facebook_Asesorias_en_Ingenieria.jpg"

    # 1. Transparent main logo (remove near-white background cleanly)
    with Image.open(white_logo_jpg) as im:
        rgba = im.convert("RGBA")
        arr = np.array(rgba)
        # Pixels where R, G, B > 240 become transparent
        is_white = (arr[:, :, 0] > 238) & (arr[:, :, 1] > 238) & (arr[:, :, 2] > 238)
        arr[is_white, 3] = 0
        trans_main = Image.fromarray(arr, mode="RGBA")
        # Crop tightly with small padding
        bbox = trans_main.getbbox()
        if bbox:
            trans_main = trans_main.crop(bbox)
        trans_main.save(ID_DIR / "Logo_Principal_Transparente.png")

    # 2. Circular badge RGBA from square navy logo
    with Image.open(square_logo_jpg) as im:
        sq = im.convert("RGBA")
        w, h = sq.size
        ss = 2
        mask = Image.new("L", (w * ss, h * ss), 0)
        ImageDraw.Draw(mask).ellipse((6, 6, w * ss - 7, h * ss - 7), fill=255)
        mask = mask.resize((w, h), Image.Resampling.LANCZOS)
        badge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        badge.paste(sq, (0, 0), mask)
        # Subtle gold ring around badge
        bdraw = ImageDraw.Draw(badge)
        bdraw.ellipse((4, 4, w - 5, h - 5), outline=GOLD + (255,), width=10)
        badge.save(ID_DIR / "Logo_Badge_Transparente.png")

    return Image.open(ID_DIR / "Logo_Principal_Transparente.png").convert("RGBA"), Image.open(ID_DIR / "Logo_Badge_Transparente.png").convert("RGBA")


def load_fit(img_path: Path, w: int, h: int, contrast: float = 1.06) -> Image.Image:
    with Image.open(img_path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        if contrast != 1.0:
            im = ImageEnhance.Contrast(im).enhance(contrast)
            im = ImageEnhance.Color(im).enhance(1.06)
        return ImageOps.fit(im, (w, h), method=Image.Resampling.LANCZOS)


def draw_messenger_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 24, bg=WHITE, fg=MESSENGER_BLUE):
    """Draws a crisp Facebook Messenger bubble with lightning bolt icon."""
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    # Little chat tail at bottom-left
    draw.polygon([
        (cx - int(r * 0.65), cy + int(r * 0.55)),
        (cx - int(r * 0.20), cy + int(r * 0.85)),
        (cx - int(r * 0.72), cy + int(r * 0.98)),
    ], fill=bg)
    # Lightning bolt inside
    bolt = [
        (cx - int(r * 0.48), cy + int(r * 0.14)),
        (cx - int(r * 0.08), cy - int(r * 0.28)),
        (cx + int(r * 0.06), cy - int(r * 0.02)),
        (cx + int(r * 0.48), cy - int(r * 0.14)),
        (cx + int(r * 0.08), cy + int(r * 0.28)),
        (cx - int(r * 0.06), cy + int(r * 0.02)),
    ]
    draw.polygon(bolt, fill=fg)


def draw_check_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 18, bg=GOLD, fg=NAVY_DARK):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    p1 = (cx - int(r * 0.42), cy + int(r * 0.05))
    p2 = (cx - int(r * 0.10), cy + int(r * 0.38))
    p3 = (cx + int(r * 0.48), cy - int(r * 0.34))
    draw.line([p1, p2, p3], fill=fg, width=4, joint="curve")


def draw_centered_text(draw: ImageDraw.ImageDraw, y: int, text: str, font, fill, canvas_w: int):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((canvas_w - tw) // 2, y), text, font=font, fill=fill)


def paste_rounded_photo(canvas: Image.Image, photo_path: Path, box: tuple, radius: int = 28, border_px: int = 5, border_col=GOLD):
    x0, y0, x1, y1 = box
    pw, ph = x1 - x0, y1 - y0
    im = load_fit(photo_path, pw, ph)
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


def draw_fb_cta_bar(canvas: Image.Image, box: tuple, title_line: str, sub_line: str, bg=ROYAL, accent=WHITE):
    draw = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = box
    h = y1 - y0
    draw.rounded_rectangle(box, radius=24, fill=bg + (255,), outline=CYAN + (255,), width=3)
    icon_r = min(32, int(h * 0.28))
    draw_messenger_icon(draw, x0 + 58, (y0 + y1) // 2, r=icon_r, bg=WHITE, fg=MESSENGER_BLUE)
    f_t = get_font(FONT_BLACK, 30 if (x1 - x0) > 850 else 26)
    f_s = get_font(FONT_BOLD, 22 if (x1 - x0) > 850 else 19)
    draw.text((x0 + 112, y0 + int(h * 0.17)), title_line, font=f_t, fill=accent + (255,))
    draw.text((x0 + 112, y0 + int(h * 0.56)), sub_line, font=f_s, fill=GOLD + (255,))


def make_facebook_cover(badge_logo: Image.Image):
    """Generates 1640x624 Facebook Page Cover Banner."""
    W, H = 1640, 624
    canvas = Image.new("RGBA", (W, H), NAVY_DARK + (255,))
    draw = ImageDraw.Draw(canvas)

    # Subtle grid lines on left
    for gx in range(0, W, 60):
        draw.line([(gx, 0), (gx, H)], fill=(22, 48, 90, 255), width=1)
    for gy in range(0, H, 60):
        draw.line([(0, gy), (W, gy)], fill=(22, 48, 90, 255), width=1)

    # Right photo panel with diagonal fade
    photo = load_fit(RES_DIR / "hero_escritorio_ingenieria.jpg", 940, H)
    canvas.paste(photo, (700, 0))
    # Gradient overlay from left navy to transparent
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad)
    for x in range(680, 1280):
        alpha = int(255 * (1.0 - (x - 680) / 600.0))
        gdraw.line([(x, 0), (x, H)], fill=NAVY_DARK + (max(0, min(255, alpha)),))
    gdraw.rectangle((0, 0, 680, H), fill=NAVY_DARK + (255,))
    canvas = Image.alpha_composite(canvas, grad)
    draw = ImageDraw.Draw(canvas)

    # Top gold stripe
    draw.rectangle((0, 0, W, 10), fill=GOLD + (255,))

    # Badge logo
    b_rs = badge_logo.resize((170, 170), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (64, 52), b_rs)

    draw.text((260, 68), "ASESORÍAS EN", font=get_font(FONT_BLACK, 52), fill=WHITE + (255,))
    draw.text((260, 128), "INGENIERÍA", font=get_font(FONT_BLACK, 64), fill=GOLD + (255,))
    draw.text((260, 206), "Clases Particulares • Tutorías Online • Proyectos", font=get_font(FONT_BOLD, 25), fill=CYAN + (255,))

    # Tags
    pills = [
        "Matemáticas y Cálculo",
        "Física y Estática",
        "Estructuras NSR-10",
        "Python & Programación",
    ]
    px, py = 64, 285
    f_pill = get_font(FONT_BOLD, 24)
    for idx, ptxt in enumerate(pills):
        bbox = draw.textbbox((0, 0), ptxt, font=f_pill)
        pw = (bbox[2] - bbox[0]) + 44
        if px + pw > 860:
            px = 64
            py += 64
        draw.rounded_rectangle((px, py, px + pw, py + 48), radius=24, fill=NAVY + (235,), outline=CYAN + (255,), width=2)
        draw.text((px + 22, py + 10), ptxt, font=f_pill, fill=WHITE + (255,))
        px += pw + 18

    # Bottom Messenger CTA (no phone number)
    draw_fb_cta_bar(
        canvas,
        (64, 445, 860, 565),
        "ESCRÍBENOS POR MENSAJE EN FACEBOOK",
        "Respuesta rápida por Inbox • Horarios flexibles online y presencial",
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
    cta_title="ESCRÍBENOS POR MENSAJE EN FACEBOOK",
    cta_sub="Te atendemos por Inbox y coordinamos tu asesoría",
):
    W, H = size
    canvas = Image.new("RGBA", (W, H), NAVY_DARK + (255,))
    draw = ImageDraw.Draw(canvas)

    # Subtle blueprint grid
    for gx in range(0, W, 54):
        draw.line([(gx, 0), (gx, H)], fill=(18, 42, 82, 255), width=1)
    for gy in range(0, H, 54):
        draw.line([(0, gy), (W, gy)], fill=(18, 42, 82, 255), width=1)

    # Top accent bar + diagonal header highlight
    draw.rectangle((0, 0, W, 12), fill=accent_color + (255,))

    # Urgent top-left pill badge
    f_badge = get_font(FONT_BLACK, 24)
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge)
    bw = (bb[2] - bb[0]) + 46
    draw.rounded_rectangle((54, 40, 54 + bw, 88), radius=24, fill=accent_color + (255,))
    draw.text((77, 50), badge_txt, font=f_badge, fill=NAVY_DARK + (255,))

    # Brand badge logo top-right
    l_size = 132
    b_rs = badge_logo.resize((l_size, l_size), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (W - l_size - 48, 30), b_rs)

    # Headlines
    draw.text((54, 110), title_l1, font=get_font(FONT_BLACK, 54), fill=WHITE + (255,))
    draw.text((54, 174), title_l2, font=get_font(FONT_BLACK, 54), fill=accent_color + (255,))
    draw.text((54, 244), subtitle, font=get_font(FONT_BOLD, 26), fill=CYAN + (255,))

    # Hero photo panel
    photo_y0 = 296
    photo_h = 370 if H >= 1300 else 270
    paste_rounded_photo(canvas, photo_path, (54, photo_y0, W - 54, photo_y0 + photo_h), radius=28, border_px=4, border_col=accent_color)

    # Bullets card
    list_y0 = photo_y0 + photo_h + 26
    cta_h = 128
    cta_y0 = H - cta_h - 42
    draw.rounded_rectangle((54, list_y0, W - 54, cta_y0 - 22), radius=24, fill=NAVY + (235,), outline=(44, 82, 140, 255), width=2)

    cy = list_y0 + 26
    f_bul = get_font(FONT_BOLD, 27 if H >= 1300 else 24)
    step_y = 64 if H >= 1300 else 50
    for item in bullets:
        draw_check_circle(draw, 98, cy + 16, r=16, bg=accent_color, fg=NAVY_DARK)
        draw.text((132, cy), item, font=f_bul, fill=WHITE + (255,))
        cy += step_y

    # Bottom Facebook Messenger CTA
    draw_fb_cta_bar(canvas, (54, cta_y0, W - 54, cta_y0 + cta_h), cta_title, cta_sub, bg=ROYAL)

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

    # Brand logo centered top
    b_rs = badge_logo.resize((176, 176), Image.Resampling.LANCZOS)
    canvas.paste(b_rs, (W - 226, 44), b_rs)

    # Top badge
    f_badge = get_font(FONT_BLACK, 28)
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge)
    bw = (bb[2] - bb[0]) + 48
    draw.rounded_rectangle((56, 56, 56 + bw, 114), radius=29, fill=accent_color + (255,))
    draw.text((80, 68), badge_txt, font=f_badge, fill=NAVY_DARK + (255,))

    draw.text((56, 146), "ASESORÍAS EN INGENIERÍA", font=get_font(FONT_BOLD, 30), fill=CYAN + (255,))

    draw.text((56, 232), title_l1, font=get_font(FONT_BLACK, 64), fill=WHITE + (255,))
    draw.text((56, 308), title_l2, font=get_font(FONT_BLACK, 64), fill=accent_color + (255,))
    draw.text((56, 396), subtitle, font=get_font(FONT_BOLD, 31), fill=SLATE + (255,))

    # Main hero photo
    paste_rounded_photo(canvas, photo_top, (56, 465, W - 56, 985), radius=34, border_px=5, border_col=accent_color)

    # Two side-by-side secondary photos
    paste_rounded_photo(canvas, photo_bottom_left, (56, 1015, 522, 1280), radius=26, border_px=4, border_col=CYAN)
    paste_rounded_photo(canvas, photo_bottom_right, (558, 1015, W - 56, 1280), radius=26, border_px=4, border_col=CYAN)

    # Bullets
    cy = 1326
    f_bul = get_font(FONT_BOLD, 32)
    for b in bullets:
        draw_check_circle(draw, 94, cy + 18, r=18, bg=accent_color, fg=NAVY_DARK)
        draw.text((134, cy), b, font=f_bul, fill=WHITE + (255,))
        cy += 76

    # Bottom Messenger CTA (no phone number)
    draw_fb_cta_bar(
        canvas,
        (56, 1685, W - 56, 1855),
        "ENVÍANOS UN MENSAJE POR FACEBOOK",
        "Escríbenos al Inbox / Messenger • Cupos disponibles esta semana",
        bg=ROYAL,
    )

    out_path = OUT_AVISOS / out_name
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def generate_upbeat_audio_wav(wav_path: Path, duration_sec: float = 15.0, sample_rate: int = 22050):
    """Generates clean, uplifting academic-tech background music (major progression + soft pulse)."""
    n_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    # Uplifting progression: Fmaj -> Cmaj -> Gmaj -> Am (3.75s each)
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
        # Soft energetic 128 BPM pluck
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
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-i", str(wav_path),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        str(out_mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    f_top = get_font(FONT_BLACK, int(W * 0.042))
    f_badge = get_font(FONT_BOLD, int(W * 0.028))
    f_title = get_font(FONT_BLACK, int(W * 0.050))
    f_sub = get_font(FONT_BOLD, int(W * 0.034))
    f_cta = get_font(FONT_BLACK, int(W * 0.038))

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

            # Top header
            hdr_h = int(H * 0.115)
            odraw.rectangle((0, 0, W, hdr_h), fill=NAVY + (232,))
            odraw.rectangle((0, hdr_h, W, hdr_h + 6), fill=accent_color + (255,))
            odraw.text((28, int(hdr_h * 0.22)), "ASESORÍAS EN INGENIERÍA", font=f_top, fill=WHITE + (255,))
            odraw.text((28, int(hdr_h * 0.58)), kicker_txt, font=f_badge, fill=CYAN + (255,))

            overlay.paste(logo_rs, (W - logo_s - 18, max(8, (hdr_h - logo_s) // 2)), logo_rs)

            # Animated lower-third
            slide_in = min(1.0, f_idx / 8.0)
            box_y0 = int(H * 0.71)
            odraw.rectangle((0, box_y0, W, H), fill=NAVY_DARK + (236,))
            odraw.rectangle((0, box_y0, int(W * slide_in), box_y0 + 8), fill=accent_color + (255,))

            odraw.text((32, box_y0 + 24), title_txt, font=f_title, fill=accent_color + (255,))
            odraw.text((32, box_y0 + 24 + int(W * 0.068)), sub_txt, font=f_sub, fill=WHITE + (255,))

            # Persistent Facebook Messenger CTA strip (NO phone number)
            cta_y = H - int(H * 0.09)
            odraw.rectangle((0, cta_y, W, H), fill=ROYAL + (255,))
            icon_r = int(H * 0.025)
            draw_messenger_icon(odraw, 48, cta_y + int((H - cta_y) * 0.5), r=icon_r, bg=WHITE, fg=MESSENGER_BLUE)
            odraw.text((88, cta_y + int((H - cta_y) * 0.25)), "ESCRÍBENOS POR FACEBOOK (MESSENGER)", font=f_cta, fill=WHITE + (255,))

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

    # 7. Historia 01 (9:16): Últimas Semanas de Estudio
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

    # 8. Historia 02 (9:16): Ingeniería y Programación
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

    # 9. Video 01 (9:16 Reel): Últimas Semanas — Salva Tu Semestre
    v1 = render_promo_video(
        OUT_VIDEOS / "Video_01_Reel_Ultimas_Semanas_Salva_Tu_Semestre_9x16.mp4",
        slides=[
            (h_tutor, "ÚLTIMAS SEMANAS DE ESTUDIO", "SALVA TU SEMESTRE", "Preparación intensiva para parciales y finales"),
            (h_desk, "BACHILLERATO Y UNIVERSIDAD", "MATEMÁTICAS Y CÁLCULO", "Álgebra, Cálculo I/II/III, Ecuaciones y Física"),
            (h_tutor, "EXPLICACIÓN PASO A PASO", "ESTÁTICA Y ESTRUCTURAS", "Resistencia de materiales y diseño NSR-10"),
            (h_night, "PROYECTOS Y ENTREGAS", "PYTHON, MATLAB Y WEB", "Acompañamiento real para tus trabajos técnicos"),
            (h_desk, "ONLINE O PRESENCIAL", "AGENDA TU CLASE HOY", "Escríbenos por mensaje directo en Facebook"),
        ],
        size=(720, 1280),
        badge_logo=badge_logo,
        accent_color=GOLD,
    )
    print("Video generado:", v1.name)

    # 10. Video 02 (9:16 Reel): Ingeniería Civil y Programación
    v2 = render_promo_video(
        OUT_VIDEOS / "Video_02_Reel_Ingenieria_Estructuras_Programacion_9x16.mp4",
        slides=[
            (h_desk, "ASESORÍA TÉCNICA ESPECIALIZADA", "INGENIERÍA CIVIL", "Estática, análisis estructural y presupuestos APU"),
            (h_night, "CÓDIGO PARA INGENIERÍA", "PYTHON Y MATLAB", "Modelado numérico, gráficas y scripts listos"),
            (h_tutor, "CLASES EN VIVO 1 A 1", "ENTIENDE DE VERDAD", "Resolvemos ejercicios tipo parcial paso a paso"),
            (h_desk, "CIERRE DE PERIODO", "CUPOS ESTA SEMANA", "Reserva tu horario antes de los exámenes finales"),
        ],
        size=(720, 1280),
        badge_logo=badge_logo,
        accent_color=CYAN,
    )
    print("Video generado:", v2.name)

    # 11. Video 03 (1:1 Feed Facebook): Campaña Integral Asesorías en Ingeniería
    v3 = render_promo_video(
        OUT_VIDEOS / "Video_03_Feed_Asesorias_en_Ingenieria_1x1.mp4",
        slides=[
            (h_tutor, "ÚLTIMAS SEMANAS DE CLASE", "ASESORÍAS EN INGENIERÍA", "Clases particulares para colegio y universidad"),
            (h_desk, "CIENCIAS EXACTAS", "CÁLCULO, FÍSICA Y ÁLGEBRA", "Preparación rápida para parciales y finales"),
            (h_night, "INGENIERÍA Y CÓDIGO", "ESTRUCTURAS Y PYTHON", "Estática, materiales, NSR-10, MATLAB y JS"),
            (h_tutor, "ATENCIÓN PERSONALIZADA", "CONTÁCTANOS EN FACEBOOK", "Envíanos un mensaje por Inbox y agenda hoy"),
        ],
        size=(720, 720),
        badge_logo=badge_logo,
        accent_color=GOLD,
    )
    print("Video generado:", v3.name)


if __name__ == "__main__":
    main()
