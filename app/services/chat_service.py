import logging
from typing import List
from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.core.config import OPENAI_API_KEY
from app.tools import db_tools
from app.crud import chat_history_crud
from app.database import schemas, database
from app.database.models import Article

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_llm():
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY ortam değişkeni ayarlanmadı.")
    return ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini", temperature=0)

def format_articles_to_markdown(articles: List[Article], intro_text: str) -> str:
    """Verilen makale listesini ön yüz için Markdown formatına dönüştürür."""
    if not articles:
        return "Bu konuda veritabanımda bir bilgi bulamadım."

    formatted_parts = []
    for i, article in enumerate(articles, 1):
        summary_text = article.summary.strip() if article.summary else "Bu haber için özet mevcut değil."
        formatted_parts.append(
            f"{i}. **{article.title.strip()}**\n"
            f"   - **Kaynak:** {article.source.strip()}\n"
            f"   - **Yayın Tarihi:** {article.publish_date.strftime('%Y-%m-%d')}\n"
            f"   - **Özet:** {summary_text}\n"
            f"   - **Link:** [Haber Linki]({article.url.strip()})"
        )
    
    return f"{intro_text}\n\n" + "\n\n".join(formatted_parts)

async def run_chat_logic(query: str, user_id: str):
    llm = get_llm()
    tools = [db_tools.get_recent_news, db_tools.search_news_by_topic]
    
    # Adım 1: Ajanın sadece "plan" yapmasını sağla
    llm_with_tools = llm.bind_tools(tools)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Sen, kullanıcının isteğine göre doğru aracı ve parametreleri seçen bir yönlendiricisin."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])
    chain = prompt | llm_with_tools

    db: Session = next(database.get_db())
    try:
        history = chat_history_crud.get_chat_history_by_user(db, user_id=user_id)
        chat_history = [
            AIMessage(content=rec.response) if i % 2 else HumanMessage(content=rec.query)
            for i, rec in enumerate(reversed(history))
        ]
        
        # Planı al
        ai_msg_with_plan = await chain.ainvoke({"input": query, "chat_history": chat_history})
        
        tool_calls = ai_msg_with_plan.tool_calls
        if not tool_calls:
            # Eğer bir plan yoksa, genel bir cevap ver
            return "Size nasıl yardımcı olabilirim? 'Son 3 gün' veya 'Yapay zeka' gibi konularla ilgili haberleri arayabilirim."

        # Adım 2: Planı manuel olarak uygula
        tool_name = tool_calls[0]['name']
        tool_args = tool_calls[0]['args']
        
        response_text = ""
        if tool_name == "get_recent_news":
            days_ago = tool_args.get('days_ago', 7)
            articles = await db_tools.get_recent_news.ainvoke(tool_args)
            intro = f"Son {days_ago} gün içinde öne çıkan haberler şunlardır:"
            response_text = format_articles_to_markdown(articles, intro)
        
        elif tool_name == "search_news_by_topic":
            topic = tool_args.get('topic', '')
            articles = await db_tools.search_news_by_topic.ainvoke(tool_args)
            intro = f"'{topic.capitalize()}' konusu ile ilgili bulunan haberler şunlardır:"
            response_text = format_articles_to_markdown(articles, intro)
        else:
            response_text = "Üzgünüm, isteğinizi anlayamadım."

        chat_history_crud.create_chat_history(db, history=schemas.ChatHistoryCreate(
            user_id=user_id,
            query=query,
            response=response_text
        ))
        
        return response_text

    except Exception as e:
        logger.error(f"Chat logic hatası (kullanıcı: {user_id}): {e}", exc_info=True)
        return "Üzgünüm, isteğinizi işlerken bir hata oluştu. Lütfen daha sonra tekrar deneyin."
    finally:
        db.close()

