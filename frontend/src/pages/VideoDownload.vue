<template>
  <div class="video-download-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          全网视频，<span class="highlight">一键下载</span>
        </h1>
        <p class="hero-description">
          支持 YouTube、Bilibili、抖音、TikTok、Twitter、Instagram 等全球主流平台，极速解析，多种清晰度选择。
        </p>

        <!-- 搜索框 -->
        <div class="search-container">
          <a-input
            v-model:value="videoUrl"
            placeholder="粘贴视频链接，立即解析..."
            size="large"
            class="search-input"
            @pressEnter="handleParse"
          >
            <template #prefix>
              <LinkOutlined />
            </template>
          </a-input>
          <a-button
            type="primary"
            size="large"
            :loading="loading"
            :disabled="!canParse"
            @click="handleParse"
            class="search-button"
          >
            {{ loading ? '解析中...' : '解析视频' }}
          </a-button>
        </div>
      </div>
    </section>

    <!-- Result Section -->
    <section v-if="videoInfo" class="result-section">
      <a-row :gutter="[24, 24]">
        <!-- Left: Video Info & Download -->
        <a-col :xs="24" :md="10">
          <a-card class="video-info-card" :bordered="false">
            <!-- 视频缩略图 -->
            <div class="video-thumbnail">
              <img v-if="videoInfo.thumbnail" :src="videoInfo.thumbnail" alt="Video Thumbnail" @error="(e: any) => e.target.style.display = 'none'" />
              <div v-else class="thumbnail-placeholder">
                <VideoCameraOutlined style="font-size: 48px; color: #d9d9d9" />
              </div>
              <div v-if="videoInfo.duration" class="duration-badge">
                {{ formatDuration(videoInfo.duration) }}
              </div>
            </div>

            <!-- 视频信息 -->
            <div class="video-info">
              <h3 class="video-title">{{ videoInfo.title }}</h3>
              <div class="video-meta">
                <span class="meta-item">
                  <UserOutlined /> {{ videoInfo.uploader || '未知' }}
                </span>
                <a-tag color="blue">{{ videoInfo.platform }}</a-tag>
                <span v-if="videoInfo.view_count" class="meta-item">
                  <EyeOutlined /> {{ formatViewCount(videoInfo.view_count) }}
                </span>
              </div>
              <p class="video-description">{{ videoInfo.description }}</p>
            </div>

            <a-divider />

            <!-- 格式选择 -->
            <div class="format-selection">
              <h4 class="format-title">
                <SettingOutlined /> 选择清晰度和格式
              </h4>
              <div class="format-list">
                <div
                  v-for="format in videoInfo.formats"
                  :key="format.format_id"
                  :class="['format-item', { 'format-item-active': selectedFormat === format.format_id }]"
                  @click="selectedFormat = format.format_id"
                >
                  <div class="format-icon" :style="{ background: getFormatColor(format) }">
                    <VideoCameraOutlined />
                  </div>
                  <div class="format-info">
                    <div class="format-label">{{ format.label }}</div>
                    <div class="format-detail">
                      {{ format.ext?.toUpperCase() }} · {{ format.has_audio ? '含音频' : '仅视频' }}
                      <span v-if="format.filesize || format.filesize_approx"> · {{ formatFileSize(format.filesize || format.filesize_approx || 0) }}</span>
                    </div>
                  </div>
                  <div class="format-check">
                    <CheckCircleFilled v-if="selectedFormat === format.format_id" style="color: #1890ff; font-size: 20px" />
                  </div>
                </div>
              </div>

              <!-- 下载操作按钮 -->
              <div class="download-actions">
                <a-button
                  type="primary"
                  size="large"
                  block
                  :loading="gettingDirectUrl"
                  :disabled="!selectedFormat"
                  @click="handleDirectDownload"
                  class="download-button"
                >
                  <CloudDownloadOutlined />
                  {{ gettingDirectUrl ? '获取链接中...' : '直接下载' }}
                </a-button>
              </div>
            </div>
          </a-card>
        </a-col>

        <!-- Right: AI Analysis Tabs -->
        <a-col :xs="24" :md="14">
          <a-card class="analysis-card" :bordered="false">
            <a-tabs v-model:activeKey="activeTab" class="analysis-tabs">
              <!-- 总结摘要 Tab -->
              <a-tab-pane key="summary" tab=" 总结摘要">
                <div class="tab-content">
                  <div v-if="summarizing" class="loading-state">
                    <a-spin size="large" />
                    <p>AI 正在生成总结...</p>
                  </div>
                  <div v-else-if="!summary" class="empty-state">
                    <RobotOutlined style="font-size: 48px; color: #d9d9d9" />
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
                  <RobotOutlined />
                  {{ summarizing ? 'AI 分析中...' : 'AI 智能总结' }}
                </a-button>
              </a-tab-pane>

              <!-- 字幕文本 Tab -->
              <a-tab-pane key="subtitles" tab=" 字幕文本">
                <div class="tab-content">
                  <a-alert
                    message="提示"
                    description="如果视频有自动字幕，将在解析后自动显示。您也可以手动粘贴字幕文本用于AI分析。"
                    type="info"
                    show-icon
                    style="margin-bottom: 16px"
                  />
                  <a-textarea
                    v-model:value="subtitles"
                    placeholder="字幕文本内容...\n\n如果没有自动字幕，您可以：\n1. 手动粘贴字幕文本\n2. 点击'AI智能总结'按钮，系统会尝试提取字幕"
                    :rows="16"
                  />
                </div>
                <div class="subtitle-actions">
                  <a-button @click="handleExportSubtitle('srt')">
                    <DownloadOutlined /> 导出 SRT
                  </a-button>
                  <a-button @click="handleExportSubtitle('vtt')">
                    <DownloadOutlined /> 导出 VTT
                  </a-button>
                  <a-button @click="handleExportSubtitle('txt')">
                    <DownloadOutlined /> 导出 TXT
                  </a-button>
                </div>
              </a-tab-pane>

              <!-- 思维导图 Tab -->
              <a-tab-pane key="mindmap" tab="🧠 思维导图">
                <div class="tab-content mindmap-container">
                  <div v-if="!mindmapData" class="empty-state">
                    <ApartmentOutlined style="font-size: 48px; color: #d9d9d9" />
                    <p>思维导图将在总结完成后自动生成</p>
                  </div>
                  <div v-else ref="mindmapContainer" class="mindmap-view"></div>
                </div>
                <div v-if="mindmapData" class="mindmap-actions">
                  <a-button @click="handleFullscreen">
                    <FullscreenOutlined /> 全屏展示
                  </a-button>
                  <a-button @click="handleExportMindmap('png')">
                    <DownloadOutlined /> 导出 PNG
                  </a-button>
                  <a-button @click="handleExportMindmap('svg')">
                    <DownloadOutlined /> 导出 SVG
                  </a-button>
                </div>
              </a-tab-pane>


            </a-tabs>
          </a-card>
        </a-col>
      </a-row>
    </section>

    <!-- Analysis Section -->
    <section v-if="videoInfo" class="analysis-section">
      <h2 class="section-title">AI 视频分析</h2>
      <VideoAnalysis :video-url="videoUrl" :video-info="videoInfo" />
    </section>



    <!-- 全屏思维导图 -->
    <a-modal
      v-model:visible="fullscreenVisible"
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
import { ref, onMounted, computed, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import {
  LinkOutlined,
  VideoCameraOutlined,
  UserOutlined,
  EyeOutlined,
  DownloadOutlined,
  CheckCircleFilled,
  SoundOutlined,
  RobotOutlined,
  ApartmentOutlined,
  FullscreenOutlined,
  SettingOutlined
} from '@ant-design/icons-vue'
import { parseVideo, getDirectUrl, proxyDownload } from '@/services/video'
import type { VideoInfo } from '@/services/video'
import { summarizeVideoStream, generateMindmap, type MindmapData } from '@/services/summaries'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'

// 状态
const videoUrl = ref('')
const loading = ref(false)
const gettingDirectUrl = ref(false)
const videoInfo = ref<VideoInfo | null>(null)
const selectedFormat = ref('')
const subtitles = ref('')

// Tab 和 AI 分析相关状态
const activeTab = ref('summary')
const summarizing = ref(false)
const summary = ref('')
const mindmapData = ref<MindmapData | null>(null)
const fullscreenVisible = ref(false)

// Refs
const mindmapContainer = ref<HTMLElement | null>(null)
const fullscreenContainer = ref<HTMLElement | null>(null)

// 计算属性：是否可以解析
const canParse = computed(() => {
  return videoUrl.value.trim().length > 0 && !loading.value
})

// 特性卡片
const features = [
  {
    icon: 'global',
    title: '支持 1800+ 平台',
    description: 'YouTube、Bilibili、抖音、TikTok、Twitter、Instagram 等全球主流平台',
    color: 'rgba(24, 144, 255, 0.1)'
  },
  {
    icon: 'thunderbolt',
    title: '极速解析下载',
    description: '智能解析视频链接，自动匹配最优下载方式，速度快人一步',
    color: 'rgba(250, 173, 20, 0.1)'
  },
  {
    icon: 'mobile',
    title: '手机也能用',
    description: '完美适配手机浏览器，随时随地，想下就下，无需安装任何 App',
    color: 'rgba(82, 196, 26, 0.1)'
  },
  {
    icon: 'video',
    title: '多种清晰度',
    description: '支持从 360p 到 4K 多种清晰度选择，满足不同场景需求',
    color: 'rgba(114, 46, 209, 0.1)'
  },
  {
    icon: 'robot',
    title: 'AI 视频总结',
    description: 'AI 智能分析视频内容，一键生成摘要、思维导图，还能针对视频提问',
    color: 'rgba(255, 77, 79, 0.1)'
  },
]

// 解析视频
async function handleParse() {
  if (!videoUrl.value.trim()) {
    message.warning('请输入视频链接')
    return
  }

  loading.value = true
  try {
    const info = await parseVideo(videoUrl.value.trim())
    videoInfo.value = info
    selectedFormat.value = info.formats?.length > 0 ? info.formats[0].format_id : ''
    
    // 如果有字幕，自动填充
    if (info.subtitles && info.subtitles.length > 0) {
      subtitles.value = info.subtitles.join('\n')
    } else if (info.automatic_captions && info.automatic_captions.length > 0) {
      subtitles.value = info.automatic_captions.join('\n')
    }
    
    message.success('解析成功')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '解析失败，请检查链接是否正确')
  } finally {
    loading.value = false
  }
}

// 获取直链下载
async function handleDirectDownload() {
  if (!selectedFormat.value || !videoInfo.value) {
    message.warning('请选择视频格式')
    return
  }

  gettingDirectUrl.value = true
  try {
    // 使用代理下载（通过后端转发，避免CORS和HTTP头问题）
    const { blob, filename } = await proxyDownload(
      videoUrl.value.trim(), 
      selectedFormat.value
    )
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    
    // 清理
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    
    message.success(`已开始下载: ${filename}`)
  } catch (error: any) {
    message.error(error.message || '下载失败，请检查链接或稍后重试')
    console.error('下载错误:', error)
  } finally {
    gettingDirectUrl.value = false
  }
}

// 格式化观看次数
function formatViewCount(count: number): string {
  if (!count) return ''
  if (count >= 100000000) return (count / 100000000).toFixed(1) + '亿'
  if (count >= 10000) return (count / 10000).toFixed(1) + '万'
  return count.toLocaleString()
}

// 格式化时长
function formatDuration(seconds: number): string {
  if (!seconds) return ''
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// 获取格式颜色
function getFormatColor(format: any): string {
  if (format.ext === 'mp4') {
    return 'rgba(24, 144, 255, 0.1)'
  } else if (format.ext === 'webm') {
    return 'rgba(82, 196, 26, 0.1)'
  } else if (format.ext === 'mkv') {
    return 'rgba(114, 46, 209, 0.1)'
  } else if (format.ext === 'mp3' || format.ext === 'm4a') {
    return 'rgba(250, 173, 20, 0.1)'
  }
  return 'rgba(140, 140, 140, 0.1)'
}

// 格式化文件大小
function formatFileSize(bytes: number): string {
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(0)}KB`
  }
  if (bytes < 1024 * 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
  }
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)}GB`
}

// 格式化时间
function formatTime(timestamp: number): string {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取选中格式的标签
function getSelectedLabel(): string {
  const fmt = videoInfo.value?.formats?.find(f => f.format_id === selectedFormat.value)
  return fmt?.label || ''
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

// AI 智能总结
async function handleSummarize() {
  if (!videoInfo.value) {
    message.warning('请先解析视频')
    return
  }

  summarizing.value = true
  summary.value = ''
  mindmapData.value = null

  try {
    await summarizeVideoStream(
      {
        video_title: videoInfo.value.title,
        subtitles: subtitles.value || '暂无字幕'
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
      downloadBlob(blob, `mindmap-${videoInfo.value?.title}.svg`)
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
            downloadBlob(blob, `mindmap-${videoInfo.value?.title}.png`)
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
  if (!subtitles.value) {
    message.warning('暂无字幕可导出')
    return
  }

  let content = subtitles.value
  let filename = `subtitles-${videoInfo.value?.title}.${format}`

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

// 计算属性：渲染后的总结内容
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

// 组件挂载
onMounted(() => {
})
</script>

<style scoped>
.video-download-page {
  min-height: 100vh;
  background: #ffffff;
}

/* Hero Section */
.hero-section {
  padding: 64px 24px 48px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #ffffff;
  border: 1px solid #d9d9d9;
  border-radius: 20px;
  font-size: 14px;
  color: #595959;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 16px;
  line-height: 1.2;
}

.hero-title .highlight {
  color: #1890ff;
}

.hero-description {
  font-size: 18px;
  color: #8c8c8c;
  max-width: 600px;
  margin: 0 auto 40px;
  line-height: 1.6;
}

/* Search Container */
.search-container {
  display: flex;
  gap: 0;
  max-width: 700px;
  margin: 0 auto 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-radius: 24px;
  overflow: hidden;
}

.search-input {
  flex: 1;
  border-radius: 24px 0 0 24px !important;
  border: 1px solid #d9d9d9 !important;
  border-right: none !important;
}

.search-input >>> .ant-input {
  font-size: 16px;
  border-radius: 24px 0 0 24px !important;
}

.search-button {
  border-radius: 0 24px 24px 0 !important;
  height: 56px;
  padding: 0 32px;
  font-size: 16px;
  font-weight: 500;
}

/* Features Section */
.features-section {
  padding: 48px 24px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.features-header {
  text-align: center;
  margin-bottom: 40px;
}

.features-title {
  font-size: 32px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 12px;
}

.features-title .highlight {
  color: #1890ff;
}

.features-subtitle {
  font-size: 16px;
  color: #8c8c8c;
  margin: 0;
}

.features-grid {
  max-width: 1200px;
  margin: 0 auto;
}

.features-grid >>> .ant-row {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
}

.feature-card {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  height: 100%;
  text-align: center;
  padding: 24px 16px;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.feature-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  transition: all 0.3s;
}

.feature-card:hover .feature-icon-wrapper {
  transform: scale(1.1);
}

.feature-icon {
  font-size: 32px;
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px;
}

.feature-description {
  font-size: 14px;
  color: #8c8c8c;
  line-height: 1.6;
  margin: 0;
}

/* Result Section */
.result-section {
  padding: 48px 24px;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
}

.result-card {
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 1200px;
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
  padding: 0 8px;
}

.video-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #595959;
}

.video-description {
  font-size: 14px;
  color: #8c8c8c;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Format List */
.format-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.format-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.format-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.format-item:hover {
  border-color: #1890ff;
  background: #f0f5ff;
}

.format-item-active {
  border-color: #1890ff;
  background: #e6f7ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.format-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.format-item-active .format-icon {
  color: #1890ff;
}

.format-info {
  flex: 1;
  min-width: 0;
}

.format-label {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.format-detail {
  font-size: 12px;
  color: #8c8c8c;
}

/* Download Actions */
.download-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.download-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 24px;
}

.selected-alert {
  border-radius: 8px;
}

/* Analysis Section */
.analysis-section {
  padding: 48px 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 24px;
  text-align: center;
}

/* Tab Content */
.tab-content {
  min-height: 400px;
  margin-bottom: 16px;
}

.summary-content {
  line-height: 1.8;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
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

.analyze-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.subtitle-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
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

/* Mobile Responsive */
@media (max-width: 768px) {
  .hero-section {
    padding: 40px 16px 32px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-description {
    font-size: 15px;
  }

  .search-container {
    flex-direction: column;
    border-radius: 16px;
  }

  .search-input {
    border-radius: 16px 16px 0 0 !important;
    border-right: 1px solid #d9d9d9 !important;
    border-bottom: none !important;
  }

  .search-input >>> .ant-input {
    border-radius: 16px 16px 0 0 !important;
  }

  .search-button {
    border-radius: 0 0 16px 16px !important;
    height: 48px;
  }

  .features-section {
    padding: 32px 16px;
  }

  .features-title {
    font-size: 24px;
  }

  .result-section {
    padding: 32px 16px;
  }

  .format-list {
    max-height: 300px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 28px;
  }

  .hero-description {
    font-size: 14px;
  }

  .status-badge {
    font-size: 12px;
    padding: 6px 12px;
  }
}
</style>
