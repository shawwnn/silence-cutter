import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const DEFAULT_DURATION = 2
const DEFAULT_NOISE = -60

async function sendFile(path, file, fields = {}) {
  const body = new FormData()
  body.append('file', file)
  Object.entries(fields).forEach(([key, value]) => body.append(key, value))
  const response = await fetch(path, { method: 'POST', body })
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || 'Bridge request failed')
  return data
}

function App() {
  const [file, setFile] = useState(null)
  const [metadata, setMetadata] = useState(null)
  const [duration, setDuration] = useState(DEFAULT_DURATION)
  const [noiseDb, setNoiseDb] = useState(DEFAULT_NOISE)
  const [status, setStatus] = useState('Select a video to begin.')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState(null)

  useEffect(() => {
    if (!jobId) return undefined
    const timer = setInterval(async () => {
      try {
        const response = await fetch(`/api/jobs/${jobId}`)
        const job = await response.json()
        if (!response.ok) throw new Error(job.error || 'Unable to read job status')
        setStatus(job.message || job.state)
        if (job.state === 'completed') {
          setLoading(false)
          setJobId(null)
          setStatus(`Completed. Output: ${job.output_path}`)
        } else if (job.state === 'failed' || job.state === 'cancelled') {
          setLoading(false)
          setJobId(null)
          if (job.error) setError(job.error)
        }
      } catch (err) {
        setLoading(false)
        setJobId(null)
        setError(err.message)
      }
    }, 500)
    return () => clearInterval(timer)
  }, [jobId])

  async function chooseFile(event) {
    const nextFile = event.target.files?.[0]
    if (!nextFile) return
    setFile(nextFile)
    setMetadata(null)
    setError('')
    setStatus('Reading video details…')
    try {
      const details = await sendFile('/api/metadata', nextFile)
      setMetadata(details)
      setStatus('Ready to remove silence.')
    } catch (err) {
      setError(err.message)
      setStatus('Unable to read this file.')
    }
  }

  async function start() {
    if (!file) return
    setLoading(true)
    setError('')
    setStatus('Processing…')
    try {
      const job = await sendFile('/api/jobs', file, {
        silence_duration: duration,
        noise_db: noiseDb,
      })
      setJobId(job.job_id)
      setStatus('Processing…')
    } catch (err) {
      setError(err.message)
      setStatus('Processing could not start.')
    }
  }

  async function cancel() {
    if (!jobId) return
    await fetch(`/api/jobs/${jobId}/cancel`, { method: 'POST' })
    setLoading(false)
    setJobId(null)
    setStatus('Processing cancelled.')
  }

  return (
    <main className="shell">
      <p className="eyebrow">Powered by FFmpeg · runs locally</p>
      <h1>Silence Cutter</h1>
      <p className="intro">Remove long silent sections from a video while keeping the original file untouched.</p>

      <section className="card">
        <label className="dropzone">
          <span>{file ? file.name : 'Choose a video file'}</span>
          <small>FFmpeg-supported video inputs are checked by FFprobe.</small>
          <input type="file" onChange={chooseFile} />
        </label>

        {metadata && <div className="metadata">{metadata.format || 'Video'} · {metadata.size_bytes} bytes · {metadata.duration_seconds?.toFixed(1) || '—'} seconds</div>}

        <div className="controls">
          <label>Silence duration: <output>{duration}s</output>
            <input type="range" min="0.1" max="60" step="0.1" value={duration} onChange={(e) => setDuration(e.target.value)} disabled={loading} />
          </label>
          <label>Silence threshold: <output>{noiseDb} dB</output>
            <input type="range" min="-100" max="0" step="1" value={noiseDb} onChange={(e) => setNoiseDb(e.target.value)} disabled={loading} />
          </label>
        </div>

        <button onClick={loading ? cancel : start} disabled={!metadata}>{loading ? 'Cancel processing' : 'Remove silence'}</button>
        <p className="status" role="status">{status}</p>
        {error && <p className="error" role="alert">{error}</p>}
      </section>
    </main>
  )
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>)
