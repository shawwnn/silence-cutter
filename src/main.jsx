import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { cancelJob, getDownloadUrl, getHealth, openOutputFolder, sendVideo } from './api'
import { Logo, ProcessPanel, Settings, VideoStage, WorkflowSteps } from './components'
import { describeProcessingError, readBrowserMetadata } from './features/video-processing/media'
import { getJobOutcome } from './features/video-processing/jobOutcome'
import { useJobPolling } from './features/video-processing/useJobPolling'
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
  const [processingMessage, setProcessingMessage] = useState('Preparing your video…')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [publicMode, setPublicMode] = useState(false)

  useEffect(() => {
    getHealth().then((health) => setPublicMode(Boolean(health.public_mode))).catch(() => setPublicMode(false))
  }, [])

  useJobPolling(jobId, {
    onUpdate: (job) => {
      setProgress(Number(job.progress || 0))
      setProcessingMessage(job.message || 'Processing your video…')
      const outcome = getJobOutcome(job)
      if (!outcome) return
      setJobId(null)
      if (outcome.result !== undefined) setResult(outcome.result)
      if (outcome.error) setError(outcome.error)
      setPhase(outcome.phase)
    },
    onError: (nextError) => {
      setJobId(null); setError(describeProcessingError(nextError, publicMode)); setPhase('failed')
    },
  })

  async function chooseFile(nextFile) {
    if (!nextFile || phase === 'processing') return
    setFile(nextFile); setMetadata(null); setResult(null); setError(''); setPhase('reading')
    try {
      const details = await readBrowserMetadata(nextFile)
      setMetadata(details); setPhase('ready')
    } catch (nextError) {
      setError(nextError.message); setPhase('idle'); setFile(null)
    }
  }

  async function start() {
    if (!file || phase !== 'ready') return
    setError(''); setResult(null); setProgress(0); setProcessingMessage('Uploading video…'); setPhase('processing')
    try {
      const job = await sendVideo('/api/jobs', file, { silence_duration: duration, noise_db: noiseDb })
      if (job.media) setMetadata(job.media)
      setJobId(job.job_id)
    } catch (nextError) {
      setError(describeProcessingError(nextError, publicMode)); setPhase(nextError.code === 'missing_audio' ? 'missing-audio' : 'failed')
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
  const downloadOutput = () => { if (result?.job_id) window.location.assign(getDownloadUrl(result.job_id)) }

  return <div className="app-shell">
    <header><div className="header-inner"><a className="brand" href="/"><Logo /> <strong>Silence Cutter</strong></a><span>{publicMode ? 'Portfolio demo · temporary processing' : 'Powered by FFmpeg · runs on your computer'}</span></div></header>
    <main>
      <input data-file-picker className="hidden-picker" type="file" accept="video/*" onChange={(e) => chooseFile(e.target.files?.[0])} />
      <section className="hero"><h1>Cut the dead air.<br /><em>Keep the video.</em></h1><p>Silence Cutter finds silent stretches in a video and removes them, so you get a tighter cut without opening an editor.</p></section>
      <WorkflowSteps phase={phase} />
      <section className="workspace">
        <VideoStage file={file} metadata={metadata} phase={phase} error={phase === 'idle' ? error : ''} onChoose={chooseFile} />
        <aside><Settings duration={duration} noiseDb={noiseDb} disabled={phase === 'processing' || phase === 'missing-audio'} onDuration={setDuration} onNoise={setNoiseDb} /><hr />
          <ProcessPanel phase={phase} progress={progress} processingMessage={processingMessage} result={result} error={error} publicMode={publicMode} onStart={start} onCancel={cancel} onRetry={resetForSettings} onOpenFolder={showOutputFolder} onDownload={downloadOutput} onChoose={openPicker} />
        </aside>
      </section>
    </main>
  </div>
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>)
