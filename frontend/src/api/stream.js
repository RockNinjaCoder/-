const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const createStreamSource = (sessionId) => {
  return `${API_BASE_URL}/chat/stream/${sessionId}`
}

export const parseStreamData = (data) => {
  try {
    const lines = data.split('\n')
    const result = {}
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const jsonStr = line.slice(6)
        if (jsonStr === '[DONE]') {
          result.done = true
        } else {
          const parsed = JSON.parse(jsonStr)
          Object.assign(result, parsed)
        }
      }
    }
    
    return result
  } catch (error) {
    console.error('Parse stream data error:', error)
    return { error: error.message }
  }
}

export const fetchStream = async (sessionId, onMessage, onError, onDone) => {
  const controller = new AbortController()
  
  try {
    const response = await fetch(createStreamSource(sessionId), {
      method: 'GET',
      headers: {
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache'
      },
      signal: controller.signal
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        onDone?.()
        break
      }

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.trim()) {
          const data = parseStreamData(line)
          onMessage?.(data)
          
          if (data.done) {
            onDone?.()
            return
          }
        }
      }
    }
  } catch (error) {
    if (error.name !== 'AbortError') {
      onError?.(error)
    }
  }

  return controller
}

export const abortStream = (controller) => {
  controller?.abort()
}

export default {
  createStreamSource,
  parseStreamData,
  fetchStream,
  abortStream
}