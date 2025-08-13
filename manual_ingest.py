
import asyncio
import sys
import os

# Proje kök dizinini Python yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ingestion_service import process_and_save_article
from app.database import database
from app.crud import article_crud
from datetime import datetime
import logging

# Temel log yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Eklenecek makalelerin listesi
# ÖNEMLİ: Tarihleri 'YYYY-MM-DD' formatında ekleyin.
ARTICLES_TO_ADD = [
    {
        "url": "https://blog.google/technology/ai/google-io-2024-100-announcements/",
        "source": "Google I/O 2024 Official Blog",
        "title": "100 things we announced at I/O 2024",
        "publish_date": "2024-05-14" 
    },
    {
        "url": "https://docs.anthropic.com/en/docs/about-claude/models",
        "source": "Anthropic Models Documentation",
        "title": "Models overview",
        "publish_date": "2024-08-01" # Gerçek tarih bilinmiyorsa tahmini bir tarih girin
    }
]

async def main():
    """
    Belirtilen makaleleri veritabanına ekleyen ana fonksiyon.
    """
    logging.info("Manuel makale ekleme işlemi başladı.")
    db = next(database.get_db())
    
    try:
        for article_data in ARTICLES_TO_ADD:
            url = article_data["url"]
            logging.info(f"İşleniyor: {url}")
            
            # Makalenin veritabanında olup olmadığını kontrol et
            if article_crud.get_article_by_url(db, url=url):
                logging.info(f"Makale zaten mevcut, atlanıyor: {url}")
                continue

            # Tarih dizesini datetime nesnesine dönüştür
            try:
                publish_date_obj = datetime.strptime(article_data["publish_date"], '%Y-%m-%d')
            except ValueError:
                logging.error(f"Hatalı tarih formatı: {article_data['publish_date']}. 'YYYY-MM-DD' formatında olmalıdır. Atlanıyor: {url}")
                continue

            # process_and_save_article fonksiyonunun beklediği formatta veri hazırla
            full_article_data = {
                "url": url,
                "title": article_data["title"],
                "source": article_data["source"],
                "publish_date": publish_date_obj
            }
            
            # Asenkron fonksiyonu çağır
            await process_and_save_article(full_article_data)
            logging.info(f"Başarıyla işlendi ve kaydedildi: {url}")

    finally:
        db.close()
        logging.info("Manuel makale ekleme işlemi tamamlandı.")

if __name__ == "__main__":
    # Nest asyncio, uvicorn gibi bir event loop çalışırken başka bir loop çalıştırmamızı sağlar
    # Terminalden direkt çalıştırdığımız için normalde gerek yok ama ne olur ne olmaz ekliyorum.
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass
        
    asyncio.run(main())

