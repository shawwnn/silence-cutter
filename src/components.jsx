export function Logo() {
  return <span className="logo" aria-hidden="true"><i /><i /><i /><i /></span>
}

export function WorkflowSteps({ phase }) {
  const steps = ['Select video', 'Set settings', 'Process', 'Done']
  const active = phase === 'idle' || phase === 'reading' ? 0 : phase === 'ready' || phase === 'missing-audio' ? 1 : phase === 'processing' || phase === 'failed' || phase === 'no-silence' ? 2 : 3
  return <ol className="steps" aria-label="Workflow progress">
    {steps.map((label, index) => <li key={label} className={index < active ? 'done' : index === active ? 'current' : ''}>
      <span>{index < active ? '✓' : index + 1}</span>{label}
    </li>)}
  </ol>
}

export function VideoStage({ file, metadata, phase, error, onChoose }) {
  const locked = phase === 'processing'
  const choose = (event) => {
    const next = event.target.files?.[0]
    if (next) onChoose(next)
    event.target.value = ''
  }
  const drop = (event) => {
    event.preventDefault()
    if (!locked && event.dataTransfer.files?.[0]) onChoose(event.dataTransfer.files[0])
  }
  const reading = phase === 'reading'
  return <section className="video-stage" onDragOver={(e) => e.preventDefault()} onDrop={drop}>
    {!file ? <label className={`dropzone ${error ? 'has-error' : ''}`}>
      <input type="file" accept="video/*" onChange={choose} />
      <span className="upload-icon">↑</span>
      <strong>Drop a video here</strong>
      <span>or browse your files</span>
      <small>Any video FFmpeg can read</small>
    </label> : <div className="selected-video">
      <div className="file-icon">▶</div>
      <div className="file-name"><span>Selected video</span><strong>{file.name}</strong></div>
      <div className="file-meta">
        <Meta label="Format" value={metadata?.format?.toUpperCase() || '—'} />
        <Meta label="Size" value={metadata ? formatBytes(metadata.size_bytes) : '—'} />
        <Meta label="Duration" value={reading ? 'Reading…' : metadata ? formatDuration(metadata.duration_seconds) : '—'} />
      </div>
      <div className="replace-row"><span>{locked ? 'Locked while processing.' : reading ? 'Reading video details…' : 'Drop another video here to replace it.'}</span>
        <label className={`ghost-button ${locked ? 'disabled' : ''}`}>Choose a different video<input type="file" accept="video/*" disabled={locked} onChange={choose} /></label>
      </div>
    </div>}
    {error && <p className="inline-error" role="alert">{error}</p>}
  </section>
}

function Meta({ label, value }) { return <div><span>{label}</span><strong>{value}</strong></div> }

export function Settings({ duration, noiseDb, disabled, onDuration, onNoise }) {
  const description = noiseDb <= -45 ? 'Cuts only near-total silence. Keeps quiet speech and room tone.' : noiseDb <= -25 ? 'Balanced. Cuts pauses and quiet gaps between speech.' : 'Cuts aggressively. Soft speech and background sound may be removed.'
  return <section className={`settings ${disabled ? 'dimmed' : ''}`}>
    <div className="setting-head"><div><h2>Silence threshold</h2><p>Audio quieter than this is cut.</p></div><output>{noiseDb} <small>dB</small></output></div>
    <input type="range" min="-60" max="-16" step="1" value={noiseDb} disabled={disabled} onChange={(e) => onNoise(Number(e.target.value))} />
    <div className="range-labels"><span>Gentle</span><span>Aggressive</span></div>
    <p className="setting-description">{description}</p>
    <button className="text-button" disabled={disabled || noiseDb === -38} onClick={() => onNoise(-38)}>Reset to default (−38 dB)</button>
    <div className="duration-setting"><div className="setting-head"><div><h2>Minimum silence duration</h2><p>How long silence must last before it is cut.</p></div><output>{duration.toFixed(1)} <small>sec</small></output></div>
      <input type="range" min="0.1" max="1.9" step="0.1" value={duration} disabled={disabled} onChange={(e) => onDuration(Number(e.target.value))} />
    </div>
  </section>
}

export function ProcessPanel({ phase, progress, result, error, onStart, onCancel, onRetry, onOpenFolder, onChoose }) {
  if (phase === 'processing') return <div className="process-panel" role="status"><button className="primary busy" onClick={onCancel}>Cancel processing</button><Progress progress={progress} /><p>Keep this window open. Longer videos take longer.</p></div>
  if (phase === 'completed' && result) return <div className="process-panel result-panel"><h2 className="success">✓ Silence removed</h2><ResultDetails result={result} /><button className="primary" onClick={onOpenFolder}>Open output folder</button><button className="text-button centered" onClick={onChoose}>Process another video</button></div>
  if (phase === 'timing-warning' && result) return <div className="process-panel warning-panel"><h2>Output timing could not be verified</h2><p>The MP4 was created, but its duration differs more than expected.</p><ResultDetails result={result} /><button className="primary" onClick={onOpenFolder}>Open output folder</button><button className="text-button centered" onClick={onRetry}>Try again</button></div>
  if (phase === 'no-silence' && result) return <div className="process-panel warning-panel"><h2>No matching silence found</h2><p>No output was created. Try a shorter duration or a higher threshold, such as −30 dB.</p><ResultDetails result={result} /><button className="primary" onClick={onRetry}>Adjust settings</button><button className="text-button centered" onClick={onChoose}>Choose another video</button></div>
  if (phase === 'missing-audio') return <div className="process-panel warning-panel"><h2>No audio track detected</h2><p>Silence Cutter needs an audio track to find silent sections. Choose a different video to continue.</p><button className="primary" onClick={onChoose}>Choose a different video</button></div>
  if (phase === 'failed') return <div className="process-panel error-panel"><h2>Processing failed</h2><p>{error || 'Processing stopped unexpectedly.'}</p><button className="primary" onClick={onRetry}>Try again</button><button className="text-button centered" onClick={onChoose}>Choose another video</button></div>
  return <div className="process-panel"><button className="primary" disabled={phase !== 'ready'} onClick={onStart}>✂ Remove silence</button><p>{phase === 'ready' ? 'Your original file is never changed.' : phase === 'reading' ? 'Reading the video…' : 'Select a video to get started.'}</p></div>
}

function Progress({ progress }) { const percent = Math.round((progress || 0) * 100); return <div className="progress"><div><i style={{ width: `${percent}%` }} /></div><span>{percent}%</span></div> }
function ResultDetails({ result }) { return <dl className="result-details"><div><dt>Input / output</dt><dd>{formatDuration(result.input_duration_seconds)} → {formatDuration(result.output_duration_seconds)}</dd></div><div><dt>Expected / actual</dt><dd>{formatDuration(result.expected_duration_seconds)} → {formatDuration(result.output_duration_seconds)}{result.duration_difference_seconds !== undefined ? ` (${result.duration_difference_seconds.toFixed(3)} sec difference)` : ''}</dd></div><div><dt>Silence removed</dt><dd>{result.detected_silence_count || 0} interval(s) · {formatDuration(result.removed_duration_seconds || 0)}</dd></div></dl> }
function formatBytes(bytes) { return bytes < 1024 * 1024 ? `${Math.round(bytes / 1024)} KB` : `${(bytes / (1024 * 1024)).toFixed(1)} MB` }
function formatDuration(seconds) { if (seconds === null || seconds === undefined) return '—'; if (seconds < 60) return `${Math.round(seconds)} sec`; return `${Math.floor(seconds / 60)} min ${Math.round(seconds % 60)} sec` }
