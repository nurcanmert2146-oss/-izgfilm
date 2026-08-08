# video.py — Sahneleri (görsel + ses + altyazı) birleştirip mp4 üretir.
# Her sahne: bir görsel + o sahnenin sesi. Süre = ses uzunluğu.
# Ken Burns (zoompan) hareket + alt yazı (drawtext, textfile ile) yakılır.
import os
import json
import subprocess
import textwrap

BOYUT = {"shorts": (1080, 1920), "uzun": (1920, 1080)}
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _sure(ses_mp3):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", ses_mp3],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return max(float(out), 0.8)


def _sahne_klip(gorsel, ses, metin, cikti, config, tmp):
    w, h = BOYUT.get(config.get("format", "shorts"), BOYUT["shorts"])
    sure = _sure(ses)
    kare = max(int(sure * 30), 24)

    # Alt yazıyı dosyaya yaz (Türkçe karakter/escape derdi olmasın)
    altyazi = "\n".join(textwrap.wrap(metin, 24))
    txt_yolu = os.path.join(tmp, "altyazi.txt")
    with open(txt_yolu, "w", encoding="utf-8") as f:
        f.write(altyazi)

    # Ken Burns: yavaş zoom in
    zoom = ("zoompan=z='min(zoom+0.0009,1.15)':d=%d:"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=%dx%d:fps=30" % (kare, w, h))
    drawtext = (
        "drawtext=fontfile=%s:textfile=%s:reload=0:"
        "fontcolor=white:fontsize=%d:line_spacing=10:"
        "box=1:boxcolor=black@0.55:boxborderw=24:"
        "x=(w-text_w)/2:y=h-text_h-%d"
        % (FONT, txt_yolu, int(w * 0.055), int(h * 0.14))
    )
    vf = "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,%s,%s" % (
        w, h, w, h, zoom, drawtext)

    subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-i", gorsel, "-i", ses,
         "-vf", vf, "-t", "%.3f" % sure, "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-shortest", cikti],
        check=True, capture_output=True,
    )
    return cikti


def uret_video(sahneler, cikti_mp4, config, tmp="/tmp/izg"):
    """sahneler: [{"gorsel": png, "ses": mp3, "metin": str}, ...]"""
    os.makedirs(tmp, exist_ok=True)
    klipler = []
    for i, s in enumerate(sahneler):
        kl = os.path.join(tmp, f"klip_{i}.mp4")
        _sahne_klip(s["gorsel"], s["ses"], s["metin"], kl, config, tmp)
        klipler.append(kl)

    liste = os.path.join(tmp, "liste.txt")
    with open(liste, "w") as f:
        for kl in klipler:
            f.write(f"file '{kl}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", liste,
         "-c", "copy", cikti_mp4],
        check=True, capture_output=True,
    )
    return cikti_mp4
