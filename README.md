# izgfilm — otonom YouTube pipeline (v0 iskelet)

Her gün sıradaki bölümü üretip YouTube'a yükleyen GitHub Actions sistemi.
Akış: `senaryolar.json` → ses (TTS) → sahne görselleri → `video.py` birleştirir → YouTube'a zamanlanmış yükleme → `durum.json` ilerler.

## Dosyalar
- `otomasyon.py` — ana akış (orkestrasyon)
- `tts.py` / `elevenlabs_tts.py` — seslendirme (ElevenLabs ya da Google)
- `gorsel.py` — sahne görseli (placeholder / ai_gorsel / pexels — TAKILABİLİR)
- `video.py` — görsel+ses+altyazı → mp4 (Ken Burns hareket)
- `youtube_yukle.py` — zamanlanmış yükleme
- `senaryolar.json` — bölüm bankası (sen doldurursun / birlikte yazarız)
- `durum.json` — nerede kaldık
- `config.json` — kanal ayarları
- `.github/workflows/otomasyon.yml` — günlük cron (19:00 TR)

## Kurulum (senin yapacakların)
1. Bu dosyaları repoya ekle.
2. Settings → Secrets and variables → Actions:
   - **Secrets:** `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`,
     `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
     (Google TTS kullanacaksan `GOOGLE_TTS_KEY`; AI görsel için `GORSEL_API_URL`/`GORSEL_API_KEY`; Pexels için `PEXELS_KEY`)
   - **Variables:** `SES_SAGLAYICI` = `elevenlabs`
3. YouTube refresh token'ı bir kez üret (consent screen'i **Published** yap, yoksa 7 günde bozulur).
4. Actions sekmesinden **Run workflow** ile elle bir test çalıştır.

## Önce GÜVENLİ MOD
`config.json` içinde `"gizlilik": "unlisted"` ve `"gorsel_saglayici": "placeholder"`
ile başla. Böylece hiçbir dış görsel API'sine gerek kalmadan boru hattının
(ses → video → yükleme) çalıştığını görürsün. Sonra:
- görseli gerçek üreticiye çevir (`ai_gorsel` veya `pexels`),
- `"gizlilik": "private"` yaparsan ertesi gün 19:00 TR'de otomatik public olur.

## Dürüst not (v0)
Bu iskelet canlı API'lere karşı TEST EDİLMEDİ (ortamımda ağ yok). İlk gerçek
çalıştırmada muhtemelen 1 hata ayıklama turu gerekir — özellikle `video.py`
(ffmpeg) ve `gorsel.py` (seçtiğin sağlayıcı). Çalıştır, çıktı/hata logunu bana
yapıştır, birlikte düzeltiriz.

## Açık karar
**Görsel nasıl üretilecek?** Çizgi film "AI video" (pahalı, yarı-manuel) ister;
bu iskelet daha ucuz "AI görsel + hareket" yolunu varsayar. Hangisini
istediğini söyle, `gorsel.py`'yi ona göre kesinleştirelim.
