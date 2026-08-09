# gorsel.py — Görsel kütüphanesi modeli (OpenArt önceden üretir, pipeline kullanır).
#
# Her sahnenin senaryodaki "gorsel" alanı artık bir DOSYA ADIDIR
# (ör. "cami_kim_kirdi_03.png") ve repodaki  gorseller/  klasöründe bulunur.
# Görseller OpenArt ile SOHBETTE parti parti üretilip repoya commit edilir.
# Burada CANLI API çağrısı YOKTUR -> kredi yakmaz, otonom çalışır.
#
# Dosya bulunamazsa placeholder kart üretir (pipeline çökmez, log'a düşer).

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

BOYUT = {"shorts": (1080, 1920), "uzun": (1920, 1080)}
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
KOK = os.path.dirname(os.path.abspath(__file__))
GORSEL_KLASOR = os.path.join(KOK, "gorseller")


def _boyut(config):
    return BOYUT.get(config.get("format", "uzun"), BOYUT["uzun"])


def gorsel_uret(gorsel_ad, cikti_png, config):
    """
    gorsel_ad: gorseller/ klasöründeki dosya adı (senaryodaki "gorsel" alanı).
    Görseli hedef en-boy oranına uyarlayıp cikti_png'ye yazar; yoksa placeholder.
    """
    kaynak = os.path.join(GORSEL_KLASOR, gorsel_ad)
    if os.path.exists(kaynak):
        return _uyarla(kaynak, cikti_png, config)
    print(f"[!] Görsel bulunamadı: {kaynak} -> placeholder kullanılıyor")
    return _placeholder(gorsel_ad, cikti_png, config)


def _uyarla(kaynak, cikti_png, config):
    """Görseli hedef çözünürlüğe 'cover' mantığıyla kırpıp ölçekler."""
    w, h = _boyut(config)
    im = Image.open(kaynak).convert("RGB")
    iw, ih = im.size
    olcek = max(w / iw, h / ih)
    yeni = (max(int(iw * olcek), w), max(int(ih * olcek), h))
    im = im.resize(yeni, Image.LANCZOS)
    sol = (yeni[0] - w) // 2
    ust = (yeni[1] - h) // 2
    im = im.crop((sol, ust, sol + w, ust + h))
    im.save(cikti_png)
    return cikti_png


def _placeholder(ad, cikti_png, config):
    w, h = _boyut(config)
    img = Image.new("RGB", (w, h), (32, 40, 64))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT, 42)
    except Exception:
        font = ImageFont.load_default()
    metin = "[GÖRSEL EKSİK]\n" + "\n".join(textwrap.wrap(ad, 30))
    d.multiline_text((60, h // 3), metin, fill=(230, 230, 240), font=font, spacing=12)
    img.save(cikti_png)
    return cikti_png
