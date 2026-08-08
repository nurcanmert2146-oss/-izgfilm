# tts.py — Tek kapı: config/env'e göre ElevenLabs ya da Google TTS.
import os
import base64
import requests


def seslendir(metin, cikti_mp3, config):
    saglayici = os.environ.get("SES_SAGLAYICI", config.get("ses_saglayici", "google"))
    if saglayici == "elevenlabs":
        from elevenlabs_tts import seslendir_elevenlabs
        return seslendir_elevenlabs(metin, cikti_mp3)
    return _google_tts(metin, cikti_mp3, config)


def _google_tts(metin, cikti_mp3, config):
    """Google Cloud TTS REST (API key ile). GOOGLE_TTS_KEY secret'ı gerekir."""
    key = os.environ["GOOGLE_TTS_KEY"]
    ses_adi = os.environ.get("GOOGLE_TTS_VOICE", "tr-TR-Wavenet-E")
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={key}"
    body = {
        "input": {"text": metin},
        "voice": {"languageCode": "tr-TR", "name": ses_adi},
        "audioConfig": {"audioEncoding": "MP3"},
    }
    r = requests.post(url, json=body, timeout=120)
    r.raise_for_status()
    ses = base64.b64decode(r.json()["audioContent"])
    with open(cikti_mp3, "wb") as f:
        f.write(ses)
    return cikti_mp3
