import { useState, useEffect } from 'react'
import axios from 'axios'

function UserManagement({ apiUrl, token }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${apiUrl}/admin/users`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUsers(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteUser = async (userId, userEmail) => {
    if (!confirm(`Are you sure you want to delete user ${userEmail}?`)) {
      return
    }

    try {
      await axios.delete(`${apiUrl}/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setSuccess(`User ${userEmail} deleted successfully`)
      fetchUsers()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete user')
    }
  }

  if (loading) return <div>Loading users...</div>

  return (
    <div>
      <h2>User Management</h2>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="card">
        <h3>All Users ({users.length})</h3>

        {users.length === 0 ? (
          <p style={{ color: '#888' }}>No users found</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id}>
                  <td>{user.email}</td>
                  <td>
                    {user.is_admin ? (
                      <span className="badge badge-admin">Admin</span>
                    ) : (
                      <span className="badge badge-user">User</span>
                    )}
                  </td>
                  <td>
                    {user.is_active ? (
                      <span style={{ color: '#51cf66' }}>Active</span>
                    ) : (
                      <span style={{ color: '#ff6b6b' }}>Inactive</span>
                    )}
                  </td>
                  <td>{new Date(user.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      onClick={() => handleDeleteUser(user.id, user.email)}
                      style={{
                        padding: '0.4rem 0.8rem',
                        fontSize: '0.875rem',
                        backgroundColor: '#ff6b6b',
                        color: 'white',
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default UserManagement
