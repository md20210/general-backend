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

  if (loading) return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h2 style={{ color: '#1a1a1a' }}>Loading Dashboard...</h2>
      <p style={{ color: '#666', marginTop: '1rem' }}>Please wait while we fetch your data.</p>
    </div>
  )

  if (error) return (
    <div className="error">
      <h3 style={{ marginBottom: '0.5rem' }}>Error Loading Dashboard</h3>
      <p>{error}</p>
      <button onClick={fetchData} style={{ marginTop: '1rem' }}>Retry</button>
    </div>
  )

  return (
    <div>
      <h2 style={{ color: '#1a1a1a', marginBottom: '1.5rem' }}>Dashboard</h2>

      <div className="card">
        <h3 style={{ color: '#1a1a1a', marginBottom: '1rem' }}>Quick Stats</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div style={{ padding: '1.5rem', backgroundColor: '#f5f5f5', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#1a1a1a' }}>{projects.length}</div>
            <div style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.5rem' }}>Projects</div>
          </div>
          <div style={{ padding: '1.5rem', backgroundColor: '#f5f5f5', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#1a1a1a' }}>{documents.length}</div>
            <div style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.5rem' }}>Documents</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 style={{ color: '#1a1a1a', marginBottom: '1rem' }}>Recent Projects</h3>
        {projects.length === 0 ? (
          <p style={{ color: '#666', marginTop: '1rem' }}>No projects yet. Create your first project to get started.</p>
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
        <h3 style={{ color: '#1a1a1a', marginBottom: '1rem' }}>Recent Documents</h3>
        {documents.length === 0 ? (
          <p style={{ color: '#666', marginTop: '1rem' }}>No documents yet. Upload your first document to see it here.</p>
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
