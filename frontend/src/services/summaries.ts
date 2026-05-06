import api from '../utils/api'

export interface SummarizeRequest {
  video_title: string
  subtitles: string
  language?: string
}

export interface MindmapNode {
  content: string
  children?: MindmapNode[]
}

export interface MindmapData {
  title: string
  root: MindmapNode
}

// 流式总结（SSE）
export async function summarizeVideoStream(
  request: SummarizeRequest,
  onChunk: (chunk: string) => void,
  onMindmap: (data: MindmapData) => void,
  onComplete: () => void,
  onError: (error: Error) => void
) {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/ai/summaries/summarize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
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
          const data = JSON.parse(line.slice(6))
          
          if (data.type === 'chunk') {
            onChunk(data.content)
          } else if (data.type === 'mindmap') {
            onMindmap(data.data)
          } else if (data.status === 'completed') {
            onComplete()
            return
          }
        }
      }
    }
  } catch (error) {
    onError(error as Error)
  }
}

// 生成思维导图
export async function generateMindmap(request: SummarizeRequest): Promise<{ mindmap: MindmapData }> {
  return await api.post('/ai/summaries/generate-mindmap', request)
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
  const response = await api.post('/ai/summaries/ask-question', request)
  return response.data
}
