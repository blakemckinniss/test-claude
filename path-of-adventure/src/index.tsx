import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Strict mode for development
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)