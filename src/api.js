export async function sendVideo(path, file, fields = {}) {
  const body = new FormData()
  body.append('file', file)
  Object.entries(fields).forEach(([key, value]) => body.append(key, value))
  const response = await fetch(path, { method: 'POST', body })
  const data = await response.json()
  if (!response.ok) {
    const error = new Error(data.error || 'Request failed')
    error.code = data.code
    error.status = response.status
    throw error
  }
  return data
}

export async function getHealth() {
  const response = await fetch('/api/health')
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || 'Unable to read service status')
  return data
}

export async function getJob(jobId) {
  const response = await fetch(`/api/jobs/${jobId}`)
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || 'Unable to read job status')
  return data
}

export async function cancelJob(jobId) {
  const response = await fetch(`/api/jobs/${jobId}/cancel`, { method: 'POST' })
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || 'Unable to cancel processing')
  return data
}

export async function openOutputFolder(jobId) {
  const response = await fetch(`/api/jobs/${jobId}/open-output-folder`, { method: 'POST' })
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || 'Unable to open output folder')
  return data
}

export function getDownloadUrl(jobId) {
  return `/api/jobs/${jobId}/download`
}
