import { useState, useEffect } from 'react'
import axios from 'axios'

function Dashboard({ apiUrl, token }) {
  const [projects, setProjects] = useState([])
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [projectsRes, docsRes] = await Promise.all([
        axios.get(`${apiUrl}/projects`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${apiUrl}/documents`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ])

      setProjects(projectsRes.data)
      setDocuments(docsRes.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div>
      <h2>Dashboard</h2>

      <div className="card">
        <h3>Quick Stats</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div style={{ padding: '1rem', backgroundColor: '#2a2a2a', borderRadius: '8px' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#646cff' }}>{projects.length}</div>
            <div style={{ color: '#888' }}>Projects</div>
          </div>
          <div style={{ padding: '1rem', backgroundColor: '#2a2a2a', borderRadius: '8px' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#51cf66' }}>{documents.length}</div>
            <div style={{ color: '#888' }}>Documents</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Recent Projects</h3>
        {projects.length === 0 ? (
          <p style={{ color: '#888' }}>No projects yet</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {projects.slice(0, 5).map(project => (
                <tr key={project.id}>
                  <td>{project.name}</td>
                  <td><span className="badge badge-user">{project.type}</span></td>
                  <td>{new Date(project.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h3>Recent Documents</h3>
        {documents.length === 0 ? (
          <p style={{ color: '#888' }}>No documents yet</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Filename/URL</th>
                <th>Type</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {documents.slice(0, 5).map(doc => (
                <tr key={doc.id}>
                  <td>{doc.filename || doc.url || 'Text Document'}</td>
                  <td><span className="badge badge-user">{doc.type}</span></td>
                  <td>{new Date(doc.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default Dashboard
