import os
import uvicorn
from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI(title="Universal Downloader API الخارق")

@app.get("/download")
def download_media(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="الرابط مطلوب")
        
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
            info = ydl.extract_info(url, download=False)
            
            # فحص إذا كان الرابط ألبوم انستغرام أو قائمة تشغيل يوتيوب
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
                
            # إذا كانت ميديا مفردة (فيديو، شورتس، ريلز، صورة)
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
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
