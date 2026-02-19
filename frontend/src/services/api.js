import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const authStorage = localStorage.getItem('auth-storage');
  if (authStorage) {
    try {
      const parsed = JSON.parse(authStorage);
      console.log('Auth storage:', parsed); // Debug log
      
      // Zustand persist stores it as { state: { token, user, isAuthenticated } }
      const token = parsed.state?.token || parsed.token;
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('Token added to request:', token.substring(0, 20) + '...'); // Debug log
      } else {
        console.warn('No token found in auth storage');
      }
    } catch (error) {
      console.error('Error parsing auth token:', error);
    }
  } else {
    console.warn('No auth-storage in localStorage');
  }
  return config;
});

// Log response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('Authentication failed:', error.response.data);
      // Optionally clear storage and redirect to login
      localStorage.removeItem('auth-storage');
    }
    return Promise.reject(error);
  }
);

// GitHub OAuth
export const githubAuth = {
  getAuthUrl: () => {
    const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID;
    const redirectUri = import.meta.env.VITE_GITHUB_REDIRECT_URI || `${window.location.origin}/auth/callback`;
    const scope = 'repo,user';
    return `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
  },
  
  handleCallback: async (code) => {
    const response = await api.post('/auth/github/callback', { code });
    return response.data;
  },
  
  getUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Agent Operations
export const agentAPI = {
  getRepos: async () => {
    const response = await api.get('/repos');
    return response.data;
  },
  
  runAgent: async (data) => {
    const response = await api.post('/run-agent', data);
    return response.data;
  },
  
  runAgentAsync: async (data) => {
    const response = await api.post('/run-agent-async', data);
    return response.data;
  },
  
  getRuns: async () => {
    const response = await api.get('/runs');
    return response.data;
  },
  
  getRun: async (id) => {
    const response = await api.get(`/runs/${id}`);
    return response.data;
  },
  
  health: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
