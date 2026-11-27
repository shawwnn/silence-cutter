import { useEffect, useRef } from 'react'
import { getJob } from '../../api'

export function useJobPolling(jobId, { onUpdate, onError }) {
  const callbacks = useRef({ onUpdate, onError })

  useEffect(() => {
    callbacks.current = { onUpdate, onError }
  }, [onUpdate, onError])

  useEffect(() => {
    if (!jobId) return undefined
    const timer = setInterval(async () => {
      try {
        callbacks.current.onUpdate(await getJob(jobId))
      } catch (error) {
        callbacks.current.onError(error)
      }
    }, 500)
    return () => clearInterval(timer)
  }, [jobId])
}
