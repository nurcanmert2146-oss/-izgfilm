# otomasyon.py — Ana akış: sıradaki bölüm -> ses -> görsel -> video -> yükleme.
import os
import json

import tts
import gorsel
import video
import youtube_yukle as yt

KOK = os.path.dirname(os.path.abspath(__file__))
IS = "/tmp/izg"


def _oku(ad):
    with open(os.path.join(KOK, ad), encoding="utf-8") as f:
        return json.load(f)


def _yaz(ad, veri):
    with open(os.path.join(KOK, ad), "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)


def main():
    os.makedirs(IS, exist_ok=True)
    config = _oku("config.json")
    senaryolar = _oku("senaryolar.json")
    durum = _oku("durum.json")

    idx = durum["sonraki"] % len(senaryolar)
    bolum = senaryolar[idx]
    print(f"[i] Bölüm {idx}: {bolum['baslik']}")

    sahne_verileri = []
    for i, s in enumerate(bolum["sahneler"]):
        ses = os.path.join(IS, f"ses_{i}.mp3")
        png = os.path.join(IS, f"gorsel_{i}.png")
        tts.seslendir(s["metin"], ses, config)
        gorsel.gorsel_uret(s["gorsel"], png, config)
        sahne_verileri.append({"ses": ses, "gorsel": png, "metin": s["metin"]})

    cikti = os.path.join(IS, "video.mp4")
    video.uret_video(sahne_verileri, cikti, config)
    print("[i] Video hazır:", cikti)

    aciklama = f"{bolum['baslik']}\n\nOtomatik üretim."
    etiketler = ["çizgi film", "animasyon", "shorts"]
    vid = yt.yukle(
        cikti, bolum["baslik"], aciklama, etiketler,
        yayin_saati_utc=config.get("yayin_saati_utc", 16),
        gizlilik=config.get("gizlilik", "unlisted"),
    )
    print(f"[i] Yüklendi: https://youtu.be/{vid}")

    durum["sonraki"] = idx + 1
    durum.setdefault("yapilan", []).append({"baslik": bolum["baslik"], "video_id": vid})
    _yaz("durum.json", durum)
    print("[i] durum.json güncellendi.")


if __name__ == "__main__":
    main()
