# youtube_yukle.py — YouTube Data API v3 ile zamanlanmış yükleme.
# Secret'lar: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
import os
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def _servis():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    return build("youtube", "v3", credentials=creds)


def yukle(dosya, baslik, aciklama, etiketler, yayin_saati_utc=16, gizlilik="private"):
    """Videoyu yükler. gizlilik 'private' ise ertesi gün yayin_saati_utc'de
    otomatik public olacak şekilde zamanlar; 'unlisted' ise anında unlisted."""
    yt = _servis()

    status = {"privacyStatus": gizlilik, "selfDeclaredMadeForKids": False}
    if gizlilik == "private":
        hedef = datetime.now(timezone.utc).replace(
            hour=yayin_saati_utc, minute=0, second=0, microsecond=0)
        if hedef <= datetime.now(timezone.utc):
            hedef += timedelta(days=1)
        status["publishAt"] = hedef.isoformat().replace("+00:00", "Z")

    body = {
        "snippet": {"title": baslik[:100], "description": aciklama,
                    "tags": etiketler, "categoryId": "1"},
        "status": status,
    }
    medya = MediaFileUpload(dosya, chunksize=-1, resumable=True, mimetype="video/mp4")
    istek = yt.videos().insert(part="snippet,status", body=body, media_body=medya)

    yanit = None
    while yanit is None:
        _, yanit = istek.next_chunk()
    return yanit["id"]
