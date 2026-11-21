import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { cancelJob, getJob, openOutputFolder, sendVideo } from './api'
import { Logo, ProcessPanel, Settings, VideoStage, WorkflowSteps } from './components'
import './styles.css'
import './centered.css'

function App() {
  const [phase, setPhase] = useState('idle')
  const [file, setFile] = useState(null)
  const [metadata, setMetadata] = useState(null)
  const [duration, setDuration] = useState(1)
  const [noiseDb, setNoiseDb] = useState(-38)
  const [jobId, setJobId] = useState(null)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!jobId) return undefined
    const timer = setInterval(async () => {
      try {
        const job = await getJob(jobId)
        setProgress(Number(job.progress || 0))
        if (job.state === 'completed') {
          setJobId(null); setResult({ ...job.result, job_id: job.job_id }); setPhase('completed')
        } else if (job.state === 'timing_warning') {
          setJobId(null); setResult({ ...job.result, job_id: job.job_id }); setPhase('timing-warning')
        } else if (job.state === 'needs_confirmation') {
          setJobId(null); setResult(job.result); setPhase('no-silence')
        } else if (job.state === 'cancelled') {
          setJobId(null); setPhase('ready')
        } else if (job.state === 'failed') {
          setJobId(null); setError(job.error || 'Processing failed.'); setPhase('failed')
        }
      } catch (nextError) {
        setJobId(null); setError(nextError.message); setPhase('failed')
      }
    }, 500)
    return () => clearInterval(timer)
  }, [jobId])

  async function chooseFile(nextFile) {
    if (!nextFile || phase === 'processing') return
    setFile(nextFile); setMetadata(null); setResult(null); setError(''); setPhase('reading')
    try {
      const details = await sendVideo('/api/metadata', nextFile)
      setMetadata(details); setPhase(details.has_audio ? 'ready' : 'missing-audio')
    } catch (nextError) {
      setError(nextError.message); setPhase('idle'); setFile(null)
    }
  }

  async function start() {
    if (!file || phase !== 'ready') return
    setError(''); setResult(null); setProgress(0); setPhase('processing')
    try {
      const job = await sendVideo('/api/jobs', file, { silence_duration: duration, noise_db: noiseDb })
      setJobId(job.job_id)
    } catch (nextError) {
      setError(nextError.message); setPhase('failed')
    }
  }

  async function cancel() {
    if (!jobId) return
    try { await cancelJob(jobId); setJobId(null); setPhase('ready'); setProgress(0) }
    catch (nextError) { setError(nextError.message); setPhase('failed') }
  }

  async function showOutputFolder() {
    try { await openOutputFolder(result.job_id) }
    catch (nextError) { setError(nextError.message); setPhase('failed') }
  }

  const resetForSettings = () => { setResult(null); setError(''); setPhase('ready') }
  const openPicker = () => document.querySelector('[data-file-picker]')?.click()

  return <div className="app-shell">
    <header><div className="header-inner"><a className="brand" href="/"><Logo /> <strong>Silence Cutter</strong></a><span>Powered by FFmpeg · runs on your computer</span></div></header>
    <main>
      <input data-file-picker className="hidden-picker" type="file" accept="video/*" onChange={(e) => chooseFile(e.target.files?.[0])} />
      <section className="hero"><h1>Cut the dead air.<br /><em>Keep the video.</em></h1><p>Silence Cutter finds silent stretches in a video and removes them, so you get a tighter cut without opening an editor.</p></section>
      <WorkflowSteps phase={phase} />
      <section className="workspace">
        <VideoStage file={file} metadata={metadata} phase={phase} error={phase === 'idle' ? error : ''} onChoose={chooseFile} />
        <aside><Settings duration={duration} noiseDb={noiseDb} disabled={phase === 'processing' || phase === 'missing-audio'} onDuration={setDuration} onNoise={setNoiseDb} /><hr />
          <ProcessPanel phase={phase} progress={progress} result={result} error={error} onStart={start} onCancel={cancel} onRetry={resetForSettings} onOpenFolder={showOutputFolder} onChoose={openPicker} />
        </aside>
      </section>
    </main>
  </div>
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>)
