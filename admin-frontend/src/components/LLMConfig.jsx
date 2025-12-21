import { useState, useEffect } from 'react'
import axios from 'axios'

function LLMConfig({ apiUrl, token }) {
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [testPrompt, setTestPrompt] = useState('Hello, how are you?')
  const [testProvider, setTestProvider] = useState('ollama')
  const [testModel, setTestModel] = useState('')
  const [testResult, setTestResult] = useState('')
  const [testLoading, setTestLoading] = useState(false)

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      const response = await axios.get(`${apiUrl}/llm/models`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setModels(response.data.models)
      if (response.data.models.length > 0) {
        setTestModel(response.data.models[0].name)
        setTestProvider(response.data.models[0].provider)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load models')
    } finally {
      setLoading(false)
    }
  }

  const handleTest = async (e) => {
    e.preventDefault()
    setTestLoading(true)
    setTestResult('')
    setError('')

    try {
      const response = await axios.post(
        `${apiUrl}/llm/generate`,
        {
          prompt: testPrompt,
          provider: testProvider,
          model: testModel,
          max_tokens: 500,
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )

      setTestResult(response.data.response)
    } catch (err) {
      setError(err.response?.data?.detail || 'Test failed')
    } finally {
      setTestLoading(false)
    }
  }

  if (loading) return <div>Loading LLM configuration...</div>

  return (
    <div>
      <h2>LLM Configuration</h2>

      {error && <div className="error">{error}</div>}

      <div className="card">
        <h3>Available Models ({models.length})</h3>
        {models.length === 0 ? (
          <p style={{ color: '#888' }}>No models available. Check your LLM providers configuration.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Provider</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {models.map((model, idx) => (
                <tr key={idx}>
                  <td><code>{model.name}</code></td>
                  <td>
                    <span className="badge badge-user">{model.provider}</span>
                  </td>
                  <td style={{ fontSize: '0.875rem', color: '#888' }}>{model.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h3>Test LLM</h3>
        <form onSubmit={handleTest}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Provider</label>
            <select
              value={testProvider}
              onChange={(e) => setTestProvider(e.target.value)}
              style={{ width: '100%' }}
            >
              <option value="ollama">Ollama (Local)</option>
              <option value="grok">GROK (X.AI)</option>
              <option value="anthropic">Anthropic Claude</option>
            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Model</label>
            <select
              value={testModel}
              onChange={(e) => setTestModel(e.target.value)}
              style={{ width: '100%' }}
            >
              {models
                .filter((m) => m.provider === testProvider)
                .map((model, idx) => (
                  <option key={idx} value={model.name}>
                    {model.name}
                  </option>
                ))}
            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Prompt</label>
            <textarea
              value={testPrompt}
              onChange={(e) => setTestPrompt(e.target.value)}
              rows={4}
              style={{ width: '100%', resize: 'vertical' }}
            />
          </div>

          <button type="submit" disabled={testLoading}>
            {testLoading ? 'Testing...' : 'Test LLM'}
          </button>
        </form>

        {testResult && (
          <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#2a2a2a', borderRadius: '8px' }}>
            <h4>Response:</h4>
            <pre style={{ whiteSpace: 'pre-wrap', marginTop: '0.5rem' }}>{testResult}</pre>
          </div>
        )}
      </div>
    </div>
  )
}

export default LLMConfig
