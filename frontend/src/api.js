import axios from 'axios';

// 创建 axios 实例，配置基础 URL
const apiClient = axios.create({
  baseURL: 'http://192.168.31.129:5001/api',  // 你的后端地址
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

// 你可以在这里添加拦截器（比如统一错误处理）
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API 请求错误:', error);
    return Promise.reject(error);
  }
);

export const api = {
  async get(url) {
    return apiClient.get(url);
  },
  async post(url, data) {
    return apiClient.post(url, data);
  },
  async put(url, data) {
    return apiClient.put(url, data);
  },
  async delete(url) {
    return apiClient.delete(url);
  }
};

export default api;