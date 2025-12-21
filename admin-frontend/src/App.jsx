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
      <header style={{ marginBottom: '2rem', borderBottom: '1px solid #333', paddingBottom: '1rem' }}>
        <h1>General Backend - Admin Panel</h1>
        {currentUser && (
          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>
              Logged in as: <strong>{currentUser.email}</strong>
              {currentUser.is_admin && <span className="badge badge-admin" style={{ marginLeft: '0.5rem' }}>Admin</span>}
            </span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        )}
      </header>

      <nav style={{ marginBottom: '2rem' }}>
        <button
          onClick={() => setCurrentView('dashboard')}
          style={{ marginRight: '0.5rem', backgroundColor: currentView === 'dashboard' ? '#646cff' : '#1a1a1a' }}
        >
          Dashboard
        </button>
        {currentUser?.is_admin && (
          <>
            <button
              onClick={() => setCurrentView('users')}
              style={{ marginRight: '0.5rem', backgroundColor: currentView === 'users' ? '#646cff' : '#1a1a1a' }}
            >
              Users
            </button>
            <button
              onClick={() => setCurrentView('llm')}
              style={{ marginRight: '0.5rem', backgroundColor: currentView === 'llm' ? '#646cff' : '#1a1a1a' }}
            >
              LLM Config
            </button>
            <button
              onClick={() => setCurrentView('stats')}
              style={{ backgroundColor: currentView === 'stats' ? '#646cff' : '#1a1a1a' }}
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
