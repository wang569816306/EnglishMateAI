/**
 * 会话管理服务
 * 提供会话列表、创建会话、加载会话消息等功能
 */
import apiClient from '../utils/api'

export interface Session {
  id: number
  session_id: string
  title: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

/**
 * 获取当前用户的历史会话列表
 */
export async function getSessionList(): Promise<Session[]> {
  try {
    const response = await apiClient.get('/sessions/list')
    console.log('getSessionList API响应:', response)
    return response || []  // apiClient已经返回了data字段
  } catch (error) {
    console.error('获取会话列表失败:', error)
    throw error
  }
}

/**
 * 创建新会话
 */
export async function createSession(title?: string): Promise<Session> {
  try {
    const response = await apiClient.post('/sessions/create', {
      title: title || '新对话'
    })
    console.log('createSession API响应:', response)
    return response  // apiClient已经返回了data字段
  } catch (error) {
    console.error('创建会话失败:', error)
    throw error
  }
}

/**
 * 获取指定会话的所有消息
 */
export async function getSessionMessages(sessionId: string): Promise<Message[]> {
  try {
    const response = await apiClient.get(`/sessions/${sessionId}/messages`)
    console.log('getSessionMessages API响应:', response)
    return response || []  // apiClient已经返回了data字段
  } catch (error) {
    console.error('获取会话消息失败:', error)
    throw error
  }
}

/**
 * 删除指定会话
 */
export async function deleteSession(sessionId: string): Promise<void> {
  try {
    await apiClient.delete(`/sessions/${sessionId}`)
  } catch (error) {
    console.error('删除会话失败:', error)
    throw error
  }
}

/**
 * 重命名会话
 */
export async function renameSession(sessionId: string, title: string): Promise<void> {
  try {
    await apiClient.put(`/sessions/${sessionId}`, { title })
  } catch (error) {
    console.error('重命名会话失败:', error)
    throw error
  }
}

/**
 * 保存当前会话ID到localStorage
 */
export function saveCurrentSessionId(sessionId: string): void {
  localStorage.setItem('current_session_id', sessionId)
}

/**
 * 从localStorage获取当前会话ID
 */
export function getCurrentSessionId(): string | null {
  return localStorage.getItem('current_session_id')
}

/**
 * 清除当前会话ID
 */
export function clearCurrentSessionId(): void {
  localStorage.removeItem('current_session_id')
}

// ==================== 口语训练对话API ====================

export interface SpeakingDialogue {
  id: number
  title: string
  scenario_id: number
  dialogue_data: any[]
  created_at: string
}

/**
 * 获取口语训练对话列表
 */
export async function getSpeakingDialogueList(): Promise<SpeakingDialogue[]> {
  try {
    const response = await apiClient.get('/scenarios/dialogues')
    console.log('getSpeakingDialogueList API响应:', response)
    return response || []  // apiClient已经返回了data字段
  } catch (error) {
    console.error('获取口语训练对话列表失败:', error)
    throw error
  }
}

/**
 * 获取口语训练对话详情
 */
export async function getSpeakingDialogueDetail(dialogueId: number): Promise<SpeakingDialogue> {
  try {
    const response = await apiClient.get(`/scenarios/dialogues/${dialogueId}`)
    console.log('getSpeakingDialogueDetail API响应:', response)
    return response  // apiClient已经返回了data字段
  } catch (error) {
    console.error('获取口语训练对话详情失败:', error)
    throw error
  }
}

/**
 * 删除口语训练对话
 */
export async function deleteSpeakingDialogue(dialogueId: number): Promise<void> {
  try {
    await apiClient.delete(`/scenarios/dialogues/${dialogueId}`)
  } catch (error) {
    console.error('删除口语训练对话失败:', error)
    throw error
  }
}

/**
 * 重命名口语训练对话
 */
export async function renameSpeakingDialogue(dialogueId: number, title: string): Promise<void> {
  try {
    await apiClient.put(`/scenarios/dialogues/${dialogueId}`, { title })
  } catch (error) {
    console.error('重命名口语训练对话失败:', error)
    throw error
  }
}
