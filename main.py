import os
import re
import uvicorn
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Universal Downloader API الخارق")

@app.get("/download")
def download_media(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="الرابط مطلوب")
        
    clean_url = url.strip()

    # --- 🛠️ بوابة المعالجة الخارقة الموحدة (يوتيوب + إنستغرام) ---
    try:
        # استخدام بوابة سحابية عالمية ومستقرة تتخطى حظر السيرفرات تلقائياً
        api_url = f"https://vkr.me{clean_url}"
        response = requests.get(api_url, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            # 🎬 فحص إذا كانت البيانات المستلمة لروابط يوتيوب أو ميديا منفردة
            if "data" in data and "media" in data["data"]:
                media_data = data["data"]["media"]
                
                # إذا كانت الميديا عبارة عن ألبوم (انستغرام متعدد)
                if isinstance(media_data, list):
                    links = []
                    for item in media_data:
                        m_url = item.get("url")
                        is_vid = item.get("type") == "video" or ".mp4" in m_url
                        links.append({
                            "url": m_url,
                            "type": "video" if is_vid else "image"
                        })
                    return {"success": True, "source": "playlist_or_carousel", "data": links}
                
                # إذا كانت ميديا منفردة (فيديو يوتيوب، شورتس، ريلز، صورة)
                elif isinstance(media_data, dict) or "url" in data["data"]:
                    # محاولة استخراج الرابط المباشر
                    m_url = data["data"].get("url") or media_data.get("url")
                    if m_url:
                        return {
                            "success": True,
                            "source": "single_media",
                            "type": "video" if ("youtube" in clean_url or "youtu.be" in clean_url or ".mp4" in m_url) else "image",
                            "media_url": m_url,
                            "title": data["data"].get("title", "Universal Media 🎬")
                        }

        # --- 🚀 المحرك الاحتياطي المباشر لليوتيوب وإنستغرام ---
        backup_url = f"https://workers.dev{clean_url}" if "instagram" in clean_url else f"https://workers.dev{clean_url}"
        backup_resp = requests.get(backup_url, timeout=15).json()
        
        if backup_resp.get("url") or backup_resp.get("media_url"):
            m_url = backup_resp.get("url") or backup_resp.get("media_url")
            return {
                "success": True,
                "source": "single_media",
                "type": "video",
                "media_url": m_url,
                "title": backup_resp.get("title", "📥 تم التحميل بنجاح!")
            }

    except Exception as e:
        print(f"Global Scraper Engine Error: {e}")
        pass

    # إذا فشلت جميع المحركات السحابية بسبب جودة الرابط أو الخصوصية
    raise HTTPException(status_code=500, detail="فشل السيرفر في فك التشفير. تأكد أن الحساب عام (Public).")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
