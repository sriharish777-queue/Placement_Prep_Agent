import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3500,
          style: {
            background: '#1e1b4b',
            color: '#e0e7ff',
            borderRadius: '10px',
            border: '1px solid rgba(124,90,242,.3)',
            fontSize: '14px',
          },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>,
)
