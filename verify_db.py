
import sys
import os

# Proje kök dizinini Python yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import database
from app.database.models import Article
from sqlalchemy.orm import Session
import logging

# Temel log yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def verify_articles():
    """
    Veritabanındaki son 5 makaleyi okur ve bilgilerini yazdırır.
    """
    logging.info("Veritabanındaki son 5 makale kontrol ediliyor...")
    db: Session = next(database.get_db())
    
    try:
        # Son eklenen 5 makaleyi çek
        recent_articles = db.query(Article).order_by(Article.id.desc()).limit(5).all()
        
        if not recent_articles:
            logging.warning("Veritabanında hiç makale bulunamadı.")
            return

        print("\n--- VERİTABANI KONTROL SONUÇLARI ---\n")
        for i, article in enumerate(recent_articles, 1):
            print(f"--- Makale #{i} ---")
            print(f"  ID: {article.id}")
            print(f"  Başlık: {article.title}")
            print(f"  Kaynak: {article.source}")
            print(f"  URL: {article.url}")
            print(f"  Yayın Tarihi: {article.publish_date}")
            print(f"  Özet: {article.summary}")
            print(f"  Anahtar Kelimeler: {article.keywords}")
            # print(f"  İçerik (ilk 100 karakter): {article.content[:100] if article.content else 'Yok'}")
            print("-" * (len(str(i)) + 14))
        print("\n--- KONTROL TAMAMLANDI ---\n")

    except Exception as e:
        logging.error(f"Veritabanı kontrolü sırasında bir hata oluştu: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    verify_articles()

