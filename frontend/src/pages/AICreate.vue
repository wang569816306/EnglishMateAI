<template>
  <div class="speaking-container">
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title">口语训练</h1>
          <p class="page-description">上传文档，AI生成对话，逐句跟读练习</p>
        </div>
        <a-button 
          type="primary" 
          @click="showSavedWordsModal"
          class="saved-words-btn"
        >
          <template #icon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
          </template>
          我的收藏 ({{ savedWords.length }})
        </a-button>
      </div>
    </div>
    
    <!-- 文件上传区域 -->
    <div class="upload-section" v-if="!currentScenario">
      <!-- Tab切换 -->
      <div class="tab-header">
        <a-tabs v-model:activeKey="activeTab" type="card">
          <a-tab-pane key="upload" tab="📄 上传文档">
            <div class="upload-content">
              <a-upload
                :before-upload="handleBeforeUpload"
                :custom-request="handleUpload"
                :show-upload-list="false"
                accept=".doc,.docx,.xls,.xlsx"
                :disabled="uploading"
              >
                <a-button type="primary" :loading="uploading" class="upload-btn">
                  <template #icon>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                  </template>
                  {{ uploading ? '上传中...' : '上传 Word/Excel 文档' }}
                </a-button>
              </a-upload>
              
              <div class="upload-hint">
                <p>支持格式：Word (.doc, .docx)、Excel (.xls, .xlsx)</p>
                <p>文件大小限制：10MB</p>
              </div>
            </div>
          </a-tab-pane>
          
          <a-tab-pane key="quick" tab="⚡ 快速生成">
            <div class="quick-generate-content">
              <h3 class="section-title">输入主题，AI立即生成对话</h3>
              <a-textarea
                v-model:value="quickTopic"
                placeholder="例如：餐厅点餐、机场值机、商务会议、医院就诊..."
                :rows="4"
                :maxlength="200"
                show-count
                class="topic-input"
              />
              <div class="quick-actions">
                <a-button 
                  type="primary" 
                  @click="handleQuickGenerate"
                  :loading="generating"
                  class="generate-btn"
                >
                  <template #icon>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                    </svg>
                  </template>
                  {{ generating ? '生成中...' : '生成双人对话' }}
                </a-button>
              </div>
              <div class="quick-hint">
                <p>💡 提示：输入具体的场景或主题，AI会生成相关的实用对话</p>
              </div>
            </div>
          </a-tab-pane>
        </a-tabs>
      </div>
    </div>

    <!-- 场景库列表 -->
    <div class="scenario-list" v-if="!currentDialogue && !generating">
      <a-empty 
        v-if="scenarios.length === 0"
        description="暂无口语训练记录"
        :image="simpleImage"
      >
        <template #description>
          <p style="color: var(--color-text-secondary); font-size: 14px;">
            上传文档或输入主题生成对话，开始你的口语练习之旅
          </p>
        </template>
      </a-empty>
      
      <div v-else>
        <div class="list-header">
          <h2 class="list-title">我的场景库</h2>
        </div>
        
        <div class="scenario-items">
          <div 
            v-for="scenario in scenarios" 
            :key="scenario.id"
            class="scenario-card"
          >
            <div class="scenario-info">
              <div class="scenario-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <div class="scenario-detail">
                <h3 class="scenario-name">{{ scenario.title }}</h3>
                <p class="scenario-meta">{{ scenario.file_name }} • {{ formatDate(scenario.created_at) }}</p>
              </div>
            </div>
            <div class="scenario-actions">
              <a-button type="primary" size="small" @click="generateDialogue(scenario.id, scenario.title)">
                <template #icon>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                </template>
                生成对话
              </a-button>
              <a-button size="small" @click="deleteScenario(scenario.id)">
                <template #icon>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </template>
                删除
              </a-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 对话生成中 -->
    <div v-if="generating" class="generating-state">
      <a-spin size="large" />
      <p>AI正在生成对话，请稍候...</p>
    </div>

    <!-- 对话展示和跟读 -->
    <div v-if="currentDialogue && !generating" class="dialogue-section">
      <!-- 第一行：标题和返回按钮 -->
      <div class="dialogue-header">
        <div>
          <h2 class="dialogue-title">{{ currentDialogue.title }}</h2>
          <p class="dialogue-subtitle">逐句跟读练习</p>
        </div>
        <a-button @click="backToScenarios">
          <template #icon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </template>
          返回场景库
        </a-button>
      </div>

      <!-- 第二行：功能控件 -->
      <div class="dialogue-controls">
        <!-- 全局翻译模式 -->
        <div class="global-translation-mode">
          <span class="toggle-label">📝 翻译模式：</span>
          <a-select 
            v-model:value="translationMode" 
            size="small"
            style="width: 120px;"
          >
            <a-select-option value="both">中英对照</a-select-option>
            <a-select-option value="en">只显示英文</a-select-option>
            <a-select-option value="zh">只显示中文</a-select-option>
          </a-select>
        </div>
        <!-- 角色语音开关 -->
        <div class="role-voice-toggle">
          <span class="toggle-label">🎭 双人对话：</span>
          <a-switch 
            v-model:checked="useRoleVoices" 
            checked-children="开启" 
            un-checked-children="关闭"
            size="small"
          />
          <span v-if="useRoleVoices" class="toggle-hint">(A=男声 B=女声)</span>
        </div>
        <!-- 语音选择 -->
        <div class="voice-selector" v-if="availableVoices.length > 0 && !useRoleVoices">
          <span class="selector-label">🎤 选择声音：</span>
          <a-select 
            v-model:value="selectedVoiceName" 
            class="voice-select"
            size="small"
            @change="handleVoiceChange"
          >
            <a-select-option 
              v-for="voice in availableVoices" 
              :key="voice.id" 
              :value="voice.id"
            >
              {{ voice.name }}
            </a-select-option>
          </a-select>
        </div>
        <!-- 连读开关 -->
        <div class="continuous-play-toggle">
          <span class="toggle-label"> 连读：</span>
          <a-switch 
            v-model:checked="continuousPlay" 
            checked-children="开启" 
            un-checked-children="关闭"
            size="small"
          />
          <a-button 
            v-if="continuousPlay && currentDialogue" 
            size="small"
            type="primary"
            :loading="isContinuousPlaying"
            @click="toggleContinuousPlay"
          >
            <template #icon>
              <svg v-if="!isContinuousPlaying" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
              </svg>
            </template>
            {{ isContinuousPlaying ? '停止' : '从头播放' }}
          </a-button>
        </div>
      </div>

      <div class="dialogue-list" :class="{ 'continuous-playing': isContinuousPlaying }">
        <div 
          v-for="(line, index) in currentDialogue.dialogue_data" 
          :key="index"
          class="dialogue-line"
          :class="{ 
            'has-score': pronunciationScores[index],
            'is-playing': playingIndex === index && isContinuousPlaying
          }"
        >
          <!-- 分数徽章 -->
          <div 
            v-if="pronunciationScores[index]" 
            class="score-badge"
            :class="getScoreBadgeClass(pronunciationScores[index].overall_score)"
          >
            <span class="score-badge-number">{{ pronunciationScores[index].overall_score }}</span>
          </div>

          <div class="line-header">
            <span class="speaker-badge" :class="line.speaker.toLowerCase()">
              {{ line.speaker }}
            </span>
            <!-- 练习次数 -->
            <span v-if="pronunciationScores[index]" class="practice-count">
              已练{{ getPracticeCount(index) }}次
            </span>
          </div>
          
          <div class="line-content">
            <p class="english-text" v-if="getLineTranslationMode(index) === 'en' || getLineTranslationMode(index) === 'both'">
              <span 
                v-for="(word, wordIndex) in parseWords(line.text)" 
                :key="wordIndex"
                class="clickable-word"
                :class="getWordScoreClass(index, wordIndex)"
                @click="showWordTranslation(word, $event)"
              >{{ word }} </span>
            </p>
            <p class="chinese-text" v-if="getLineTranslationMode(index) === 'zh' || getLineTranslationMode(index) === 'both'">{{ line.translation }}</p>
          </div>

          <!-- 评分摘要栏 -->
          <div v-if="pronunciationScores[index]" class="score-summary">
            <div class="score-summary-item">
              <span class="score-summary-label">总分</span>
              <span class="score-summary-value" :class="getScoreColorClass(pronunciationScores[index].overall_score)">
                {{ pronunciationScores[index].overall_score }}分
              </span>
            </div>
            <div class="score-summary-divider"></div>
            <div class="score-summary-item">
              <span class="score-summary-label">流畅度</span>
              <span class="score-summary-value">{{ pronunciationScores[index].fluency }}</span>
            </div>
            <div class="score-summary-divider"></div>
            <div class="score-summary-item">
              <span class="score-summary-label">准确度</span>
              <span class="score-summary-value">{{ pronunciationScores[index].accuracy }}</span>
            </div>
            <div class="score-summary-divider"></div>
            <div class="score-summary-item">
              <span class="score-summary-label">完整度</span>
              <span class="score-summary-value">{{ pronunciationScores[index].completeness }}</span>
            </div>
            <div class="score-summary-arrow">></div>
          </div>

          <div class="line-actions">
            <!-- 播放按钮 -->
            <a-button 
              size="small" 
              @click="playText(line.text, index, line.speaker)"
              :loading="playingIndex === index"
            >
              <template #icon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
              </template>
              播放
            </a-button>

            <!-- 录音按钮 -->
            <a-button 
              size="small"
              :type="recordingIndex === index ? 'primary' : 'default'"
              @click="toggleRecording(index)"
            >
              <template #icon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                  <line x1="8" y1="23" x2="16" y2="23"/>
                </svg>
              </template>
              {{ recordingIndex === index ? '停止' : '录音' }}
            </a-button>

            <!-- 翻译模式下拉框（只对当前对话生效） -->
            <a-select 
              v-model:value="lineTranslationModes[index]" 
              size="small"
              style="textAlign:center;"
            >
              <a-select-option value="default">默认</a-select-option>
              <a-select-option value="both">中英对照</a-select-option>
              <a-select-option value="en">只显示英文</a-select-option>
              <a-select-option value="zh">只显示中文</a-select-option>
            </a-select>

            <!-- 播放录音 -->
            <a-button 
              v-if="recordings[index]"
              size="small"
              @click="playRecording(index)"
              :loading="playingRecordingIndex === index"
            >
              <template #icon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
              </template>
              回放
            </a-button>

            <!-- 评分按钮 -->
            <a-button 
              v-if="recordings[index]"
              size="small"
              type="primary"
              @click="evaluatePronunciation(index)"
              :loading="evaluatingIndex === index"
            >
              <template #icon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </template>
              {{ pronunciationScores[index] ? '查看评分' : '评分' }}
            </a-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-progress">
      <a-progress :percent="uploadProgress" status="active" />
    </div>
  </div>

  <!-- 悬浮翻译框 -->
  <div 
    v-if="showTranslationPopup"
    class="word-translation-popup"
    :style="{ top: popupPosition.top + 'px', left: popupPosition.left + 'px' }"
  >
    <div class="popup-header">
      <h3 class="popup-word">{{ currentWord }}</h3>
      <a-button 
        type="text" 
        size="small" 
        @click="playWord(currentWord)"
        class="play-word-btn"
      >
        <template #icon>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
        </template>
      </a-button>
      <a-button 
        type="text" 
        size="small" 
        @click="closeTranslationPopup"
        class="close-btn"
      >
        ✕
      </a-button>
    </div>
    
    <div class="popup-content" v-if="wordTranslation">
      <div class="translation-item" v-if="wordTranslation.phonetic">
        <span class="label">发音：</span>
        <span class="value">{{ wordTranslation.phonetic }}</span>
      </div>
      
      <div class="translation-item" v-if="wordTranslation.pos">
        <span class="label">词性：</span>
        <span class="value">{{ wordTranslation.pos }}</span>
      </div>
      
      <div class="translation-item" v-if="wordTranslation.translation">
        <span class="label">翻译：</span>
        <span class="value">{{ wordTranslation.translation }}</span>
      </div>
      
      <div class="translation-item" v-if="wordTranslation.example">
        <span class="label">例句：</span>
        <span class="value">{{ wordTranslation.example }}</span>
      </div>

      <!-- 阶段2：单词收藏按钮 -->
      <div class="popup-actions">
        <a-button 
          size="small" 
          :type="isWordSaved(currentWord) ? 'primary' : 'default'"
          @click="toggleSaveWord(currentWord)"
        >
          <template #icon>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
          </template>
          {{ isWordSaved(currentWord) ? '已收藏' : '收藏' }}
        </a-button>
      </div>
    </div>
    
    <div class="popup-loading" v-else>
      <a-spin size="small" />
      <span>查询中...</span>
    </div>
  </div>

  <!-- 收藏单词列表弹窗 -->
  <div 
    v-if="showSavedWordsList"
    class="saved-words-modal-overlay"
    @click="closeSavedWordsModal"
  >
    <div 
      class="saved-words-modal"
      @click.stop
    >
      <div class="modal-header">
        <h2 class="modal-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
          </svg>
          我的收藏单词
        </h2>
        <a-button 
          type="text" 
          size="small" 
          @click="closeSavedWordsModal"
          class="modal-close-btn"
        >
          ✕
        </a-button>
      </div>
      
      <div class="modal-body">
        <div v-if="savedWords.length === 0" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
          </svg>
          <p>暂无收藏的单词</p>
          <p class="empty-hint">点击对话中的单词，然后点击“收藏”按钮即可添加</p>
        </div>
        
        <div v-else class="words-list">
          <div 
            v-for="(word, index) in savedWords" 
            :key="index"
            class="word-item"
          >
            <div class="word-info">
              <h3 class="word-text">{{ word }}</h3>
              <div class="word-actions-inline">
                <a-button 
                  type="text" 
                  size="small"
                  @click="playWord(word)"
                  class="inline-action-btn"
                  title="播放发音"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                </a-button>
                <a-button 
                  type="text" 
                  size="small"
                  @click="removeSavedWord(word)"
                  class="inline-action-btn delete-btn"
                  title="删除收藏"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </a-button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer" v-if="savedWords.length > 0">
        <a-button 
          danger
          @click="clearAllSavedWords"
        >
          <template #icon>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </template>
          清空全部
        </a-button>
        <span class="total-count">共 {{ savedWords.length }} 个单词</span>
      </div>
    </div>
  </div>

  <!-- 发音评分结果弹窗 -->
  <div 
    v-if="showScoreModal && currentScoreIndex !== null"
    class="score-modal-overlay"
    @click="closeScoreModal"
  >
    <div 
      class="score-modal"
      @click.stop
    >
      <div class="modal-header">
        <h2 class="modal-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
          发音评分报告
        </h2>
        <a-button 
          type="text" 
          size="small" 
          @click="closeScoreModal"
          class="modal-close-btn"
        >
          ✕
        </a-button>
      </div>
      
      <div class="modal-body">
        <!-- 总体评分 -->
        <div class="overall-score">
          <div class="score-circle" :style="{ borderColor: getScoreColor(pronunciationScores[currentScoreIndex]?.overall_score || 0) }">
            <span class="score-number" :style="{ color: getScoreColor(pronunciationScores[currentScoreIndex]?.overall_score || 0) }">
              {{ pronunciationScores[currentScoreIndex]?.overall_score || 0 }}
            </span>
          </div>
          <div class="score-details">
            <div class="score-item">
              <span class="score-label">准确度</span>
              <span class="score-value" :style="{ color: getScoreColor(pronunciationScores[currentScoreIndex]?.accuracy || 0) }">
                {{ pronunciationScores[currentScoreIndex]?.accuracy || 0 }}%
              </span>
            </div>
            <div class="score-item">
              <span class="score-label">流利度</span>
              <span class="score-value" :style="{ color: getScoreColor(pronunciationScores[currentScoreIndex]?.fluency || 0) }">
                {{ pronunciationScores[currentScoreIndex]?.fluency || 0 }}%
              </span>
            </div>
            <div class="score-item">
              <span class="score-label">完整度</span>
              <span class="score-value" :style="{ color: getScoreColor(pronunciationScores[currentScoreIndex]?.completeness || 0) }">
                {{ pronunciationScores[currentScoreIndex]?.completeness || 0 }}%
              </span>
            </div>
          </div>
        </div>

        <!-- 逐词评分 -->
        <div class="word-evaluation">
          <h3 class="section-title-small">逐词分析</h3>
          <div class="words-container">
            <div 
              v-for="(wordDetail, idx) in pronunciationScores[currentScoreIndex]?.word_details || []" 
              :key="idx"
              class="word-eval-item"
              :class="getWordColorClass(wordDetail.status)"
            >
              <span class="eval-word">{{ wordDetail.word }}</span>
              <span class="eval-score" :style="{ color: getScoreColor(wordDetail.score) }">
                {{ wordDetail.score }}%
              </span>
              <div class="eval-status" v-if="wordDetail.status === 'wrong' && wordDetail.recognized">
                <small>识别为: {{ wordDetail.recognized }}</small>
              </div>
            </div>
          </div>
        </div>

        <!-- 图例说明 -->
        <div class="legend">
          <div class="legend-item">
            <span class="legend-color word-correct"></span>
            <span>正确</span>
          </div>
          <div class="legend-item">
            <span class="legend-color word-wrong"></span>
            <span>读错</span>
          </div>
          <div class="legend-item">
            <span class="legend-color word-missing"></span>
            <span>漏读</span>
          </div>
          <div class="legend-item">
            <span class="legend-color word-extra"></span>
            <span>多读</span>
          </div>
        </div>

        <!-- 识别文本对比 -->
        <div class="recognition-result">
          <h3 class="section-title-small">识别结果</h3>
          <div class="result-text">
            <p><strong>原文：</strong>{{ pronunciationScores[currentScoreIndex]?.original_text }}</p>
            <p><strong>识别：</strong>{{ pronunciationScores[currentScoreIndex]?.recognized_text }}</p>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <a-button type="primary" @click="closeScoreModal">
          确定
        </a-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Select } from 'ant-design-vue'
import { Empty } from 'ant-design-vue'
import apiClient from '../utils/api'
import { isAuthenticated } from '../services/auth'

const route = useRoute()
const router = useRouter()

const simpleImage = Empty.PRESENTED_IMAGE_SIMPLE
const { Option } = Select

interface Scenario {
  id: number
  title: string
  file_name: string
  file_type: string
  created_at: string
}

interface DialogueLine {
  speaker: string
  text: string
  translation: string
}

interface Dialogue {
  id: number
  title: string
  dialogue_data: DialogueLine[]
  created_at: string
}

const uploading = ref(false)
const uploadProgress = ref(0)
const activeTab = ref('upload')
const quickTopic = ref('')
const scenarios = ref<Scenario[]>([])
const generating = ref(false)
const currentDialogue = ref<Dialogue | null>(null)
const playingIndex = ref<number | null>(null)
const recordingIndex = ref<number | null>(null)
const playingRecordingIndex = ref<number | null>(null)
const recordings = ref<Record<number, Blob>>({})

// 评分相关
interface WordScore {
  word: string
  score: number
  status: 'correct' | 'wrong' | 'missing' | 'extra'
  recognized?: string
}

interface PronunciationScore {
  overall_score: number
  accuracy: number
  fluency: number
  completeness: number
  word_details: WordScore[]
  recognized_text: string
  original_text: string
}

const evaluatingIndex = ref<number | null>(null)
const pronunciationScores = ref<Record<number, PronunciationScore>>({})
const showScoreModal = ref(false)
const currentScoreIndex = ref<number | null>(null)

// 防止重复加载的标志
const isLoadingDialogue = ref(false)
const lastLoadedDialogueId = ref<string | null>(null)

// 语音相关
const availableVoices = ref<Array<{id: string, name: string}>>([])
const selectedVoiceName = ref<string>('en-US-AriaNeural')  // 默认使用 Aria
const playingAudio = ref<HTMLAudioElement | null>(null)

// 音频缓存相关（使用 IndexedDB，浏览器关闭后自动清除）
const DB_NAME = 'EnglishMateAudioCache'
const DB_VERSION = 1
const STORE_NAME = 'audioCache'
let db: IDBDatabase | null = null
const audioCache = new Map<string, string>()  // 内存缓存：key -> base64音频数据

// 初始化 IndexedDB
const initAudioDB = async (): Promise<void> => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    
    request.onerror = () => {
      console.error('❌ IndexedDB 打开失败:', request.error)
      reject(request.error)
    }
    
    request.onsuccess = () => {
      db = request.result
      console.log('✅ IndexedDB 初始化成功')
      
      // 浏览器关闭时清除缓存
      window.addEventListener('beforeunload', async () => {
        await clearAudioCache()
      })
      
      resolve()
    }
    
    request.onupgradeneeded = (event: any) => {
      const database = event.target.result
      if (!database.objectStoreNames.contains(STORE_NAME)) {
        database.createObjectStore(STORE_NAME)
        console.log('✅ IndexedDB 创建对象存储成功')
      }
    }
  })
}

// 对话角色语音开关
const useRoleVoices = ref(false)  // 是否启用角色语音（A男声B女声）
const maleVoice = ref<string>('en-US-GuyNeural')  // 男声默认：Guy
const femaleVoice = ref<string>('en-US-AriaNeural')  // 女声默认：Aria

// 连读相关
const continuousPlay = ref(false)  // 是否启用连读模式
const isContinuousPlaying = ref(false)  // 是否正在连读播放
const continuousPlayIndex = ref<number>(0)  // 当前播放的索引
let continuousPlayTimer: any = null  // 连读定时器

// 切换连读播放
const toggleContinuousPlay = async () => {
  if (isContinuousPlaying.value) {
    // 停止播放
    stopContinuousPlay()
  } else {
    // 开始播放
    await startContinuousPlay()
  }
}

// 开始连读播放
const startContinuousPlay = async () => {
  if (!currentDialogue.value || !currentDialogue.value.dialogue_data) {
    message.warning('没有可播放的对话')
    return
  }

  isContinuousPlaying.value = true
  continuousPlayIndex.value = 0
  console.log('▶️ 开始连读播放')
  
  // 播放第一句
  await playContinuousLine(0)
}

// 播放连读中的某一句
const playContinuousLine = async (index: number) => {
  if (!currentDialogue.value || !currentDialogue.value.dialogue_data) {
    stopContinuousPlay()
    return
  }

  if (index >= currentDialogue.value.dialogue_data.length) {
    // 播放完成
    console.log('✅ 连读播放完成')
    stopContinuousPlay()
    message.success('整段对话播放完成')
    return
  }

  if (!isContinuousPlaying.value) {
    return  // 用户手动停止了
  }

  const line = currentDialogue.value.dialogue_data[index]
  continuousPlayIndex.value = index
  
  console.log(`▶️ 连读播放第 ${index + 1} 句`)
  
  // 高亮当前正在播放的句子
  playingIndex.value = index
  
  try {
    // 根据角色选择语音
    const voiceToUse = line.speaker ? getVoiceForSpeaker(line.speaker) : selectedVoiceName.value
    
    // 调用后端 TTS API
    const response = await apiClient.post('/tts/synthesize-base64', {
      text: line.text,
      voice: voiceToUse,
      rate: '+0%',
      pitch: '+0Hz'
    })
    
    // 将 base64 转换为音频并播放
    const audioData = `data:audio/mp3;base64,${response.audio}`
    const audio = new Audio(audioData)
    playingAudio.value = audio
    
    // 等待播放完成
    await new Promise<void>((resolve, reject) => {
      audio.onended = () => {
        console.log(`⏹️ 第 ${index + 1} 句播放完成`)
        resolve()
      }
      
      audio.onerror = () => {
        console.error(`❌ 第 ${index + 1} 句播放失败`)
        reject(new Error('播放失败'))
      }
      
      audio.play()
    })
    
    // 播放下一句（间隔 500ms）
    if (isContinuousPlaying.value) {
      continuousPlayTimer = setTimeout(() => {
        playContinuousLine(index + 1)
      }, 500)
    }
    
  } catch (error: any) {
    console.error('❌ 连读播放失败:', error)
    message.error(error.message || '播放失败')
    stopContinuousPlay()
  }
}

// 停止连读播放
const stopContinuousPlay = () => {
  isContinuousPlaying.value = false
  playingIndex.value = null
  
  if (continuousPlayTimer) {
    clearTimeout(continuousPlayTimer)
    continuousPlayTimer = null
  }
  
  if (playingAudio.value) {
    playingAudio.value.pause()
    playingAudio.value = null
  }
  
  console.log('⏹️ 停止连读播放')
}

// 从缓存获取音频
const getCachedAudio = async (cacheKey: string): Promise<string | null> => {
  // 先检查内存缓存
  if (audioCache.has(cacheKey)) {
    console.log('💾 从内存缓存获取音频:', cacheKey)
    return audioCache.get(cacheKey)!
  }
  
  // 检查 IndexedDB
  if (!db) {
    console.warn('⚠️ IndexedDB 未初始化')
    return null
  }
  
  return new Promise((resolve, reject) => {
    const transaction = db!.transaction(STORE_NAME, 'readonly')
    const store = transaction.objectStore(STORE_NAME)
    const request = store.get(cacheKey)
    
    request.onsuccess = () => {
      if (request.result) {
        console.log(' 从 IndexedDB 获取音频:', cacheKey)
        // 同时放入内存缓存
        audioCache.set(cacheKey, request.result)
        resolve(request.result)
      } else {
        resolve(null)
      }
    }
    
    request.onerror = () => {
      console.error(' 从 IndexedDB 读取失败:', request.error)
      reject(request.error)
    }
  })
}

// 保存音频到缓存
const saveAudioToCache = async (cacheKey: string, audioBase64: string): Promise<void> => {
  // 先保存到内存缓存
  audioCache.set(cacheKey, audioBase64)
  
  // 保存到 IndexedDB
  if (!db) {
    console.warn('️ IndexedDB 未初始化')
    return
  }
  
  return new Promise((resolve, reject) => {
    const transaction = db!.transaction(STORE_NAME, 'readwrite')
    const store = transaction.objectStore(STORE_NAME)
    const request = store.put(audioBase64, cacheKey)
    
    request.onsuccess = () => {
      console.log(' 音频已缓存:', cacheKey)
      resolve()
    }
    
    request.onerror = () => {
      console.error('❌ 保存到 IndexedDB 失败:', request.error)
      reject(request.error)
    }
  })
}

// 清除所有缓存音频
const clearAudioCache = async (): Promise<void> => {
  if (!db) {
    console.log('⚠️ IndexedDB 未初始化，无需清除')
    return
  }
  
  return new Promise((resolve, reject) => {
    const transaction = db!.transaction(STORE_NAME, 'readwrite')
    const store = transaction.objectStore(STORE_NAME)
    const request = store.clear()
    
    request.onsuccess = () => {
      audioCache.clear()
      console.log('🗑️ 已清除所有音频缓存')
      resolve()
    }
    
    request.onerror = () => {
      console.error('❌ 清除缓存失败:', request.error)
      reject(request.error)
    }
  })
}

// 悬浮翻译相关
const showTranslationPopup = ref(false)
const currentWord = ref('')
const wordTranslation = ref<any>(null)
const popupPosition = ref({ top: 0, left: 0 })

// 翻译显示模式：'en' | 'zh' | 'both'
const translationMode = ref<'en' | 'zh' | 'both'>('both')  // 全局翻译模式，默认中英都显示

// 每条对话的独立翻译模式
const lineTranslationModes = ref<Record<number, 'en' | 'zh' | 'both'>>({})

// 获取某条对话的翻译模式（局部优先于全局）
const getLineTranslationMode = (index: number): 'en' | 'zh' | 'both' => {
  // 如果该条对话有独立设置且不是'default'，使用局部设置
  if (lineTranslationModes.value[index] && lineTranslationModes.value[index] !== 'default') {
    return lineTranslationModes.value[index]
  }
  // 否则使用全局设置
  return translationMode.value
}

// 设置某条对话的翻译模式
const setLineTranslationMode = (index: number, mode: 'en' | 'zh' | 'both') => {
  lineTranslationModes.value[index] = mode
  console.log(`🔄 设置第${index + 1}条对话翻译模式:`, mode)
}

// 阶段2：单词收藏
const savedWords = ref<string[]>([])
const showSavedWordsList = ref(false)

let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []

// 解析单词（按空格分割）
const parseWords = (text: string): string[] => {
  const words = text.split(/\s+/).filter(w => w.length > 0)
  console.log('📝 解析单词:', words)
  return words
}

// 显示单词翻译
const showWordTranslation = async (word: string, event: MouseEvent) => {
  // 阻止事件冒泡，避免触发全局点击关闭
  event.stopPropagation()
  
  // 清除标点符号
  const cleanWord = word.replace(/[^a-zA-Z'-]/g, '')
  if (!cleanWord || cleanWord.length < 2) return
  
  currentWord.value = cleanWord
  wordTranslation.value = null
  showTranslationPopup.value = true
  
  // 计算悬浮框位置 - 使用更可靠的定位方式
  const target = event.target as HTMLElement
  const rect = target.getBoundingClientRect()
  
  // 获取视口尺寸
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  
  // 计算位置，确保不超出视口
  let left = rect.left + (rect.width / 2) - 140 // 居中显示，假设宽度280px
  let top = rect.bottom + 10
  
  // 边界检查 - 左右
  if (left < 10) left = 10
  if (left + 280 > viewportWidth) left = viewportWidth - 290
  
  // 边界检查 - 上下（如果下方空间不足，显示在上方）
  if (top + 300 > viewportHeight) {
    top = rect.top - 310
  }
  
  popupPosition.value = {
    top: top + window.scrollY,
    left: left + window.scrollX
  }
  
  console.log('📍 显示翻译卡片:', cleanWord, '位置:', popupPosition.value)
  
  // 调用翻译 API
  await fetchWordTranslation(cleanWord)
}

// 获取单词翻译（阶段1: 使用 MyMemory API）
const fetchWordTranslation = async (word: string) => {
  try {
    console.log('🔍 查询单词翻译:', word)
    
    // 使用 MyMemory API (免费，无需密钥)
    const response = await fetch(
      `https://api.mymemory.translated.net/get?q=${encodeURIComponent(word)}&langpair=en|zh`
    )
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('✅ 翻译API响应:', data)
    
    if (data.responseStatus === 200 && data.responseData?.translatedText) {
      wordTranslation.value = {
        word: word,
        phonetic: '',  // MyMemory 不提供音标
        pos: '',       // MyMemory 不提供词性
        translation: data.responseData.translatedText,
        example: data.matches?.[0]?.segment || ''
      }
      console.log('✅ 翻译成功:', wordTranslation.value)
    } else {
      console.warn('⚠️ 翻译API返回异常:', data)
      wordTranslation.value = {
        word: word,
        translation: '暂无翻译',
        phonetic: '',
        pos: '',
        example: ''
      }
    }
  } catch (error) {
    console.error('❌ 翻译失败:', error)
    wordTranslation.value = {
      word: word,
      translation: '网络错误，请稍后重试',
      phonetic: '',
      pos: '',
      example: ''
    }
  }
}

// 播放单词发音
const playWord = async (word: string) => {
  try {
    const response = await apiClient.post('/tts/synthesize-base64', {
      text: word,
      voice: selectedVoiceName.value,
      rate: '-10%',  // 稍慢一点，便于学习
      pitch: '+0Hz'
    })
    
    const audioData = `data:audio/mp3;base64,${response.audio}`
    const audio = new Audio(audioData)
    await audio.play()
  } catch (error) {
    console.error('播放失败:', error)
    message.error('播放失败')
  }
}

// 获取翻译模式文本（已弃用，改用下拉框）
const getTranslationModeText = (): string => {
  switch (translationMode.value) {
    case 'en':
      return '英文'
    case 'zh':
      return '中文'
    case 'both':
      return '中英'
    default:
      return '中英'
  }
}

// 关闭翻译框
const closeTranslationPopup = () => {
  showTranslationPopup.value = false
  currentWord.value = ''
  wordTranslation.value = null
}

// 点击其他地方关闭翻译框
const handleClickOutside = (event: MouseEvent) => {
  if (!showTranslationPopup.value) return
  
  const popup = document.querySelector('.word-translation-popup')
  const clickedElement = event.target as HTMLElement
  
  // 如果点击的是可点击单词，不关闭（因为会触发新的翻译）
  if (clickedElement.classList.contains('clickable-word')) {
    return
  }
  
  // 如果点击的不是弹窗内部，则关闭
  if (popup && !popup.contains(clickedElement)) {
    console.log('🔒 点击外部，关闭翻译卡片')
    closeTranslationPopup()
  }
}

// 处理加载对话事件 - 提取为命名函数以便清理
const handleLoadDialogueEvent = (event: any) => {
  const dialogueId = event.detail?.dialogueId
  console.log('dialogueId', dialogueId)
  if (dialogueId) {
    console.log('📨 收到加载对话事件:', dialogueId)
    loadDialogueHistory(dialogueId)
  }
}

// 阶段2：单词收藏功能
const loadSavedWords = () => {
  const saved = localStorage.getItem('saved_words')
  if (saved) {
    try {
      savedWords.value = JSON.parse(saved)
      console.log('✅ 加载收藏单词:', savedWords.value.length, '个')
    } catch (e) {
      console.error('❌ 加载收藏单词失败:', e)
      savedWords.value = []
    }
  }
}

const saveSavedWords = () => {
  localStorage.setItem('saved_words', JSON.stringify(savedWords.value))
  console.log('💾 保存收藏单词:', savedWords.value.length, '个')
}

const isWordSaved = (word: string): boolean => {
  return savedWords.value.includes(word.toLowerCase())
}

const toggleSaveWord = (word: string) => {
  const lowerWord = word.toLowerCase()
  const index = savedWords.value.indexOf(lowerWord)
  
  if (index > -1) {
    savedWords.value.splice(index, 1)
    message.success('已取消收藏')
  } else {
    savedWords.value.push(lowerWord)
    message.success('收藏成功')
  }
  
  saveSavedWords()
}

// 显示收藏单词列表
const showSavedWordsModal = () => {
  showSavedWordsList.value = true
  console.log('📖 打开收藏单词列表')
}

// 关闭收藏单词列表
const closeSavedWordsModal = () => {
  showSavedWordsList.value = false
  console.log('🔒 关闭收藏单词列表')
}

// 删除单个收藏单词
const removeSavedWord = (word: string) => {
  const lowerWord = word.toLowerCase()
  const index = savedWords.value.indexOf(lowerWord)
  
  if (index > -1) {
    savedWords.value.splice(index, 1)
    saveSavedWords()
    message.success('已删除收藏')
    console.log('🗑️ 删除收藏单词:', word)
  }
}

// 清空所有收藏单词
const clearAllSavedWords = () => {
  // 使用 confirm 确认
  if (window.confirm(`确定要清空全部 ${savedWords.value.length} 个收藏单词吗？此操作不可恢复。`)) {
    savedWords.value = []
    saveSavedWords()
    message.success('已清空所有收藏')
    console.log('🗑️ 清空所有收藏单词')
  }
}

// 加载历史对话
const loadDialogueHistory = async (dialogueId: string) => {
  // 防止重复加载
  if (isLoadingDialogue.value) {
    console.log('️ 正在加载中，跳过重复请求')
    return
  }
  
  // 如果已经加载过同一个对话，跳过
  if (lastLoadedDialogueId.value === dialogueId && currentDialogue.value) {
    console.log('⚠️ 对话已加载，跳过重复请求')
    return
  }
  
  try {
    isLoadingDialogue.value = true
    lastLoadedDialogueId.value = dialogueId
    console.log(' 加载历史对话, dialogueId:', dialogueId)
    const response = await apiClient.get(`/scenarios/dialogues/${dialogueId}`)
    console.log('✅ 加载对话API响应:', response)
    
    // apiClient拦截器已经返回了data字段
    if (response && response.id) {
      currentDialogue.value = response
      
      // 初始化每条对话的翻译模式为'default'（跟随全局设置）
      if (response.dialogue_data && Array.isArray(response.dialogue_data)) {
        lineTranslationModes.value = {}
        response.dialogue_data.forEach((_: any, index: number) => {
          lineTranslationModes.value[index] = 'default'
        })
        console.log(' 初始化对话翻译模式，共', response.dialogue_data.length, '条对话')
      }
      
      // 更新 URL，添加对话 ID（如果当前 URL 没有 ID）
      const currentId = route.params.id as string
      if (!currentId || currentId !== String(response.id)) {
        await router.push(`/ai-create/${response.id}`)
        console.log('🔗 URL 已更新为:', `/ai-create/${response.id}`)
      }
      
      message.success('对话加载成功，可以继续练习')
    } else {
      console.error('❌ 响应数据格式错误:', response)
      message.error('加载失败：响应数据格式错误')
    }
  } catch (error: any) {
    console.error('❌ 加载对话失败:', error)
    message.error(error.message || '加载失败')
  } finally {
    isLoadingDialogue.value = false
  }
}

// 加载场景列表
const loadScenarios = async () => {
  try {
    console.log('📞 加载场景列表...')
    const response = await apiClient.get('/scenarios/list')
    console.log('✅ 场景列表API响应:', response)
    
    // apiClient拦截器已经返回了data字段
    scenarios.value = response || []
    console.log('✅ 场景列表已更新，共', scenarios.value.length, '个场景')
  } catch (error) {
    console.error('❌ 加载场景失败:', error)
  }
}

// 上传前校验
const handleBeforeUpload = (file: File) => {
  if (!isAuthenticated()) {
    message.error('请先登录')
    return false
  }

  const validTypes = [
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]
  const isValidType = validTypes.includes(file.type) || 
    file.name.endsWith('.doc') || 
    file.name.endsWith('.docx') || 
    file.name.endsWith('.xls') || 
    file.name.endsWith('.xlsx')

  if (!isValidType) {
    message.error('只支持 Word 和 Excel 文件')
    return false
  }

  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    message.error('文件大小不能超过 10MB')
    return false
  }

  return true
}

// 上传文件
const handleUpload = async (options: any) => {
  const { file, onSuccess, onError } = options
  
  uploading.value = true
  uploadProgress.value = 0

  try {
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)

    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post('/documents/upload-and-save', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    clearInterval(progressInterval)
    uploadProgress.value = 100

    console.log('✅ 文档上传API响应:', response)
    
    // apiClient拦截器已经返回了data字段
    if (response && response.id) {
      message.success('文档上传并保存成功')
      await loadScenarios()
      onSuccess?.(response)
    } else {
      console.error('❌ 响应数据格式错误:', response)
      message.error('上传失败：响应数据格式错误')
      onError?.(new Error('上传失败'))
    }
  } catch (error: any) {
    console.error('❌ 上传失败:', error)
    message.error(error.message || '上传失败，请重试')
    onError?.(error)
  } finally {
    uploading.value = false
    setTimeout(() => {
      uploadProgress.value = 0
    }, 1000)
  }
}

// 生成对话
const generateDialogue = async (scenarioId: number, scenarioTitle: string) => {
  generating.value = true
  
  try {
    console.log('📞 开始生成对话, scenarioId:', scenarioId)
    const response = await apiClient.post('/scenarios/generate-dialogue', {
      scenario_id: scenarioId,
      title: `${scenarioTitle} - 对话练习`
    })
    
    console.log('✅ 生成对话API响应:', response)

    // apiClient拦截器已经返回了data字段，直接就是对话数据
    if (response && response.id) {
      currentDialogue.value = response
      
      // 更新 URL，添加对话 ID
      await router.push(`/ai-create/${response.id}`)
      console.log('🔗 URL 已更新为:', `/ai-create/${response.id}`)
      
      message.success('对话生成成功')
      // 刷新场景列表（如果需要）
      await loadScenarios()
    } else {
      console.error('❌ 响应数据格式错误:', response)
      message.error('生成失败：响应数据格式错误')
    }
  } catch (error: any) {
    console.error('❌ 生成对话失败:', error)
    message.error(error.message || '生成失败，请重试')
  } finally {
    generating.value = false
  }
}

// 快速生成对话（基于主题）
const handleQuickGenerate = async () => {
  if (!quickTopic.value.trim()) {
    message.warning('请输入对话主题')
    return
  }

  if (!isAuthenticated()) {
    message.error('请先登录')
    return
  }

  generating.value = true
  
  try {
    console.log('📞 开始快速生成对话, topic:', quickTopic.value)
    // 直接调用AI生成对话，不经过场景库
    const response = await apiClient.post('/scenarios/generate-from-topic', {
      topic: quickTopic.value.trim(),
      title: `${quickTopic.value.trim()} - 对话练习`
    })
    
    console.log('✅ 快速生成对话API响应:', response)

    // apiClient拦截器已经返回了data字段，直接就是对话数据
    if (response && response.id) {
      currentDialogue.value = response
      
      // 初始化每条对话的翻译模式为'default'（跟随全局设置）
      if (response.dialogue_data && Array.isArray(response.dialogue_data)) {
        lineTranslationModes.value = {}
        response.dialogue_data.forEach((_: any, index: number) => {
          lineTranslationModes.value[index] = 'default'
        })
        console.log(' 初始化对话翻译模式，共', response.dialogue_data.length, '条对话')
      }
      
      // 更新 URL，添加对话 ID
      await router.push(`/ai-create/${response.id}`)
      console.log('🔗 URL 已更新为:', `/ai-create/${response.id}`)
      
      message.success('对话生成成功！')
      quickTopic.value = ''  // 清空输入
      // 刷新场景列表
      await loadScenarios()
    } else {
      console.error('❌ 响应数据格式错误:', response)
      message.error('生成失败：响应数据格式错误')
    }
  } catch (error: any) {
    console.error('❌ 快速生成对话失败:', error)
    message.error(error.message || '生成失败，请重试')
  } finally {
    generating.value = false
  }
}

// 从后端加载可用语音
const loadVoices = async () => {
  try {
    const response = await apiClient.get('/tts/voices')
    console.log('✅ 加载语音列表:', response)
    availableVoices.value = response || []
    
    // 恢复用户上次选择的语音
    const savedVoice = localStorage.getItem('preferred_voice')
    if (savedVoice && availableVoices.value.find(v => v.id === savedVoice)) {
      selectedVoiceName.value = savedVoice
      console.log('✅ 恢复上次选择的语音:', savedVoice)
    } else if (availableVoices.value.length > 0) {
      // 默认选择第一个（通常是 Aria）
      selectedVoiceName.value = availableVoices.value[0].id
    }
    
    console.log('✅ 当前选择语音:', selectedVoiceName.value)
  } catch (error) {
    console.error('❌ 加载语音列表失败:', error)
    message.error('加载语音列表失败')
  }
}

// 处理语音变化
const handleVoiceChange = (voiceName: string) => {
  console.log('🎤 用户选择语音:', voiceName)
  // 保存到 localStorage，下次自动使用
  localStorage.setItem('preferred_voice', voiceName)
  message.success('已切换声音')
}

// 根据角色选择语音
const getVoiceForSpeaker = (speaker: string): string => {
  if (!useRoleVoices.value) {
    return selectedVoiceName.value
  }
  
  // 根据 speaker 选择语音
  const speakerLower = speaker.toLowerCase()
  if (speakerLower === 'a' || speakerLower === 'male') {
    return maleVoice.value
  } else if (speakerLower === 'b' || speakerLower === 'female') {
    return femaleVoice.value
  }
  
  // 默认返回选中的语音
  return selectedVoiceName.value
}

// 播放文本（使用 Edge-TTS）
const playText = async (text: string, index: number, speaker?: string) => {
  try {
    // 停止之前的播放
    if (playingAudio.value) {
      playingAudio.value.pause()
      playingAudio.value = null
    }
    
    playingIndex.value = index
    console.log('▶️ 开始播放第', index + 1, '句')
    
    // 根据角色选择语音
    const voiceToUse = speaker ? getVoiceForSpeaker(speaker) : selectedVoiceName.value
    console.log('🎤 使用语音:', voiceToUse, speaker ? `(角色: ${speaker})` : '')
    
    // 调用后端 TTS API
    const cacheKey = `tts_${voiceToUse}_${text.substring(0, 50)}_${index}`
    let audioBase64: string | null = await getCachedAudio(cacheKey)
        
    if (!audioBase64) {
      console.log(' 缓存未命中，调用 TTS API')
      const response = await apiClient.post('/tts/synthesize-base64', {
        text: text,
        voice: voiceToUse,
        rate: '+0%',
        pitch: '+0Hz'
      })
      audioBase64 = response.audio
      await saveAudioToCache(cacheKey, audioBase64)
    } else {
      console.log(' 使用缓存音频')
    }
        
    const audioData = `data:audio/mp3;base64,${audioBase64}`
    const audio = new Audio(audioData)
    playingAudio.value = audio
    
    audio.onended = () => {
      playingIndex.value = null
      playingAudio.value = null
      console.log('⏹️ 播放完成')
    }
    
    audio.onerror = () => {
      playingIndex.value = null
      playingAudio.value = null
      console.error('❌ 播放失败')
      message.error('播放失败')
    }
    
    await audio.play()
    
  } catch (error: any) {
    console.error('❌ 播放失败:', error)
    playingIndex.value = null
    message.error(error.message || '播放失败')
  }
}

// 开始/停止录音
const toggleRecording = async (index: number) => {
  if (recordingIndex.value === index) {
    // 停止录音
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
    }
    recordingIndex.value = null
  } else {
    // 开始录音
    try {
      // 使用 window.navigator 确保访问全局对象
      const nav = window.navigator as any
      
      console.log('🔍 ========== 录音诊断信息 ==========')
      console.log('🔍 当前 URL:', window.location.href)
      console.log('🔍 协议:', window.location.protocol)
      console.log('🔍 主机:', window.location.host)
      console.log('🔍 window:', typeof window)
      console.log('🔍 window.navigator:', nav)
      console.log('🔍 typeof window.navigator:', typeof nav)
      console.log('🔍 navigator keys:', Object.keys(nav || {}))
      console.log('🔍 mediaDevices:', nav?.mediaDevices)
      console.log('🔍 typeof mediaDevices:', typeof nav?.mediaDevices)
      console.log('🔍 mediaDevices === undefined:', nav?.mediaDevices === undefined)
      console.log('🔍 mediaDevices === null:', nav?.mediaDevices === null)
      
      if (nav?.mediaDevices) {
        console.log('🔍 mediaDevices keys:', Object.keys(nav.mediaDevices))
        console.log('🔍 getUserMedia:', nav.mediaDevices.getUserMedia)
        console.log('🔍 typeof getUserMedia:', typeof nav.mediaDevices.getUserMedia)
      } else {
        console.error('❌❌❌ mediaDevices 不存在！')
        console.log('🔍 尝试直接访问 window.navigator.mediaDevices:', (window as any).navigator?.mediaDevices)
      }
      
      // 检查是否在 iframe 中
      if (window.self !== window.top) {
        console.warn('⚠️  页面在 iframe 中运行，可能需要特殊权限')
      }
      
      // 检查协议
      if (window.location.protocol !== 'https:' && 
          window.location.hostname !== 'localhost' && 
          window.location.hostname !== '127.0.0.1') {
        console.warn('⚠️  非 HTTPS 且非 localhost，媒体 API 可能被阻止')
      }
      
      // 检查浏览器是否支持 - 使用 window.navigator
      if (!nav?.mediaDevices || typeof nav.mediaDevices.getUserMedia !== 'function') {
        console.error('❌ 浏览器不支持媒体设备 API')
        console.error('❌ nav:', nav)
        console.error('❌ nav.mediaDevices:', nav?.mediaDevices)
        console.error('❌ nav.mediaDevices.getUserMedia:', nav?.mediaDevices?.getUserMedia)
        
        // 尝试使用旧版 API
        const getUserMedia = 
          nav.getUserMedia || 
          nav.webkitGetUserMedia || 
          nav.mozGetUserMedia || 
          nav.msGetUserMedia
        
        if (getUserMedia && typeof getUserMedia === 'function') {
          console.log('✅ 发现旧版 getUserMedia API，尝试使用...')
          return new Promise((resolve, reject) => {
            getUserMedia.call(nav, { audio: true }, 
              (stream: MediaStream) => {
                console.log('✅ 旧版 API 成功获取麦克风流')
                setupMediaRecorder(stream, index)
                resolve(true)
              },
              (err: Error) => {
                console.error('❌ 旧版 API 也失败:', err)
                reject(err)
              }
            )
          })
        }
        
        console.error('❌ 所有 API 都不可用')
        message.error('您的浏览器不支持录音功能，请使用 Chrome、Firefox 或 Safari')
        return
      }
      
      console.log('✅ 浏览器支持现代媒体设备 API')
      
      // 请求麦克风权限 - 使用 window.navigator
      console.log('🎤 请求麦克风权限...')
      const stream = await nav.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      })
      
      console.log('✅ 成功获取麦克风流')
      console.log('🔍 音频轨道数:', stream.getAudioTracks().length)
      console.log('🔍 轨道状态:', stream.getAudioTracks()[0]?.enabled)
      
      setupMediaRecorder(stream, index)
      
    } catch (error: any) {
      console.error('❌ 录音失败:', error)
      console.error('❌ 错误名称:', error.name)
      console.error('❌ 错误消息:', error.message)
      console.error('❌ 错误堆栈:', error.stack)
      console.log('🔍 ==========================================')
      
      // 根据错误类型给出具体提示
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        message.error('麦克风权限被拒绝，请在浏览器设置中允许访问麦克风')
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        message.error('未检测到麦克风设备，请检查麦克风连接')
      } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
        message.error('麦克风被其他应用占用，请关闭其他使用麦克风的程序')
      } else if (error.name === 'OverconstrainedError') {
        message.error('麦克风配置不支持，请尝试简化设置')
      } else if (error.name === 'SecurityError') {
        message.error('安全错误：请在 HTTPS 或 localhost 环境下使用')
      } else {
        message.error(`无法访问麦克风: ${error.message || '未知错误'}`)
      }
    }
  }
}

// 设置 MediaRecorder
const setupMediaRecorder = (stream: MediaStream, index: number) => {
  try {
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    })
    audioChunks = []
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }
    
    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      recordings.value[index] = audioBlob
      stream.getTracks().forEach(track => track.stop())
      
      console.log('✅ 录音完成，大小:', audioBlob.size, 'bytes')
      message.success('录音保存成功')
    }
    
    mediaRecorder.onerror = (event: any) => {
      console.error('❌ MediaRecorder 错误:', event.error)
      message.error('录音过程中出现错误')
    }
    
    mediaRecorder.start()
    recordingIndex.value = index
    console.log('🎤 开始录音...')
    message.info('开始录音...')
  } catch (error) {
    console.error('❌ 创建 MediaRecorder 失败:', error)
    message.error('录音初始化失败')
  }
}

// 播放录音
const playRecording = (index: number) => {
  const blob = recordings.value[index]
  if (!blob) return
  
  const url = URL.createObjectURL(blob)
  const audio = new Audio(url)
  
  playingRecordingIndex.value = index
  
  audio.onended = () => {
    playingRecordingIndex.value = null
    URL.revokeObjectURL(url)
  }
  
  audio.onerror = () => {
    playingRecordingIndex.value = null
    message.error('播放失败')
  }
  
  audio.play()
}

// 评估发音
const evaluatePronunciation = async (index: number) => {
  const blob = recordings.value[index]
  if (!blob) {
    message.warning('请先录音')
    return
  }
  
  if (!currentDialogue.value) return
  
  const line = currentDialogue.value.dialogue_data[index]
  if (!line) return
  
  evaluatingIndex.value = index
  
  try {
    // 创建 FormData
    const formData = new FormData()
    formData.append('file', blob, `recording_${index}.webm`)
    formData.append('original_text', line.text)
    
    console.log('📞 开始评估发音, index:', index)
    
    // 调用后端 API
    const response = await apiClient.post('/pronunciation/evaluate-pronunciation', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    console.log('✅ 评分API响应:', response)
    
    // 保存评分结果
    pronunciationScores.value[index] = response
    
    // 显示评分弹窗
    currentScoreIndex.value = index
    showScoreModal.value = true
    
    message.success('评分完成！')
  } catch (error: any) {
    console.error('❌ 评分失败:', error)
    message.error(error.message || '评分失败，请重试')
  } finally {
    evaluatingIndex.value = null
  }
}

// 关闭评分弹窗
const closeScoreModal = () => {
  showScoreModal.value = false
  currentScoreIndex.value = null
}

// 获取单词颜色类名
const getWordColorClass = (status: string): string => {
  switch (status) {
    case 'correct':
      return 'word-correct'
    case 'wrong':
      return 'word-wrong'
    case 'missing':
      return 'word-missing'
    case 'extra':
      return 'word-extra'
    default:
      return ''
  }
}

// 获取分数颜色
const getScoreColor = (score: number): string => {
  if (score >= 90) return '#52c41a'  // 绿色
  if (score >= 70) return '#faad14'  // 黄色
  if (score >= 50) return '#ff7a45'  // 橙色
  return '#ff4d4f'  // 红色
}

// 获取分数徽章样式类
const getScoreBadgeClass = (score: number): string => {
  if (score >= 90) return 'badge-excellent'
  if (score >= 70) return 'badge-good'
  if (score >= 50) return 'badge-fair'
  return 'badge-poor'
}

// 获取分数颜色类（用于文本）
const getScoreColorClass = (score: number): string => {
  if (score >= 90) return 'score-excellent'
  if (score >= 70) return 'score-good'
  if (score >= 50) return 'score-fair'
  return 'score-poor'
}

// 获取单词评分样式类
const getWordScoreClass = (lineIndex: number, wordIndex: number): string => {
  const score = pronunciationScores.value[lineIndex]
  if (!score || !score.word_details) return ''
  
  const wordDetail = score.word_details[wordIndex]
  if (!wordDetail) return ''
  
  switch (wordDetail.status) {
    case 'correct':
      return 'word-correct'
    case 'wrong':
      return 'word-wrong'
    case 'missing':
      return 'word-missing'
    case 'extra':
      return 'word-extra'
    default:
      return ''
  }
}

// 获取练习次数
const getPracticeCount = (lineIndex: number): number => {
  // 这里可以根据实际需求计算，暂时返回1
  return 1
}

// 返回场景库
const backToScenarios = async () => {
  currentDialogue.value = null
  recordings.value = {}
  // 清除加载状态，允许下次重新加载
  isLoadingDialogue.value = false
  lastLoadedDialogueId.value = null
  
  // 清除 URL 中的对话 ID
  await router.push('/ai-create')
  console.log('🔗 URL 已重置为: /ai-create')
}

// 删除场景
const deleteScenario = async (scenarioId: number) => {
  try {
    console.log('📞 删除场景, scenarioId:', scenarioId)
    await apiClient.delete(`/scenarios/${scenarioId}`)
    message.success('删除成功')
    await loadScenarios()
  } catch (error: any) {
    console.error('❌ 删除失败:', error)
    message.error(error.message || '删除失败')
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  // 🎤 录音功能诊断
  console.log('🎤 ========== 页面加载 - 录音功能检查 ==========')
  console.log('🔍 URL:', window.location.href)
  console.log('🔍 协议:', window.location.protocol)
  console.log('🔍 主机:', window.location.hostname)
  console.log('🔍 navigator.mediaDevices:', navigator.mediaDevices)
  console.log('🔍 typeof mediaDevices:', typeof navigator.mediaDevices)
  
  if (navigator.mediaDevices) {
    console.log('✅ navigator.mediaDevices 存在')
    console.log('🔍 getUserMedia:', typeof navigator.mediaDevices.getUserMedia)
  } else {
    console.error('❌ navigator.mediaDevices 不存在！')
    console.log('🔍 尝试查找旧版 API...')
    console.log('🔍 webkitGetUserMedia:', !!(navigator as any).webkitGetUserMedia)
    console.log('🔍 mozGetUserMedia:', !!(navigator as any).mozGetUserMedia)
    console.log('🔍 msGetUserMedia:', !!(navigator as any).msGetUserMedia)
  }
  
  console.log('🔍 ==========================================')
  
  // 初始化音频缓存
  initAudioDB().catch(err => {
    console.error('❌ 音频缓存初始化失败:', err)
  })
  
  loadScenarios()
  loadVoices()
  loadSavedWords()  // 加载收藏的单词
  
  // 添加全局点击监听
  document.addEventListener('click', handleClickOutside)
  
  // 监听加载历史对话事件
  window.addEventListener('load-speaking-dialogue', handleLoadDialogueEvent)
})

// 监听路由参数变化，自动加载对话
watch(
  () => route.params.id,
  (newDialogueId, oldDialogueId) => {
    console.log('👀 路由参数变化:', { old: oldDialogueId, new: newDialogueId })
    
    if (newDialogueId && newDialogueId !== oldDialogueId) {
      // 只有当 ID 真正改变时才加载
      console.log('🔗 检测到对话 ID 变化，准备加载:', newDialogueId)
      loadDialogueHistory(String(newDialogueId))
    }
  },
  { immediate: true }  // 立即执行一次，替代 onMounted 中的逻辑
)

onUnmounted(() => {
  // 清理事件监听
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('load-speaking-dialogue', handleLoadDialogueEvent)
  
  // 停止连读播放
  stopContinuousPlay()
  
  if (playingAudio.value) {
    playingAudio.value.pause()
    playingAudio.value = null
  }
  if (mediaRecorder) {
    mediaRecorder.stream.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
:deep(.ant-select-selection-item),
:deep(.ant-select-selection-placeholder) {
  padding-inline-end: 0px !important;
}
.speaking-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 40px 20px;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
  position: relative;  /* 为悬浮框提供定位上下文 */
}

.page-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0 0 12px 0;
  letter-spacing: 0.5px;
}

.page-description {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0;
}

.saved-words-btn {
  height: 40px;
  padding: 0 20px;
  border-radius: var(--radius-md);
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(45, 110, 255, 0.2);
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.saved-words-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(45, 110, 255, 0.3);
}

.upload-section {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 32px;
  margin-bottom: 24px;
}

.tab-header {
  width: 100%;
}

.upload-content,
.quick-generate-content {
  padding: 20px 0;
  text-align: center;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0 0 20px 0;
}

.topic-input {
  margin-bottom: 20px;
  font-size: 15px;
}

.quick-actions {
  margin-bottom: 16px;
}

.generate-btn {
  height: 48px;
  padding: 0 32px;
  font-size: 16px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.quick-hint {
  color: var(--color-text-placeholder);
  font-size: 13px;
}

.quick-hint p {
  margin: 0;
}

.upload-btn {
  height: 48px;
  padding: 0 32px;
  font-size: 16px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.upload-hint {
  margin-top: 16px;
  color: var(--color-text-placeholder);
  font-size: 13px;
}

.upload-hint p {
  margin: 4px 0;
}

.upload-progress {
  margin-bottom: 24px;
}

/* 场景库列表 */
.scenario-list {
  margin-top: 24px;
}

.list-header {
  margin-bottom: 20px;
}

.list-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0;
}

.scenario-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.scenario-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.scenario-card:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--color-primary);
}

.scenario-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.scenario-icon {
  width: 48px;
  height: 48px;
  background: var(--color-primary-light);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
}

.scenario-detail {
  flex: 1;
}

.scenario-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0 0 4px 0;
}

.scenario-meta {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
}

.scenario-actions {
  display: flex;
  gap: 12px;
}

/* 修复场景卡片中 Ant Design Vue 按钮图标对齐 */
.scenario-actions :deep(.ant-btn) {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px;
}

.scenario-actions :deep(.ant-btn-icon) {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.scenario-actions :deep(.ant-btn svg) {
  vertical-align: middle;
}

/* 对话展示 */
.dialogue-section {
  margin-top: 24px;
}

.dialogue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--color-border);
}

.dialogue-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

/* 修复 Ant Design Vue 按钮图标对齐 */
.dialogue-controls :deep(.ant-btn) {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 6px;
}

.dialogue-controls :deep(.ant-btn-icon) {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.dialogue-controls :deep(.ant-btn svg) {
  vertical-align: middle;
}

.voice-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 修复语音选择器中 Ant Design Vue 组件图标对齐 */
.voice-selector :deep(.ant-btn),
.voice-selector :deep(.ant-select) {
  display: inline-flex !important;
  align-items: center !important;
}

.voice-selector :deep(.ant-btn svg),
.voice-selector :deep(.ant-select svg) {
  vertical-align: middle;
}

.voice-select {
  width: 280px;
}

.selector-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

/* 连读开关样式 */
.continuous-play-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 连读播放时高亮当前对话 */
.dialogue-list.continuous-playing .dialogue-line {
  transition: all 0.3s;
}

.dialogue-line.is-playing {
  border-color: var(--color-primary) !important;
  background: linear-gradient(135deg, rgba(45, 110, 255, 0.05) 0%, rgba(45, 110, 255, 0.1) 100%) !important;
  box-shadow: 0 0 0 2px rgba(45, 110, 255, 0.2);
}

.dialogue-line.is-playing .speaker-badge {
  transform: scale(1.1);
}

/* 全局翻译模式样式 */
.global-translation-mode {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 角色语音开关样式 */
.role-voice-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 翻译显示模式切换样式 */
.translation-mode-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.toggle-hint {
  font-size: 12px;
  color: var(--color-primary);
  margin-left: 4px;
}

.dialogue-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0 0 8px 0;
}

.dialogue-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

.dialogue-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dialogue-line {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  position: relative;
  transition: all 0.3s;
}

.dialogue-line.has-score {
  border-color: #52c41a;
  background: linear-gradient(135deg, rgba(82, 196, 26, 0.02) 0%, rgba(82, 196, 26, 0.05) 100%);
}

/* 分数徽章 */
.score-badge {
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 60px;
  overflow: hidden;
}

.score-badge::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 60px 60px 0;
}

.badge-excellent::before {
  border-color: transparent #52c41a transparent transparent;
}

.badge-good::before {
  border-color: transparent #1890ff transparent transparent;
}

.badge-fair::before {
  border-color: transparent #faad14 transparent transparent;
}

.badge-poor::before {
  border-color: transparent #ff4d4f transparent transparent;
}

.score-badge-number {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 18px;
  font-weight: 700;
  color: white;
  z-index: 1;
}

/* 练习次数标签 */
.practice-count {
  display: inline-block;
  margin-left: 12px;
  padding: 2px 10px;
  background: #f0f0f0;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
}

/* 单词评分样式 */
.word-correct {
  color: #52c41a;
  font-weight: 600;
}

.word-wrong {
  color: #ff4d4f;
  font-weight: 600;
  text-decoration: underline wavy #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
  padding: 2px 4px;
  border-radius: 4px;
}

.word-missing {
  color: #999;
  text-decoration: line-through;
  opacity: 0.6;
}

.word-extra {
  color: #faad14;
  font-style: italic;
}

/* 评分摘要栏 */
.score-summary {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-top: 16px;
  background: linear-gradient(135deg, rgba(82, 196, 26, 0.05) 0%, rgba(82, 196, 26, 0.1) 100%);
  border: 1px solid rgba(82, 196, 26, 0.2);
  border-radius: 12px;
  gap: 12px;
}

.score-summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.score-summary-label {
  font-size: 12px;
  color: #666;
}

.score-summary-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.score-summary-value.score-excellent {
  color: #52c41a;
}

.score-summary-value.score-good {
  color: #1890ff;
}

.score-summary-value.score-fair {
  color: #faad14;
}

.score-summary-value.score-poor {
  color: #ff4d4f;
}

.score-summary-divider {
  width: 1px;
  height: 30px;
  background: rgba(0, 0, 0, 0.1);
}

.score-summary-arrow {
  margin-left: auto;
  font-size: 18px;
  color: #999;
  cursor: pointer;
}

.line-header {
  margin-bottom: 12px;
}

.speaker-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
}

.speaker-badge.a {
  background: #e3f2fd;
  color: #1976d2;
}

.speaker-badge.b {
  background: #f3e5f5;
  color: #7b1fa2;
}

.line-content {
  margin-bottom: 16px;
}

.english-text {
  font-size: 16px;
  color: var(--color-text-main);
  margin: 0 0 8px 0;
  line-height: 1.6;
  font-weight: 500;
}

.chinese-text {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

.line-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 修复对话行中 Ant Design Vue 按钮图标对齐 */
.line-actions :deep(.ant-btn) {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px;
}

.line-actions :deep(.ant-btn-icon) {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.line-actions :deep(.ant-btn svg) {
  vertical-align: middle;
}

/* 可点击单词样式 */
.clickable-word {
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 3px;
  padding: 2px 2px;
  margin: 0 1px;
  display: inline-block;
}

.clickable-word:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

/* 悬浮翻译框 */
.word-translation-popup {
  position: fixed;  /* 使用 fixed 定位，相对于视口 */
  z-index: 9999;  /* 确保在最上层 */
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  padding: 16px;
  min-width: 280px;
  max-width: 350px;
  animation: fadeIn 0.2s ease;
  pointer-events: auto;  /* 确保可以交互 */
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.popup-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}

.popup-word {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0;
  flex: 1;
}

.play-word-btn {
  color: var(--color-primary);
}

.close-btn {
  color: var(--color-text-secondary);
}

.popup-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.translation-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.translation-item .label {
  color: var(--color-text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.translation-item .value {
  color: var(--color-text-main);
  flex: 1;
}

.popup-actions {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.popup-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-secondary);
  font-size: 14px;
  padding: 20px 0;
  justify-content: center;
}

/* 生成中状态 */
.generating-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 20px;
}

.generating-state p {
  font-size: 16px;
  color: var(--color-text-secondary);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .speaking-container {
    padding: 24px 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .page-description {
    font-size: 14px;
  }

  .upload-section {
    padding: 32px 16px;
  }

  .upload-btn {
    width: 100%;
    height: 44px;
    font-size: 15px;
  }

  .scenario-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .scenario-actions {
    width: 100%;
  }

  .scenario-actions .ant-btn {
    flex: 1;
  }

  .dialogue-header {
    flex-direction: column;
    gap: 12px;
  }

  .dialogue-controls {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    width: 100%;
  }

  /* 翻译模式和角色语音开关占一行 */
  .global-translation-mode,
  .role-voice-toggle {
    flex: 0 0 auto;
  }

  /* 声音选择器和下拉框占一行 */
  .voice-selector {
    flex: 1 1 100%;
    flex-direction: row;
    align-items: center;
    gap: 8px;
    width: 100%;
  }

  .voice-select {
    flex: 1;
    width: auto !important;
  }

  .selector-label {
    font-size: 13px;
    white-space: nowrap;
  }

  /* 连读开关独占一行 */
  .continuous-play-toggle {
    flex: 1 1 100%;
    width: 100%;
  }

  .dialogue-controls .ant-btn {
    width: 100%;
  }

  .dialogue-title {
    font-size: 18px;
  }

  .line-actions {
    flex-direction: column;
  }

  .line-actions .ant-btn {
    width: 100%;
  }

  /* 移动端悬浮翻译框适配 */
  .word-translation-popup {
    position: fixed;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: none;
  }

  .clickable-word {
    padding: 4px 6px;
    margin: 0 -4px;
  }
}

/* 收藏单词列表弹窗 */
.saved-words-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

.saved-words-modal {
  background: white;
  border-radius: var(--radius-xl);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-title svg {
  color: var(--color-primary);
}

.modal-close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-main);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-text-secondary);
}

.empty-state svg {
  color: var(--color-text-placeholder);
  margin-bottom: 16px;
}

.empty-state p {
  margin: 8px 0;
  font-size: 16px;
}

.empty-hint {
  font-size: 14px !important;
  color: var(--color-text-placeholder) !important;
}

.words-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.word-item {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 16px;
  transition: all 0.2s;
}

.word-item:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(45, 110, 255, 0.1);
  transform: translateX(4px);
}

.word-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.word-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0;
  flex: 1;
}

.word-actions-inline {
  display: flex;
  gap: 8px;
}

.inline-action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.inline-action-btn:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

.delete-btn:hover {
  color: #ff4d4f;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
}

.total-count {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .saved-words-btn {
    width: 100%;
  }
  
  .saved-words-modal {
    width: 95%;
    max-height: 85vh;
  }
  
  .modal-header {
    padding: 20px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-footer {
    padding: 12px 20px;
    flex-direction: column;
    gap: 12px;
  }
  
  .modal-footer .ant-btn {
    width: 100%;
  }
  
  .word-text {
    font-size: 16px;
  }
}

/* 发音评分弹窗 */
.score-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

.score-modal {
  background: white;
  border-radius: var(--radius-xl);
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.score-modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--color-border);
}

.score-modal .modal-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-modal .modal-close-btn {
  color: var(--color-text-secondary);
}

.score-modal .modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 总体评分 */
.overall-score {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: var(--radius-lg);
  margin-bottom: 24px;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 4px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.score-number {
  font-size: 32px;
  font-weight: 700;
}

.score-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: var(--radius-md);
}

.score-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.score-value {
  font-size: 18px;
  font-weight: 600;
}

/* 逐词分析 */
.section-title-small {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0 0 16px 0;
}

.words-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
}

.word-eval-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  border: 2px solid;
  min-width: 80px;
  transition: all 0.2s;
}

.word-eval-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.eval-word {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.eval-score {
  font-size: 14px;
  font-weight: 500;
}

.eval-status {
  margin-top: 4px;
  text-align: center;
}

.eval-status small {
  font-size: 11px;
  color: var(--color-text-secondary);
}

/* 单词状态颜色 */
.word-correct {
  background: #f6ffed;
  border-color: #52c41a;
  color: #52c41a;
}

.word-wrong {
  background: #fff2f0;
  border-color: #ff4d4f;
  color: #ff4d4f;
}

.word-missing {
  background: #fff7e6;
  border-color: #faad14;
  color: #faad14;
}

.word-extra {
  background: #f0f5ff;
  border-color: #2f54eb;
  color: #2f54eb;
}

/* 图例 */
.legend {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 2px solid;
}

/* 识别结果 */
.recognition-result {
  padding: 16px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.result-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-text p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
}

.result-text strong {
  color: var(--color-text-main);
}

.score-modal .modal-footer {
  display: flex;
  justify-content: center;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .score-modal {
    width: 95%;
    max-height: 90vh;
  }
  
  .overall-score {
    flex-direction: column;
    gap: 16px;
  }
  
  .score-circle {
    width: 80px;
    height: 80px;
  }
  
  .score-number {
    font-size: 24px;
  }
  
  .words-container {
    gap: 8px;
  }
  
  .word-eval-item {
    min-width: 60px;
    padding: 8px 12px;
  }
  
  .legend {
    gap: 12px;
  }
}
</style>
