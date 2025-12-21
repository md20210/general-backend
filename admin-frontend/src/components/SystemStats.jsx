import { useState, useEffect } from 'react'
import axios from 'axios'

function SystemStats({ apiUrl, token }) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${apiUrl}/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setStats(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load stats')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading system stats...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div>
      <h2>System Statistics</h2>

      <div className="card">
        <h3>User Statistics</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div style={{ padding: '1.5rem', backgroundColor: '#2a2a2a', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', fontWeight: 'bold', color: '#646cff' }}>
              {stats.total_users}
            </div>
            <div style={{ color: '#888', marginTop: '0.5rem' }}>Total Users</div>
          </div>

          <div style={{ padding: '1.5rem', backgroundColor: '#2a2a2a', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', fontWeight: 'bold', color: '#51cf66' }}>
              {stats.admin_users}
            </div>
            <div style={{ color: '#888', marginTop: '0.5rem' }}>Admins</div>
          </div>

          <div style={{ padding: '1.5rem', backgroundColor: '#2a2a2a', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', fontWeight: 'bold', color: '#ffd43b' }}>
              {stats.regular_users}
            </div>
            <div style={{ color: '#888', marginTop: '0.5rem' }}>Regular Users</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>System Information</h3>
        <table className="table">
          <tbody>
            <tr>
              <td><strong>Backend Version</strong></td>
              <td>1.0.0</td>
            </tr>
            <tr>
              <td><strong>API URL</strong></td>
              <td><code>{apiUrl}</code></td>
            </tr>
            <tr>
              <td><strong>Status</strong></td>
              <td><span style={{ color: '#51cf66' }}>✓ Healthy</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Quick Actions</h3>
        <button
          onClick={fetchStats}
          style={{ marginRight: '0.5rem' }}
        >
          Refresh Stats
        </button>
        <button
          onClick={() => window.open(`${apiUrl}/docs`, '_blank')}
        >
          API Documentation
        </button>
      </div>
    </div>
  )
}

export default SystemStats
