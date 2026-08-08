# elevenlabs_tts.py — ElevenLabs seslendirme (çok dilli).
import os
import time
import requests

_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


def seslendir_elevenlabs(metin, cikti_yolu, voice_id=None, api_key=None,
                         model="eleven_multilingual_v2"):
    """Metni ElevenLabs ile seslendirir, mp3 olarak yazar, yolu döndürür."""
    api_key = api_key or os.environ["ELEVENLABS_API_KEY"]
    voice_id = voice_id or os.environ.get("ELEVENLABS_VOICE_ID")
    if not voice_id:
        raise ValueError("voice_id gerekli: ELEVENLABS_VOICE_ID secret'ı ekle.")

    url = _URL.format(voice_id=voice_id)
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "text": metin,
        "model_id": model,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75,
                           "style": 0.0, "use_speaker_boost": True},
    }
    son = ""
    for _ in range(3):
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        if r.status_code == 200:
            with open(cikti_yolu, "wb") as f:
                f.write(r.content)
            return cikti_yolu
        son = f"{r.status_code}: {r.text[:300]}"
        if r.status_code in (429, 500, 502, 503):
            time.sleep(20)
            continue
        break
    raise RuntimeError(f"ElevenLabs hata -> {son}")
