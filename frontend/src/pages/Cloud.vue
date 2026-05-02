<template>
  <div class="cloud-container">
    <div class="page-header">
      <h1 class="page-title">云盘</h1>
      <p class="page-description">存储和管理你的文件</p>
    </div>
    
    <div class="cloud-content">
      <div class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        <p class="empty-text">暂无文件</p>
        <p class="empty-hint">上传的文件将在这里显示</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.cloud-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 40px 20px;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 24px;
  font-weight: 500;
  color: #08060d;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.cloud-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #ccc;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  color: #999;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: #bbb;
  margin: 0;
}
</style>
