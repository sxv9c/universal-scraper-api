import os
import re
import uvicorn
import requests
import yt_dlp
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Universal Downloader API الخارق")

@app.get("/download")
def download_media(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="الرابط مطلوب")
        
    clean_url = url.strip()

    # --- 🎬 1. مسار المعالجة لروابط يوتيوب والشورتس ---
    if "youtube.com" in clean_url or "youtu.be" in clean_url:
        try:
            api_url = f"https://vkr.me{clean_url}"
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "media" in data["data"]:
                    media_list = data["data"]["media"]
                    for item in media_list:
                        if item.get("type") == "video" or ".mp4" in item.get("url", ""):
                            return {
                                "success": True,
                                "source": "single_media",
                                "type": "video",
                                "media_url": item["url"],
                                "title": data["data"].get("title", "YouTube Video 🎬")
                            }

            backup_url = f"https://workers.dev{clean_url}"
            backup_resp = requests.get(backup_url, timeout=15).json()
            if backup_resp.get("url"):
                return {
                    "success": True,
                    "source": "single_media",
                    "type": "video",
                    "media_url": backup_resp["url"],
                    "title": backup_resp.get("title", "YouTube Shorts 🎬")
                }
                
        except Exception as e:
            print(f"YouTube Engine Log: {e}")
            pass

    # --- 📸 2. مسار المعالجة لروابط إنستغرام مالتك ---
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
        print(f"Instagram API Log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
