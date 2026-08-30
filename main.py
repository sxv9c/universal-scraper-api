import os
import re
import uvicorn
import requests
from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI(title="Universal Downloader API الخارق")

@app.get("/download")
def download_media(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="الرابط مطلوب")
        
    clean_url = url.strip()

    # --- مسار الطوارئ الذكي لروابط يوتيوب لتخطي حظر السيرفرات ---
    if "youtube.com" in clean_url or "youtu.be" in clean_url:
        try:
            # استخدام بوابة Cobalt المستقرة عالمياً لتنزيل ميديا يوتيوب بدون حظر
            api_url = "https://cobalt.tools"
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            payload = {"url": clean_url, "videoQuality": "720", "filenamePattern": "basic"}
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "stream" or "url" in data:
                    return {
                        "success": True,
                        "source": "single_media",
                        "type": "video",
                        "media_url": data["url"],
                        "title": "YouTube Video 🎬"
                    }
            
            # محرك احتياطي مجاني لليوتيوب في حال تعطل الأول
            backup_url = f"https://vkr.me{clean_url}"
            backup_resp = requests.get(backup_url, timeout=15).json()
            if "data" in backup_resp and backup_resp["data"].get("media"):
                m_url = backup_resp["data"]["media"][0]["url"]
                return {
                    "success": True,
                    "source": "single_media",
                    "type": "video",
                    "media_url": m_url,
                    "title": "YouTube Video 🎬"
                }
        except Exception as e:
            print(f"YouTube Bypass Error: {e}")
            raise HTTPException(status_code=500, detail="فشل استخراج رابط يوتيوب بسبب قيود المنصة.")

    # --- مسار المعالجة الخاص والمستقر لروابط إنستغرام مالتك ---
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            
            # ألبومات إنستغرام المتعددة
            if 'entries' in info and info['entries']:
                links = []
                for entry in info['entries']:
                    if entry:
                        entry_url = entry.get('url', '')
                        is_vid = entry.get('vcodec') != 'none' or ".mp4" in entry_url or "video" in entry.get('ext', '')
                        links.append({
                            "url": entry_url,
                            "type": "video" if is_vid else "image"
                        })
                return {"success": True, "source": "playlist_or_carousel", "data": links}
                
            # ميديا إنستغرام المفردة
            media_url = info.get('url', '')
            is_video = info.get('vcodec') != 'none' or ".mp4" in media_url or "video" in info.get('ext', '')
            title = info.get('title', '⚡ تم الاستخراج بنجاح!')
            
            return {
                "success": True, 
                "source": "single_media",
                "type": "video" if is_video else "image", 
                "media_url": media_url,
                "title": title
            }
    except Exception as e:
        print(f"Instagram API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
