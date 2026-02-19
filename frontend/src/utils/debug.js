/**
 * Debug utilities for testing authentication
 * Open browser console and use: window.debugAuth.testToken()
 */

export const debugAuth = {
  // Check what's in localStorage
  checkStorage: () => {
    const authStorage = localStorage.getItem('auth-storage');
    console.log('=== Auth Storage Debug ===');
    console.log('Raw storage:', authStorage);
    
    if (authStorage) {
      try {
        const parsed = JSON.parse(authStorage);
        console.log('Parsed storage:', parsed);
        console.log('Token:', parsed.state?.token || parsed.token);
        console.log('User:', parsed.state?.user || parsed.user);
      } catch (e) {
        console.error('Failed to parse:', e);
      }
    } else {
      console.log('No auth-storage found');
    }
  },
  
  // Test token with API call
  testToken: async () => {
    const authStorage = localStorage.getItem('auth-storage');
    if (!authStorage) {
      console.error('No auth storage found. Please login first.');
      return;
    }
    
    try {
      const parsed = JSON.parse(authStorage);
      const token = parsed.state?.token || parsed.token;
      
      console.log('Testing token:', token?.substring(0, 20) + '...');
      
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      console.log('API Response:', response.status, data);
      
      if (response.ok) {
        console.log('✅ Token is valid!');
      } else {
        console.error('❌ Token validation failed');
      }
      
      return data;
    } catch (e) {
      console.error('Test failed:', e);
    }
  },
  
  // Test repos endpoint
  testRepos: async () => {
    const authStorage = localStorage.getItem('auth-storage');
    if (!authStorage) {
      console.error('No auth storage found. Please login first.');
      return;
    }
    
    try {
      const parsed = JSON.parse(authStorage);
      const token = parsed.state?.token || parsed.token;
      
      console.log('Fetching repos with token:', token?.substring(0, 20) + '...');
      
      const response = await fetch('http://localhost:8000/repos', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      console.log('Repos Response:', response.status, data);
      
      return data;
    } catch (e) {
      console.error('Test failed:', e);
    }
  },
  
  // Test debug endpoint
  testDebug: async () => {
    const authStorage = localStorage.getItem('auth-storage');
    const token = authStorage ? JSON.parse(authStorage).state?.token || JSON.parse(authStorage).token : null;
    
    console.log('Testing debug endpoint with token:', token?.substring(0, 20) + '...');
    
    try {
      const response = await fetch('http://localhost:8000/debug/token', {
        headers: {
          'Authorization': token ? `Bearer ${token}` : 'None',
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      console.log('Debug Response:', response.status, data);
      
      return data;
    } catch (e) {
      console.error('Test failed:', e);
    }
  },
  
  // Clear storage
  clearStorage: () => {
    localStorage.removeItem('auth-storage');
    console.log('✅ Auth storage cleared');
  }
};

// Make it available globally in development
if (typeof window !== 'undefined') {
  window.debugAuth = debugAuth;
}
