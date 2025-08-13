import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';
import Login from './Login';
import apiService from './apiService';
import NewsCard from './NewsCard'; // Yeni bileşeni import et
import UpgradeModal from './UpgradeModal'; // Modal bileşenini import et
import novalogo from "./assets/nova logo.png";
import addBtn from "./assets/add-30.png";
import msgIcon from "./assets/message.svg";
import loginIcon from "./assets/home.svg";
import saveBtn from "./assets/bookmark.svg";
import rocket from "./assets/rocket.svg";
import sendBtn from "./assets/send.svg";
import userImg from "./assets/user-icon.png";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [chats, setChats] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false); // Modal state'i
  
  const chatEndRef = useRef(null);

  useEffect(() => {
    const checkSavedUser = () => {
      const savedUser = localStorage.getItem('cosmicUser');
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          const thirtyDaysMs = 30 * 24 * 60 * 60 * 1000;
          if (Date.now() - userData.loginTime < thirtyDaysMs) {
            setUser(userData);
            setIsLoggedIn(true);
          } else {
            localStorage.removeItem('cosmicUser');
          }
        } catch (error) {
          localStorage.removeItem('cosmicUser');
        }
      }
      setLoading(false);
    };

    setTimeout(checkSavedUser, 1000);
  }, []);
  
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chats, isTyping]);


  const handleLogin = (userData) => {
    setUser(userData);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUser(null);
    setChats([]);
    localStorage.removeItem('cosmicUser');
  };

  const handleSendMessage = async (query) => {
    if (!query.trim()) return;

    const newUserMessage = {
      id: Date.now(),
      sender: 'user',
      text: query,
      avatar: user?.avatar || userImg
    };

    setChats(prev => [...prev, newUserMessage]);
    setMessage('');
    setIsTyping(true);

    try {
      const response = await apiService.sendMessage(
        user.id || user.email || 'anonymous', 
        query
      );
      
      console.log("Backend'den gelen ham yanıt:", response.response); // Hata ayıklama için eklendi

      const aiResponse = {
        id: Date.now() + 1,
        sender: 'ai',
        text: response.response, // Backend'den gelen yanıt
        avatar: novalogo,
      };
      
      setChats(prev => [...prev, aiResponse]);
      
    } catch (error) {
      console.error('Chat API error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'ai',
        text: `Üzgünüm, bir hata oluştu: ${error.message}. Lütfen daha sonra tekrar deneyin.`,
        avatar: novalogo
      };
      setChats(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    handleSendMessage(message);
  };
  
  const handleQueryClick = (queryText) => {
    handleSendMessage(queryText);
  };

  const handleNewChat = () => {
    setChats([]);
  };

  const renderMessageContent = (chat) => {
    const text = chat.text || '';

    // Gelen metin bir haber listesi içeriyor mu diye kontrol et (örneğin, "1. **" ile başlıyor mu?)
    // Bu, daha esnek bir kontrol sağlar.
    const isArticleList = /\d+\.\s\*\*/.test(text);

    if (chat.sender === 'ai' && isArticleList) {
      const articles = parseMarkdownToArticles(text);
      if (articles.length > 0) {
        // Giriş metnini, ilk numaralı listeden önceki kısım olarak al.
        const introMatch = text.match(/([\s\S]*?)(?=\n\d+\.\s\*\*)/);
        const introText = introMatch ? introMatch[1].trim() : '';

        return (
          <>
            {introText && <p>{introText}</p>}
            <div className="news-grid">
              {articles.map(article => (
                <NewsCard key={article.url} article={article} />
              ))}
            </div>
          </>
        );
      }
    }

    // Haber listesi değilse veya ayrıştırma başarısız olursa, normal Markdown olarak işle.
    return (
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({node, ...props}) => <a {...props} target="_blank" rel="noopener noreferrer" className="markdown-link" />
        }}
      >
        {text}
      </ReactMarkdown>
    );
  };

  const parseMarkdownToArticles = (markdownText) => {
    try {
      const articles = [];
      // Her bir numaralı maddeyi ayır
      const articleBlocks = markdownText.split(/^\d+\.\s/m).filter(Boolean);

      articleBlocks.forEach(block => {
        // Regex'leri her bir alan için daha esnek hale getir
        const titleMatch = block.match(/\*\*(.*?)\*\*/);
        const urlMatch = block.match(/\[Haber Linki\]\((.*?)\)/);
        const sourceMatch = block.match(/\*\*Kaynak:\*\* (.*?)(?:\n|$)/);
        const dateMatch = block.match(/\*\*Yayın Tarihi:\*\* (.*?)(?:\n|$)/);
        const summaryMatch = block.match(/\*\*Özet:\*\* ([\s\S]*?)(?=\n   - \*\*Link:\*\*|$)/);

        if (titleMatch && urlMatch) {
          articles.push({
            title: titleMatch[1].trim(),
            url: urlMatch[1].trim(),
            source: sourceMatch ? sourceMatch[1].trim() : 'Kaynak Bilgisi Yok',
            publish_date: dateMatch ? dateMatch[1].trim() : 'Tarih Bilgisi Yok',
            // Özet varsa onu kullan, yoksa başlığı özet olarak ata
            summary: summaryMatch ? summaryMatch[1].trim() : titleMatch[1].trim(),
          });
        }
      });
      return articles;
    } catch (e) {
      console.error("Markdown parse hatası:", e);
      return [];
    }
  };

  if (loading) {
    return (
      <div className="loadingScreen">
        <div className="loadingContent">
          <img src={novalogo} alt="Nova AI" className="loadingLogo" />
          <h1 className="loadingTitle">Nova AI</h1>
          <div className="loadingSpinner"></div>
          <p className="loadingText">Cosmic sistemler başlatılıyor...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      <div className="sideBar">
        <div className="upperSide">
          <div className="upperSideLogo">
            <img src={novalogo} alt="Nova AI Logo" className="logo"/>
            <span className="brand">Nova AI</span>
          </div>
          <button className="midBtn" onClick={handleNewChat}>
            <img src={addBtn} alt="Add" className="addBtn" />
            New Chat
          </button>
          <div className="upperSideBottom">
            <button 
              className="query"
              onClick={() => handleQueryClick("Son 3 gündeki AI haberlerini özetle")}
            >
              <img src={msgIcon} alt="Message" />
              Son 3 gündeki haberler
            </button>
            <button 
              className="query"
              onClick={() => handleQueryClick("Son 7 gündeki AI haberlerini özetle")}
            >
              <img src={msgIcon} alt="Message" />
              Son 7 gündeki haberler
            </button>
             <button 
              className="query"
              onClick={() => handleQueryClick("GPT-5 ile ilgili haberleri getir")}
            >
              <img src={msgIcon} alt="Message" />
              GPT-5
            </button>
          </div>
        </div>
        <div className="lowerSide">
          <div className="listItems userProfile">
            <img src={user?.avatar || userImg} alt="User" className="listItemsimg userAvatar" />
            <div className="userInfo">
              <span className="userName">{user?.name || user?.email}</span>
              <span className="userStatus">Online</span>
            </div>
          </div>
          <div className="listItems">
            <img src={saveBtn} alt="Save" className="listItemsimg" />
            Kayıtlı Sohbetler
          </div>
          <div className="listItems" onClick={() => setShowUpgradeModal(true)}>
            <img src={rocket} alt="Upgrade" className="listItemsimg" />
            Pro'ya Yükselt
          </div>
          <div className="listItems logoutItem" onClick={handleLogout}>
            <img src={loginIcon} alt="Logout" className="listItemsimg" />
            Çıkış Yap
          </div>
        </div>
      </div>
      
      <div className="main">
        <div className="chats">
          {chats.length === 0 ? (
            <div className="welcomeMessage">
              <img src={novalogo} alt="Nova AI Logo" className="welcomeLogo" />
              <h2>Nova AI'ye Hoş Geldiniz!</h2>
              <p>Merhaba <strong>{user?.name || user?.email}</strong>! AI ve teknoloji dünyasından en son haberleri öğrenmek için bir soru sorun.</p>
            </div>
          ) : (
            chats.map(chat => (
              <div key={chat.id} className={`chat ${chat.sender === 'ai' && 'ai-chat'}`}>
                <img className="chat-avatar" src={chat.avatar} alt={chat.sender} />
                <div className="txt">
                  {renderMessageContent(chat)}
                </div>
              </div>
            ))
          )}
          
          {isTyping && (
            <div className="chat ai-chat">
              <img className="chat-avatar" src={novalogo} alt="ai" />
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        <div className="chatFooter">
          <form onSubmit={handleFormSubmit} className="inp">
            <input 
              type="text" 
              placeholder="AI dünyasından bir soru sorun..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={isTyping}
            />
            <button 
              type="submit"
              className="send" 
              disabled={isTyping || !message.trim()}
            >
              <img src={sendBtn} alt="Send" />
            </button>
          </form>
        </div>
      </div>
      {showUpgradeModal && <UpgradeModal onClose={() => setShowUpgradeModal(false)} />}
    </div>
  );
}

export default App;
