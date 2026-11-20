import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const DEFAULT_DURATION = 1
const DEFAULT_NOISE = -38

function formatBytes(bytes) {
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDuration(seconds) {
  if (!seconds) return '—'
  if (seconds < 60) return `${Math.round(seconds)} sec`
  return `${Math.floor(seconds / 60)} min ${Math.round(seconds % 60)} sec`
}

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
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState(null)

  useEffect(() => {
    if (!jobId) return undefined
    const timer = setInterval(async () => {
      try {
        const response = await fetch(`/api/jobs/${jobId}`)
        const job = await response.json()
        if (!response.ok) throw new Error(job.error || 'Unable to read job status')
        setStatus(job.message || job.state)
        setProgress(Number(job.progress || 0))
        if (job.state === 'completed') {
          setLoading(false)
          setJobId(null)
          setResult(job.result ? { ...job.result, job_id: job.job_id } : null)
          setStatus(`Completed. Output: ${job.output_path}`)
        } else if (job.state === 'needs_confirmation') {
          setLoading(false)
          setJobId(null)
          setResult(job.result || {})
          setStatus('No matching silence found. No output was created.')
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
    setResult(null)
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
    setProgress(0)
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
      setLoading(false)
    }
  }

  async function cancel() {
    if (!jobId) return
    await fetch(`/api/jobs/${jobId}/cancel`, { method: 'POST' })
    setLoading(false)
    setJobId(null)
    setStatus('Processing cancelled.')
    setProgress(0)
  }

  async function openOutputFolder() {
    if (!jobId && !result) return
    const completedJobId = jobId || result.job_id
    if (!completedJobId) return
    const response = await fetch(`/api/jobs/${completedJobId}/open-output-folder`, { method: 'POST' })
    const data = await response.json()
    if (!response.ok) setError(data.error || 'Unable to open output folder')
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

        {metadata && <div className="metadata">{metadata.format?.toUpperCase() || 'VIDEO'} · {formatBytes(metadata.size_bytes)} · {formatDuration(metadata.duration_seconds)}</div>}

        <div className="controls">
          <label>Silence duration: <output>{duration}s</output>
            <input type="range" min="0.1" max="60" step="0.1" value={duration} onChange={(e) => setDuration(e.target.value)} disabled={loading} />
          </label>
          <label>Silence threshold: <output>{noiseDb} dB</output>
            <input type="range" min="-100" max="0" step="1" value={noiseDb} onChange={(e) => setNoiseDb(e.target.value)} disabled={loading} />
          </label>
        </div>

        <button onClick={loading ? cancel : start} disabled={!metadata}>{loading ? 'Cancel processing' : 'Remove silence'}</button>
        {loading && <div className="progress-wrap" aria-label="Processing progress">
          <div className="progress-bar" style={{ width: `${Math.round(progress * 100)}%` }} />
          <small>{Math.round(progress * 100)}% · Longer videos may take more time.</small>
        </div>}
        <p className="status" role="status">{status}</p>
        {error && <p className="error" role="alert">{error}</p>}
        {result && <div className="result" role="status">
          <strong>{result.detected_silence_count ? 'Silence removed' : 'No matching silence found'}</strong>
          <p>Input: {formatDuration(result.input_duration_seconds)} · Output: {formatDuration(result.output_duration_seconds)}</p>
          <p>Detected: {result.detected_silence_count} interval(s) · Removed: {formatDuration(result.removed_duration_seconds)}</p>
          {!result.detected_silence_count && <>
            <p>No output was created. Try a shorter duration or a higher threshold, such as −45 dB.</p>
          </>}
          {result.output_path && <button className="secondary" onClick={openOutputFolder}>Open output folder</button>}
        </div>}
      </section>
    </main>
  )
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>)
