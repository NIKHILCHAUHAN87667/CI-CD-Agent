import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { debugAuth } from './utils/debug.js'

// Make debug tools available in console
if (import.meta.env.DEV) {
  window.debugAuth = debugAuth;
  console.log('🔧 Debug tools available: window.debugAuth');
  console.log('  - debugAuth.checkStorage() - Check localStorage');
  console.log('  - debugAuth.testToken() - Test token validity');
  console.log('  - debugAuth.testRepos() - Test repos endpoint');
  console.log('  - debugAuth.testDebug() - Test if backend receives token');
  console.log('  - debugAuth.clearStorage() - Clear auth storage');
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
