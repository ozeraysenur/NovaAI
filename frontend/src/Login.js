import React, { useState } from 'react';
import './Login.css';
import novalogo from "./assets/nova logo.png";
import googleLogo from "./assets/google-logo-9808.png";
import githubLogo from "./assets/github-seeklogo.png";

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'E-posta adresi gerekli';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Geçerli bir e-posta adresi girin';
    }
    
    if (!formData.password) {
      newErrors.password = 'Şifre gerekli';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Şifre en az 6 karakter olmalı';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    
    try {
      // Simulated login delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // For demo purposes, accept any valid email/password
      if (formData.email && formData.password.length >= 6) {
        const userData = {
          email: formData.email,
          name: formData.email.split('@')[0],
          avatar: `https://ui-avatars.com/api/?name=${formData.email}&background=8a2be2&color=fff`,
          loginTime: Date.now()
        };

        // Save user data to localStorage if "Remember Me" is checked
        if (formData.rememberMe) {
          localStorage.setItem('cosmicUser', JSON.stringify(userData));
        }
        
        onLogin(userData);
      } else {
        setErrors({ general: 'Giriş bilgileri hatalı' });
      }
    } catch (error) {
      setErrors({ general: 'Giriş sırasında bir hata oluştu' });
    } finally {
      setLoading(false);
    }
  };

  const handleSocialLogin = (provider) => {
    setLoading(true);
    setTimeout(() => {
      const userData = {
        email: `user@${provider}.com`,
        name: `${provider} User`,
        avatar: `https://ui-avatars.com/api/?name=${provider}&background=8a2be2&color=fff`,
        loginTime: Date.now()
      };
      onLogin(userData);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="loginPage">
      {/* Background with cosmic effects */}
      <div className="loginBackground"></div>
      
      {/* Main content */}
      <div className="loginMainContent">
        {/* Welcome section */}
        <div className="loginWelcomeSection">
          <div className="loginBrand">
            <img src={novalogo} alt="Nova AI" className="loginBrandLogo" />
            <h1 className="loginBrandTitle">Nova AI</h1>
          </div>
          <div className="loginWelcomeText">
            <h2 className="welcomeTitle">Yapay Zeka Dünyasına Hoş Geldiniz</h2>
            <h3 className="welcomeSubtitle">Anlık Haber ve Analiz Deneyimi</h3>
            <p className="welcomeDescription">
              Yapay zeka ve teknoloji dünyasındaki en son gelişmeleri anında öğrenin. 
              Nova AI, en güncel haberleri sizin için analiz eder ve özetler.
            </p>
          </div>
        </div>

        {/* Login form section */}
        <div className="loginFormSection">
          <div className="loginContainer">
            <div className="loginHeader">
              <h2 className="loginTitle">Giriş Yap</h2>
              <p className="loginSubtitle">Bilgi akışına yeniden bağlanın</p>
            </div>
            
            <form className="loginForm" onSubmit={handleSubmit}>
              {errors.general && (
                <div className="loginError">
                  {errors.general}
                </div>
              )}
              
              <div className="loginInputGroup">
                <input 
                  type="email" 
                  name="email"
                  className={`loginInput ${errors.email ? 'error' : ''}`}
                  placeholder="E-posta adresiniz"
                  value={formData.email}
                  onChange={handleInputChange}
                  disabled={loading}
                />
                {errors.email && <span className="loginErrorText">{errors.email}</span>}
              </div>
              
              <div className="loginInputGroup">
                <input 
                  type="password" 
                  name="password"
                  className={`loginInput ${errors.password ? 'error' : ''}`}
                  placeholder="Şifreniz"
                  value={formData.password}
                  onChange={handleInputChange}
                  disabled={loading}
                />
                {errors.password && <span className="loginErrorText">{errors.password}</span>}
              </div>
              
              <div className="loginOptions">
                <label className="loginRemember">
                  <input 
                    type="checkbox" 
                    name="rememberMe"
                    className="loginCheckbox"
                    checked={formData.rememberMe}
                    onChange={handleInputChange}
                    disabled={loading}
                  />
                  <span>Beni hatırla</span>
                </label>
                <button type="button" className="loginForgot">Şifremi unuttum</button>
              </div>
              
              <button 
                type="submit" 
                className={`loginButton ${loading ? 'loading' : ''}`}
                disabled={loading}
              >
                {loading ? '' : 'Giriş Yap'}
              </button>
            </form>
            
            <div className="loginDivider">
              <span className="loginDividerText">veya</span>
            </div>
            
            <div className="loginSocial">
              <button 
                type="button"
                className="socialButton" 
                onClick={() => handleSocialLogin('google')}
                disabled={loading}
              >
                <img src={googleLogo} alt="Google" className="socialLogo" />
                Google ile Giriş
              </button>
              <button 
                type="button"
                className="socialButton" 
                onClick={() => handleSocialLogin('github')}
                disabled={loading}
              >
                <img src={githubLogo} alt="GitHub" className="socialLogo" />
                GitHub ile Giriş
              </button>
            </div>
            
            <div className="loginFooter">
              Hesabınız yok mu?
              <button type="button" className="loginSignup">Kayıt Ol</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;