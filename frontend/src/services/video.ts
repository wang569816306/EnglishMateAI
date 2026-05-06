/**
 * 视频下载API服务
 */
import apiClient from '../utils/api'

export interface VideoFormat {
  format_id: string
  ext: string
  resolution: string
  height: number
  filesize?: number
  filesize_approx?: number
  vcodec: string
  acodec?: string | null
  has_audio: boolean
  label: string
}

export interface VideoInfo {
  id: string
  title: string
  thumbnail: string
  duration?: number
  duration_string: string
  uploader: string
  platform: string
  view_count?: number
  upload_date: string
  description: string
  formats: VideoFormat[]
  subtitles: string[]
  automatic_captions: string[]
}

export interface DownloadResult {
  title: string
  filename: string
  ext: string
  download_url: string
  filepath: string
}

export interface DirectUrlResult {
  direct_url: string
  ext: string
  filesize?: number
  title: string
}

export interface DownloadHistory {
  filename: string
  size: number
  created_time: number
  modified_time: number
  download_url: string
  title?: string
  format?: string
  filesize?: number
  created_at?: number
}

/**
 * 解析视频信息
 */
export async function parseVideo(url: string): Promise<VideoInfo> {
  const response = await apiClient.post('/videos/parse', { url })
  return response
}

/**
 * 下载视频到服务器
 */
export async function downloadVideo(url: string, formatId: string): Promise<DownloadResult> {
  const response = await apiClient.post('/videos/download', { 
    url, 
    format_id: formatId 
  })
  return response
}

/**
 * 获取视频直链
 */
export async function getDirectUrl(url: string, formatId: string): Promise<DirectUrlResult> {
  const response = await apiClient.post('/videos/direct-url', { 
    url, 
    format_id: formatId 
  })
  return response
}

/**
 * 代理下载视频（通过后端下载，避免CORS和HTTP头问题）
 * 返回文件blob和文件名
 */
export async function proxyDownload(url: string, formatId: string): Promise<{ blob: Blob, filename: string }> {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/ai'
  const response = await fetch(`${baseURL}/videos/proxy-download`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, format_id: formatId })
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '下载失败')
  }
  
  // 从Content-Disposition获取文件名
  const contentDisposition = response.headers.get('Content-Disposition')
  let filename = 'video.mp4'
  if (contentDisposition) {
    const match = contentDisposition.match(/filename\*?=([^;]+)/)
    if (match) {
      filename = match[1].replace(/['"]|utf-8/gi, '').trim()
    }
  }
  
  const blob = await response.blob()
  return { blob, filename }
}

/**
 * 获取下载历史记录
 */
export async function getDownloadHistory(): Promise<DownloadHistory[]> {
  const response = await apiClient.get('/videos/history')
  return response
}

/**
 * 删除已下载的文件
 */
export async function deleteDownloadFile(filename: string): Promise<void> {
  await apiClient.delete(`/videos/file/${filename}`)
}

/**
 * 获取文件下载URL
 */
export function getFileDownloadUrl(filename: string): string {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseURL}/api/v1/videos/file/${filename}`
}
