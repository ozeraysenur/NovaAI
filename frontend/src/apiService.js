// src/apiService.js
const API_BASE_URL = 'http://localhost:8000/api/v1'; // Backend API base URL'i

class ApiService {
  async makeRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Chat endpoint'i için
  async sendMessage(userId, query) {
    return this.makeRequest('/chat', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        query: query // 'message' -> 'query' olarak düzeltildi
      })
    });
  }

  // News ingestion (admin/test kullanımı için)
  async ingestNews() {
    return this.makeRequest('/ingest-news', {
      method: 'POST'
    });
  }
}

export default new ApiService();