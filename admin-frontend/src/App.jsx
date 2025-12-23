import { useState, useEffect } from 'react'
import axios from 'axios'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import UserManagement from './components/UserManagement'
import LLMConfig from './components/LLMConfig'
import SystemStats from './components/SystemStats'

// API Base URL - change to your Railway URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [currentUser, setCurrentUser] = useState(null)
  const [currentView, setCurrentView] = useState('dashboard')
  const [error, setError] = useState('')

  useEffect(() => {
    if (token) {
      fetchCurrentUser()
    }
  }, [token])

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setCurrentUser(response.data)
    } catch (err) {
      console.error('Failed to fetch current user:', err)
      handleLogout()
    }
  }

  const handleLogin = (newToken) => {
    setToken(newToken)
    localStorage.setItem('token', newToken)
  }

  const handleLogout = () => {
    setToken(null)
    setCurrentUser(null)
    localStorage.removeItem('token')
    setCurrentView('dashboard')
  }

  if (!token) {
    return <Login onLogin={handleLogin} apiUrl={API_URL} />
  }

  return (
    <div className="container">
      <header style={{ marginBottom: '2rem', borderBottom: '2px solid #e0e0e0', paddingBottom: '1rem' }}>
        <h1 style={{ color: '#1a1a1a', marginBottom: '0.5rem' }}>General Backend - Admin Panel</h1>
        {currentUser && (
          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: '#666' }}>
              Logged in as: <strong style={{ color: '#1a1a1a' }}>{currentUser.email}</strong>
              {currentUser.is_admin && <span className="badge badge-admin" style={{ marginLeft: '0.5rem' }}>Admin</span>}
            </span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        )}
      </header>

      <nav style={{ marginBottom: '2rem', display: 'flex', gap: '0.5rem' }}>
        <button
          onClick={() => setCurrentView('dashboard')}
          style={{
            backgroundColor: currentView === 'dashboard' ? '#1a1a1a' : '#f5f5f5',
            color: currentView === 'dashboard' ? '#ffffff' : '#1a1a1a',
            border: '1px solid #e0e0e0'
          }}
        >
          Dashboard
        </button>
        {currentUser?.is_admin && (
          <>
            <button
              onClick={() => setCurrentView('users')}
              style={{
                backgroundColor: currentView === 'users' ? '#1a1a1a' : '#f5f5f5',
                color: currentView === 'users' ? '#ffffff' : '#1a1a1a',
                border: '1px solid #e0e0e0'
              }}
            >
              Users
            </button>
            <button
              onClick={() => setCurrentView('llm')}
              style={{
                backgroundColor: currentView === 'llm' ? '#1a1a1a' : '#f5f5f5',
                color: currentView === 'llm' ? '#ffffff' : '#1a1a1a',
                border: '1px solid #e0e0e0'
              }}
            >
              LLM Config
            </button>
            <button
              onClick={() => setCurrentView('stats')}
              style={{
                backgroundColor: currentView === 'stats' ? '#1a1a1a' : '#f5f5f5',
                color: currentView === 'stats' ? '#ffffff' : '#1a1a1a',
                border: '1px solid #e0e0e0'
              }}
            >
              System Stats
            </button>
          </>
        )}
      </nav>

      {error && <div className="error">{error}</div>}

      <main>
        {currentView === 'dashboard' && <Dashboard apiUrl={API_URL} token={token} />}
        {currentView === 'users' && currentUser?.is_admin && (
          <UserManagement apiUrl={API_URL} token={token} />
        )}
        {currentView === 'llm' && currentUser?.is_admin && (
          <LLMConfig apiUrl={API_URL} token={token} />
        )}
        {currentView === 'stats' && currentUser?.is_admin && (
          <SystemStats apiUrl={API_URL} token={token} />
        )}
      </main>
    </div>
  )
}

export default App
