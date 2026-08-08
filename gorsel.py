# gorsel.py — Sahne görseli üretimi. TAKILABİLİR (pluggable) tasarım.
#
# config["gorsel_saglayici"]:
#   "placeholder" -> internetsiz test kartı (boru hattını denemek için)
#   "ai_gorsel"   -> AI görsel üretici (GORSEL_API_URL + GORSEL_API_KEY env gerekli)
#   "pexels"      -> Pexels'ten stok fotoğraf (PEXELS_KEY env gerekli)
#
# NOT: Çizgi film "AI video" değil; burada her sahneye bir GÖRSEL üretip
# video.py'de Ken Burns ile hareket veriyoruz. Gerçek animasyon istenirse
# bu modül AI-video sağlayıcısına çevrilir (maliyet + yarı-manuel uyarısı geçerli).

import os
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont

BOYUT = {"shorts": (1080, 1920), "uzun": (1920, 1080)}


def gorsel_uret(prompt, cikti_png, config):
    saglayici = config.get("gorsel_saglayici", "placeholder")
    if saglayici == "ai_gorsel":
        return _ai_gorsel(prompt, cikti_png, config)
    if saglayici == "pexels":
        return _pexels(prompt, cikti_png, config)
    return _placeholder(prompt, cikti_png, config)


def _boyut(config):
    return BOYUT.get(config.get("format", "shorts"), BOYUT["shorts"])


def _placeholder(prompt, cikti_png, config):
    w, h = _boyut(config)
    img = Image.new("RGB", (w, h), (32, 40, 64))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
    except Exception:
        font = ImageFont.load_default()
    metin = "[TEST GÖRSELİ]\n" + "\n".join(textwrap.wrap(prompt, 26))
    d.multiline_text((60, h // 3), metin, fill=(230, 230, 240), font=font, spacing=12)
    img.save(cikti_png)
    return cikti_png


def _ai_gorsel(prompt, cikti_png, config):
    """Genel AI görsel üretici. Sağlayıcıya göre GORSEL_API_URL'i sen ayarlarsın."""
    url = os.environ["GORSEL_API_URL"]          # ör. sağlayıcının image endpoint'i
    key = os.environ.get("GORSEL_API_KEY", "")
    stil = config.get("gorsel_stil_eki", "")
    w, h = _boyut(config)
    tam_prompt = f"{prompt}, {stil}".strip(", ")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    body = {"prompt": tam_prompt, "width": w, "height": h}
    r = requests.post(url, json=body, headers=headers, timeout=180)
    r.raise_for_status()
    # Sağlayıcı ya ham görsel byte'ı ya da {"image_base64": ...} döndürür.
    ctype = r.headers.get("content-type", "")
    if ctype.startswith("image/"):
        with open(cikti_png, "wb") as f:
            f.write(r.content)
    else:
        import base64
        b64 = r.json().get("image_base64") or r.json()["data"][0]["b64_json"]
        with open(cikti_png, "wb") as f:
            f.write(base64.b64decode(b64))
    return cikti_png


def _pexels(prompt, cikti_png, config):
    key = os.environ["PEXELS_KEY"]
    yon = "portrait" if config.get("format", "shorts") == "shorts" else "landscape"
    q = " ".join(prompt.split()[:4])
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": key, "User-Agent": "Mozilla/5.0"},
        params={"query": q, "orientation": yon, "per_page": 5},
        timeout=60,
    )
    r.raise_for_status()
    fotolar = r.json().get("photos", [])
    if not fotolar:
        return _placeholder(prompt, cikti_png, config)
    src = fotolar[0]["src"]["large2x"]
    im = requests.get(src, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    with open(cikti_png, "wb") as f:
        f.write(im.content)
    return cikti_png
