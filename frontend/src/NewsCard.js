import React from 'react';
import './NewsCard.css';

const NewsCard = ({ article }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Tarih Bilgisi Yok';
    try {
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateString).toLocaleDateString('tr-TR', options);
    } catch (error) {
      return dateString;
    }
  };

  return (
    <div className="news-card">
      <div className="news-card-content">
        <h3 className="news-card-title">
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            {article.title}
          </a>
        </h3>
        <p className="news-card-summary">{article.summary}</p>
        <div className="news-card-footer">
          <span className="news-card-source">{article.source || 'Kaynak Yok'}</span>
          <span className="news-card-date">{formatDate(article.publish_date)}</span>
        </div>
      </div>
    </div>
  );
};

export default NewsCard;

