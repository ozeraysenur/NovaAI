import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
import feedparser
import requests
from trafilatura import extract


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from app.core.config import OPENAI_API_KEY
from app.crud import article_crud
from app.database import schemas, database

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Asenkron uyumluluk için
import nest_asyncio
nest_asyncio.apply()

NEWS_SOURCES = {
    # Core AI Labs
    "OpenAI Blog": "https://openai.com/blog/rss.xml",
    "Google AI Blog": "https://ai.googleblog.com/feeds/posts/default?alt=rss",
    "Anthropic News": "https://www.anthropic.com/news/rss.xml",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
    "Perplexity Blog": "https://blog.perplexity.ai/rss.xml",

    # Major Tech & AI News Outlets
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Wired AI": "https://www.wired.com/feed/tag/artificial-intelligence/latest/rss",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "Ars Technica AI": "https://arstechnica.com/tag/ai/feed/",
}

def get_llm():
    """LLM modelini başlatır."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY ortam değişkeni ayarlanmadı.")
    return ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0.3)

async def process_content_with_llm(content: str):
    """Verilen metni kullanarak özet ve anahtar kelimeler üretir."""
    llm = get_llm()

    # Özetleme prompt'u
    summary_prompt = ChatPromptTemplate.from_template(
        "Aşağıdaki makale metnini analiz et ve yaklaşık 50-75 kelimelik kısa ve öz bir özetini **tamamen Türkçe** olarak yaz. "
        "Eğer metin çok kısaysa veya anlamsızsa, yine de elinden geldiğince bir cümlelik bir özet çıkarmaya çalış."
        "\n\n--- MAKAELİ METNİ ---\n{text}"
    )
    summary_chain = summary_prompt | llm | StrOutputParser()

    # Anahtar kelime prompt'u
    keywords_prompt = ChatPromptTemplate.from_template(
        "Aşağıdaki makale metnine dayanarak, en ilgili 5 anahtar kelimeyi virgülle "
        "ayırarak Türkçe olarak listele (örneğin: yapay zeka, makine öğrenmesi, dil modelleri):\n\n{text}"
    )
    keywords_chain = keywords_prompt | llm | StrOutputParser()

    # Eş zamanlı çalıştırma
    summary_task = summary_chain.ainvoke({"text": content})
    keywords_task = keywords_chain.ainvoke({"text": content})

    summary, keywords = await asyncio.gather(summary_task, keywords_task)
    return summary.strip(), keywords.strip()

async def scrape_and_process_article(url: str, source: str, db: Session):
    """Tek bir makaleyi indirir, işler ve veritabanına kaydeder."""
    logger.info(f"İşleniyor: {url}")
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        logger.warning(f"İndirilemedi: {url}")
        return

    content = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
    if not content or len(content) < 200: # Kısa içerikleri atla
        logger.info(f"Yetersiz içerik, atlanıyor: {url}")
        return

    try:
        summary, keywords = await process_content_with_llm(content)
        
        # trafilatura'dan başlık ve tarihi de alabiliriz, ancak RSS'ten almak daha güvenilir olabilir.
        # Bu kısmı RSS'ten gelen veriyle birleştireceğiz.
        # Şimdilik bu bilgiyi geçici olarak boş bırakıp CRUD'da dolduracağız.
        
        return {
            "url": url,
            "source": source,
            "content": content,
            "summary": summary,
            "keywords": keywords,
        }

    except Exception as e:
        logger.error(f"LLM işlenirken hata oluştu ({url}): {e}")
        return None


async def ingest_news():
    """Haber kaynaklarından makaleleri toplar ve işler."""
    logger.info("Haber toplama işlemi başladı.")
    
    articles_to_process = []
    # with context manager'ı kullanarak db oturumunu yönetelim.
    try:
        db = next(database.get_db())
        for source, rss_url in NEWS_SOURCES.items():
            logger.info(f"Kaynak işleniyor: {source} ({rss_url})")
            try:
                feed = feedparser.parse(rss_url)
                # Sadece en son 30 makaleyi alarak süreci hızlandır.
                for entry in feed.entries[:30]:
                    if not article_crud.get_article_by_url(db, url=entry.link):
                        articles_to_process.append({
                            "url": entry.link,
                            "title": entry.title,
                            "source": source,
                            "publish_date": datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
                        })
                logger.info(f"Kaynak tamamlandı: {source}. İşlenecek {len(articles_to_process)} yeni makale bulundu.")
            except Exception as e:
                logger.error(f"RSS beslemesi okunurken hata ({rss_url}): {e}")

    finally:
        db.close()

    # Toplu olarak asenkron görevleri çalıştır
    if articles_to_process:
        logger.info(f"Toplam {len(articles_to_process)} makale için içerik indirme ve işleme başlatılıyor...")
        tasks = [process_and_save_article(article_data) for article_data in articles_to_process]
        await asyncio.gather(*tasks)

    logger.info("Haber toplama işlemi tamamlandı.")

async def process_and_save_article(article_data: dict):
    """Bir makaleyi indirir, işler ve veritabanına kaydeder."""
    url = article_data["url"]
    logger.info(f"-> Başlatıldı: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://www.google.com/'
    }

    loop = asyncio.get_event_loop()
    try:
        # Adım 1: İçerik indirme (requests senkron olduğu için asenkron loop'ta çalıştır)
        logger.debug(f"   [1/4] İçerik indiriliyor: {url}")
        response = await loop.run_in_executor(
            None, 
            lambda: requests.get(url, headers=headers, timeout=15)
        )
        response.raise_for_status()  # 4xx veya 5xx hatası varsa exception fırlat
        html_content = response.text

        # Adım 2: Metin ayıklama
        logger.debug(f"   [2/4] Metin ayıklanıyor: {url}")
        content = extract(html_content, include_comments=False, include_tables=False)
        if not content:
            logger.info(f"<- İçerik bulunamadı, atlanıyor: {url}")
            return
        
        # Adım 3: LLM ile işleme
        logger.debug(f"   [3/4] LLM ile işleniyor: {url}")
        summary, keywords = await process_content_with_llm(content)
        
        logger.debug(f"LLM Sonucu -> Özet alındı mı?: {summary is not None and len(summary) > 10}, Anahtar Kelimeler alındı mı?: {keywords is not None and len(keywords) > 5}")

        # Eğer özet veya anahtar kelimeler boşsa veya anlamsızsa, kaydetme.
        if not summary or not keywords:
            logger.warning(f"<- LLM'den geçerli özet alınamadı, makale kaydedilmeyecek: {url}")
            return

        # --- YENİ DOĞRULAMA ADIMI ---
        # 2. Özet Doğrulaması: Özet boş olamaz.
        if not summary or len(summary.strip()) < 20:
            logger.warning(f"<- Yetersiz özet, makale kaydedilmeyecek: {url}")
            return

        article_to_create = schemas.ArticleCreate(
            **article_data,
            content=content,
            summary=summary,
            keywords=keywords
        )

        # Adım 4: Veritabanına kaydetme
        logger.debug(f"   [4/4] Veritabanına kaydediliyor: {url}")
        with next(database.get_db()) as db:
            article_crud.create_article(db, article=article_to_create)
        logger.info(f"<- Başarıyla tamamlandı: {url}")

    except requests.exceptions.RequestException as e:
        logger.error(f"<- İndirme hatası ({url}): {e}")
    except Exception as e:
        logger.error(f"<- Genel bir hata oluştu ({url}): {e}", exc_info=True)

