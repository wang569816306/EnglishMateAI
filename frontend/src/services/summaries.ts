import api from '../utils/api'

export interface SummarizeRequest {
  video_title: string
  subtitles: string
  language?: string
}

// 流式总结（SSE）
export async function summarizeVideoStream(
  request: SummarizeRequest,
  onChunk: (chunk: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void
) {
  try {
    // 使用 apiClient 的 baseURL，避免重复 /ai/ 前缀
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/ai'
    const response = await fetch(`${baseURL}/summaries/summarize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(request)
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader!.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.type === 'chunk') {
              onChunk(data.content)
            } else if (data.status === 'completed') {
              console.log('✅ 总结完成')
              onComplete()
              return
            }
          } catch (parseError) {
            console.error('解析SSE数据失败:', line, parseError)
          }
        }
      }
    }
  } catch (error) {
    onError(error as Error)
  }
}

// AI 视频内容问答
export interface QuestionRequest {
  video_title: string
  subtitles: string
  question: string
  language?: string
}

export interface AnswerResponse {
  answer: string
}

export async function askQuestion(request: QuestionRequest): Promise<AnswerResponse> {
  const response = await api.post('/summaries/ask-question', request)
  return response.data
}
