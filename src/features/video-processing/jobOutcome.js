const TERMINAL_PHASES = {
  completed: 'completed',
  timing_warning: 'timing-warning',
  needs_confirmation: 'no-silence',
  settings_warning: 'over-cut',
  cancelled: 'ready',
  failed: 'failed',
}

export function getJobOutcome(job) {
  const phase = TERMINAL_PHASES[job.state]
  if (!phase) return null

  const result = job.state === 'completed' || job.state === 'timing_warning'
    ? { ...job.result, job_id: job.job_id }
    : job.result
  return { phase, result, error: job.state === 'failed' ? job.error || 'Processing failed.' : '' }
}
