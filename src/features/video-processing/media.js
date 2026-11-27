export function describeProcessingError(error, publicMode) {
  if (publicMode && error?.code === 'service_unavailable') {
    return 'The demo server restarted while rendering. No output was created. Try a shorter or lower-resolution video.'
  }
  return error?.message || 'Processing failed.'
}

export function readBrowserMetadata(file) {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file)
    const video = document.createElement('video')
    video.preload = 'metadata'
    const finish = (durationSeconds = null) => {
      URL.revokeObjectURL(url)
      const suffix = file.name.split('.').pop()?.toLowerCase() || 'video'
      resolve({ filename: file.name, size_bytes: file.size, duration_seconds: durationSeconds, format: suffix, has_audio: true })
    }
    video.onloadedmetadata = () => finish(Number.isFinite(video.duration) ? video.duration : null)
    video.onerror = () => finish()
    video.src = url
  })
}
