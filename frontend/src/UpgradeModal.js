import React from 'react';
import './UpgradeModal.css';
import novalogo from "./assets/nova logo.png"; // Logoyu kullanmak için

const UpgradeModal = ({ onClose }) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-button" onClick={onClose}>×</button>
        
        <div className="modal-header">
          <img src={novalogo} alt="Nova AI Pro" className="modal-logo" />
          <h2>Nova AI Pro'ya Yükseltin</h2>
          <p>Yapay zeka destekli haber deneyiminizi bir üst seviyeye taşıyın.</p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <h3>Daha Detaylı Özetler</h3>
            <p>Standart özetlerin ötesine geçin. Pro ile her haberin en kritik detaylarını içeren, derinlemesine analizler ve çok paragraflı özetler alın.</p>
          </div>
          <div className="feature-card">
            <h3>Genişletilmiş Kaynak Erişimi</h3>
            <p>Daha fazla teknoloji sitesi, araştırma makalesi ve özel bültenlerden oluşan genişletilmiş bir veri havuzundan en güncel haberlere anında erişin.</p>
          </div>
          <div className="feature-card">
            <h3>Sesli Özetler (Çok Yakında)</h3>
            <p>Yoldayken veya başka bir işle meşgulken bile haberleri takip edin. Pro kullanıcıları, makale özetlerini yüksek kaliteli seslendirme ile dinleyebilecek.</p>
          </div>
          <div className="feature-card">
            <h3>Öncelikli Erişim</h3>
            <p>En yeni özelliklere ve beta sürümlerine herkesten önce siz erişin. Nova AI'nin geleceğini şekillendirmemize yardımcı olun.</p>
          </div>
        </div>

        <div className="modal-footer">
          <p>Bu özellikler şu anda geliştirme aşamasındadır.</p>
          <button className="upgrade-button-soon" disabled>Çok Yakında</button>
        </div>
      </div>
    </div>
  );
};

export default UpgradeModal;
