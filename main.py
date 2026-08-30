import os
import re
import uvicorn
from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI(title="Universal Downloader API الخارق")

@app.get("/")
def home():
    return {"status": "running", "message": "API الخاص بك يعمل بنجاح، استخدم مسار /download"}

@app.get("/download")
def download_media(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="الرابط مطلوب")
        
    clean_url = url.strip()
    is_youtube = "youtube.com" in clean_url or "youtu.be" in clean_url

    # تنظيف روابط يوتيوب من أي معاملات زائدة لضمان القبول
    if is_youtube and "?" in clean_url:
        # إبقاء المعرف الأساسي للفيديو وحذف معاملات التتبع لعام 2026
        if "youtu.be" in clean_url:
            clean_url = clean_url.split("?")[0]

    # إعدادات برمجية خارقة تحاكي التطبيقات الرسمية وتتخطى جدار حماية يوتيوب وإنستغرام
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'youtube_include_dash_manifest': False,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'], # محاكاة تشغيل من تطبيق الهاتف الرسمي لتفادي حظر السيرفرات
                'skip': ['dash', 'hls']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            
            # فحص إذا كان الرابط ألبوم انستغرام أو قائمة تشغيل
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
                
            # إذا كانت ميديا مفردة (فيديو يوتيوب، شورتس، ريلز، صورة)
            media_url = info.get('url', '')
            is_video = info.get('vcodec') != 'none' or ".mp4" in media_url or "video" in info.get('ext', '') or is_youtube
            title = info.get('title', '⚡ تم الاستخراج بنجاح!')
            
            return {
                "success": True, 
                "source": "single_media",
                "type": "video" if is_video else "image", 
                "media_url": media_url,
                "title": title
            }
    except Exception as e:
        print(f"API Error details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
