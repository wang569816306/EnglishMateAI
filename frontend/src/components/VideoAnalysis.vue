<template>
  <div class="video-analysis-page">
    <a-row :gutter="[24, 24]">
      <!-- 左侧：视频信息 -->
      <a-col :xs="24" :lg="10">
        <div class="video-thumbnail">
          <img
            v-if="videoInfo?.thumbnail"
            :src="videoInfo.thumbnail"
            :alt="videoInfo.title"
            @error="(e: any) => e.target.style.display = 'none'"
          />
          <div v-else class="thumbnail-placeholder">
            <a-icon type="video-camera" style="font-size: 48px; color: #d9d9d9;" />
          </div>
          <div v-if="videoInfo?.duration_string" class="duration-badge">
            {{ videoInfo.duration_string }}
          </div>
        </div>

        <div class="video-info">
          <h2 class="video-title">{{ videoInfo?.title }}</h2>
          <div class="video-meta">
            <span class="meta-item">
              <a-icon type="user" />
              {{ videoInfo?.uploader }}
            </span>
            <a-tag color="blue">{{ videoInfo?.platform }}</a-tag>
            <span v-if="videoInfo?.view_count" class="meta-item">
              <a-icon type="eye" />
              {{ formatViewCount(videoInfo.view_count) }}
            </span>
          </div>
        </div>

        <!-- 字幕控制 -->
        <div class="subtitle-controls">
          <h4>
            <a-icon type="file-text" /> 字幕文本
          </h4>
          <a-textarea
            v-model="subtitlesModel"
            placeholder="粘贴字幕文本,或等待AI自动生成..."
            :rows="6"
          />
          <div class="subtitle-actions">
            <a-button @click="handleExportSubtitle('srt')">
              <a-icon type="download" /> 导出 SRT
            </a-button>
            <a-button @click="handleExportSubtitle('vtt')">
              <a-icon type="download" /> 导出 VTT
            </a-button>
            <a-button @click="handleExportSubtitle('txt')">
              <a-icon type="download" /> 导出 TXT
            </a-button>
          </div>
        </div>
      </a-col>

      <!-- 右侧：AI分析结果 -->
      <a-col :xs="24" :lg="14">
        <a-tabs v-model="activeTab" class="analysis-tabs">
          <!-- 总结摘要 -->
          <a-tab-pane key="summary" tab="📝 总结摘要">
            <div class="summary-container">
              <div v-if="summarizing" class="loading-state">
                <a-spin size="large" />
                <p>AI 正在生成总结...</p>
              </div>
              <div v-else-if="!summary" class="empty-state">
                <a-icon type="robot" style="font-size: 48px; color: #d9d9d9;" />
                <p>点击按钮开始 AI 智能总结</p>
              </div>
              <div v-else class="summary-content markdown-body" v-html="renderedSummary"></div>
            </div>
            <a-button
              type="primary"
              size="large"
              block
              :loading="summarizing"
              @click="handleSummarize"
              class="analyze-button"
            >
              <a-icon type="robot" /> 
              {{ summarizing ? 'AI 分析中...' : 'AI 智能总结' }}
            </a-button>
          </a-tab-pane>

          <!-- 字幕文本 -->
          <a-tab-pane key="subtitles" tab="📄 字幕文本">
            <div class="subtitles-container">
              <a-textarea
                v-model="subtitlesModel"
                placeholder="字幕文本内容..."
                :rows="16"
                readonly
              />
            </div>
          </a-tab-pane>

          <!-- 思维导图 -->
          <a-tab-pane key="mindmap" tab=" 思维导图">
            <div class="mindmap-container">
              <div v-if="!mindmapData" class="empty-state">
                <a-icon type="apartment" style="font-size: 48px; color: #d9d9d9;" />
                <p>思维导图将在总结完成后自动生成</p>
              </div>
              <div v-else ref="mindmapContainer" class="mindmap-view"></div>
            </div>
            <div class="mindmap-actions">
              <a-button @click="handleFullscreen">
                <a-icon type="fullscreen" /> 全屏展示
              </a-button>
              <a-button @click="handleExportMindmap('png')">
                <a-icon type="download" /> 导出 PNG
              </a-button>
              <a-button @click="handleExportMindmap('svg')">
                <a-icon type="download" /> 导出 SVG
              </a-button>
            </div>
          </a-tab-pane>

          <!-- AI问答 -->
          <a-tab-pane key="qa" tab="💬 AI问答">
            <div class="qa-container">
              <div class="chat-messages" ref="chatContainer">
                <div
                  v-for="(msg, index) in chatMessages"
                  :key="index"
                  :class="['message', msg.role === 'user' ? 'user-message' : 'ai-message']"
                >
                  <div class="message-avatar">
                    <a-icon :type="msg.role === 'user' ? 'user' : 'robot'" />
                  </div>
                  <div class="message-content">{{ msg.content }}</div>
                </div>
              </div>
              <div class="chat-input">
                <a-input
                  v-model="question"
                  placeholder="针对视频内容提问..."
                  @pressEnter="handleAskQuestion"
                  :disabled="asking"
                >
                  <a-button
                    slot="addonAfter"
                    type="primary"
                    :loading="asking"
                    @click="handleAskQuestion"
                  >
                    <a-icon type="send" />
                  </a-button>
                </a-input>
              </div>
            </div>
          </a-tab-pane>
        </a-tabs>
      </a-col>
    </a-row>

    <!-- 全屏思维导图 -->
    <a-modal
      v-model="fullscreenVisible"
      title="思维导图 - 全屏模式"
      width="95vw"
      :footer="null"
      @cancel="fullscreenVisible = false"
    >
      <div ref="fullscreenContainer" class="fullscreen-mindmap"></div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { message } from 'ant-design-vue'
import { summarizeVideoStream, generateMindmap, askQuestion, type MindmapData } from '@/services/summaries'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'

interface VideoInfo {
  title: string
  uploader: string
  platform: string
  thumbnail?: string
  duration_string?: string
  view_count?: number
}

const props = defineProps<{
  videoInfo: VideoInfo | null
  subtitles: string
}>()

const emit = defineEmits<{
  'update:subtitles': [value: string]
}>()

// 创建计算属性用于 v-model 绑定
const subtitlesModel = computed({
  get: () => props.subtitles,
  set: (value: string) => emit('update:subtitles', value)
})

// 状态
const activeTab = ref('summary')
const summarizing = ref(false)
const summary = ref('')
const mindmapData = ref<MindmapData | null>(null)
const asking = ref(false)
const question = ref('')
const chatMessages = ref<Array<{ role: 'user' | 'ai', content: string }>>([])
const fullscreenVisible = ref(false)

// Refs
const mindmapContainer = ref<HTMLElement | null>(null)
const fullscreenContainer = ref<HTMLElement | null>(null)
const chatContainer = ref<HTMLElement | null>(null)

// 计算属性
const renderedSummary = computed(() => {
  // 简单的 Markdown 渲染
  return summary.value
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    .replace(/\*\*(.*)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*)\*/g, '<em>$1</em>')
    .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
    .replace(/^-\s+(.*$)/gm, '<li>$1</li>')
    .replace(/\n/g, '<br>')
})

// 格式化观看次数
function formatViewCount(count: number): string {
  if (!count) return ''
  if (count >= 100000000) return (count / 100000000).toFixed(1) + '亿'
  if (count >= 10000) return (count / 10000).toFixed(1) + '万'
  return count.toLocaleString()
}

// AI 智能总结
async function handleSummarize() {
  if (!props.videoInfo) {
    message.warning('请先选择视频')
    return
  }

  summarizing.value = true
  summary.value = ''
  mindmapData.value = null

  try {
    await summarizeVideoStream(
      {
        video_title: props.videoInfo.title,
        subtitles: props.subtitles || '暂无字幕'
      },
      (chunk) => {
        summary.value += chunk
      },
      (data) => {
        mindmapData.value = data
        renderMindmap()
      },
      () => {
        summarizing.value = false
        message.success('总结完成')
      },
      (error) => {
        summarizing.value = false
        message.error('总结失败：' + error.message)
      }
    )
  } catch (error: any) {
    summarizing.value = false
    message.error('总结失败')
  }
}

// 渲染思维导图
function renderMindmap() {
  nextTick(() => {
    if (!mindmapData.value || !mindmapContainer.value) return

    const transformer = new Transformer()
    const { root } = transformer.transform(mindmapData.value.root.content)
    
    // 添加子节点
    if (mindmapData.value.root.children) {
      mindmapData.value.root.children.forEach(child => {
        root.children!.push(transformer.transform(child.content).root)
      })
    }

    Markmap.create(mindmapContainer.value, undefined, root)
  })
}

// 全屏展示
async function handleFullscreen() {
  fullscreenVisible.value = true
  await nextTick()
  
  if (mindmapData.value && fullscreenContainer.value) {
    const transformer = new Transformer()
    const { root } = transformer.transform(mindmapData.value.root.content)
    
    if (mindmapData.value.root.children) {
      mindmapData.value.root.children.forEach(child => {
        root.children!.push(transformer.transform(child.content).root)
      })
    }

    Markmap.create(fullscreenContainer.value, undefined, root)
  }
}

// 导出思维导图
async function handleExportMindmap(format: 'png' | 'svg') {
  if (!mindmapData.value || !mindmapContainer.value) {
    message.warning('请先生成思维导图')
    return
  }

  try {
    const svg = mindmapContainer.value.querySelector('svg')
    if (!svg) {
      message.error('导出失败')
      return
    }

    if (format === 'svg') {
      const svgData = new XMLSerializer().serializeToString(svg)
      const blob = new Blob([svgData], { type: 'image/svg+xml' })
      downloadBlob(blob, `mindmap-${props.videoInfo?.title}.svg`)
      message.success('SVG 导出成功')
    } else {
      // PNG 导出
      const canvas = document.createElement('canvas')
      const svgData = new XMLSerializer().serializeToString(svg)
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml' })
      const url = URL.createObjectURL(svgBlob)
      
      const img = new Image()
      img.onload = () => {
        canvas.width = img.width
        canvas.height = img.height
        const ctx = canvas.getContext('2d')
        ctx?.drawImage(img, 0, 0)
        canvas.toBlob((blob) => {
          if (blob) {
            downloadBlob(blob, `mindmap-${props.videoInfo?.title}.png`)
            message.success('PNG 导出成功')
          }
        })
        URL.revokeObjectURL(url)
      }
      img.src = url
    }
  } catch (error) {
    message.error('导出失败')
  }
}

// 导出字幕
function handleExportSubtitle(format: 'srt' | 'vtt' | 'txt') {
  if (!props.subtitles) {
    message.warning('暂无字幕可导出')
    return
  }

  let content = props.subtitles
  let filename = `subtitles-${props.videoInfo?.title}.${format}`

  if (format === 'vtt') {
    content = `WEBVTT\n\n${content}`
  }

  const blob = new Blob([content], { type: 'text/plain' })
  downloadBlob(blob, filename)
  message.success(`${format.toUpperCase()} 导出成功`)
}

// 下载 Blob
function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// AI 问答
async function handleAskQuestion() {
  if (!question.value.trim()) return

  if (!props.videoInfo) {
    message.warning('请先选择视频')
    return
  }

  const userQuestion = question.value
  question.value = ''
  chatMessages.value.push({ role: 'user', content: userQuestion })

  asking.value = true

  try {
    const response = await askQuestion({
      video_title: props.videoInfo.title,
      subtitles: props.subtitles || '暂无字幕',
      question: userQuestion,
      language: 'zh'
    })

    chatMessages.value.push({
      role: 'ai',
      content: response.answer
    })
    
    // 滚动到底部
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    })
  } catch (error: any) {
    message.error('问答失败：' + (error.message || '未知错误'))
  } finally {
    asking.value = false
  }
}

// 组件挂载
onMounted(() => {
  // 初始化
})
</script>

<style scoped>
.video-analysis-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.video-thumbnail {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f5f5;
  margin-bottom: 16px;
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.duration-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.7);
  color: #ffffff;
  font-size: 12px;
  border-radius: 4px;
}

.video-info {
  margin-bottom: 24px;
}

.video-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 12px;
  line-height: 1.4;
}

.video-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #595959;
}

.subtitle-controls {
  margin-top: 24px;
}

.subtitle-controls h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.subtitle-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.analysis-tabs {
  min-height: 600px;
}

.summary-container {
  min-height: 400px;
  margin-bottom: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #8c8c8c;
}

.loading-state p,
.empty-state p {
  margin-top: 16px;
}

.summary-content {
  line-height: 1.8;
}

.summary-content h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 16px 0 8px;
}

.summary-content h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 12px 0 6px;
}

.summary-content h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 8px 0 4px;
}

.summary-content li {
  margin-left: 20px;
  margin-bottom: 4px;
}

.analyze-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.subtitles-container {
  min-height: 500px;
}

.mindmap-container {
  min-height: 500px;
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.mindmap-view {
  width: 100%;
  height: 500px;
}

.mindmap-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.fullscreen-mindmap {
  width: 100%;
  height: 80vh;
}

.qa-container {
  display: flex;
  flex-direction: column;
  height: 550px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #1890ff;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-message .message-avatar {
  background: #52c41a;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.user-message .message-content {
  background: #e6f7ff;
}

.chat-input {
  margin-top: auto;
}

@media (max-width: 768px) {
  .video-analysis-page {
    padding: 16px;
  }

  .mindmap-view {
    height: 400px;
  }

  .qa-container {
    height: 500px;
  }
}
</style>
