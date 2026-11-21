const SERVICE_UNAVAILABLE = 'The processing service became unavailable. Try again.'

async function requestJson(path, options = {}) {
  let response
  try {
    response = await fetch(path, options)
  } catch {
    const error = new Error(SERVICE_UNAVAILABLE)
    error.code = 'service_unavailable'
    throw error
  }
  const text = await response.text()
  let data = null
  try { data = text ? JSON.parse(text) : null } catch { /* handled below */ }
  if (!data || typeof data !== 'object') {
    const error = new Error(SERVICE_UNAVAILABLE)
    error.code = 'service_unavailable'
    error.status = response.status
    throw error
  }
  if (!response.ok) {
    const error = new Error(data.error || 'Request failed')
    error.code = data.code
    error.status = response.status
    throw error
  }
  return data
}

export async function sendVideo(path, file, fields = {}) {
  const body = new FormData()
  body.append('file', file)
  Object.entries(fields).forEach(([key, value]) => body.append(key, value))
  return requestJson(path, { method: 'POST', body })
}

export async function getHealth() {
  return requestJson('/api/health')
}

export async function getJob(jobId) {
  return requestJson(`/api/jobs/${jobId}`)
}

export async function cancelJob(jobId) {
  return requestJson(`/api/jobs/${jobId}/cancel`, { method: 'POST' })
}

export async function openOutputFolder(jobId) {
  return requestJson(`/api/jobs/${jobId}/open-output-folder`, { method: 'POST' })
}

export function getDownloadUrl(jobId) {
  return `/api/jobs/${jobId}/download`
}
