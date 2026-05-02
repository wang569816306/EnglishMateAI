<template>
  <div class="ai-create-container">
    <div class="page-header">
      <h1 class="page-title">AI 创作</h1>
      <p class="page-description">使用AI能力创作各种内容</p>
    </div>
    
    <div class="features-grid">
      <div class="feature-card" v-for="feature in features" :key="feature.title">
        <div class="feature-icon">{{ feature.icon }}</div>
        <h3 class="feature-title">{{ feature.title }}</h3>
        <p class="feature-desc">{{ feature.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Feature {
  icon: string
  title: string
  description: string
}

const features = ref<Feature[]>([
  { icon: '📝', title: '文章创作', description: '帮助你撰写各种类型的文章和内容' },
  { icon: '🎨', title: '创意生成', description: '激发创意灵感，生成独特想法' },
  { icon: '📊', title: '数据分析', description: '智能分析和解读数据' },
  { icon: '💡', title: '头脑风暴', description: 'AI辅助进行创意头脑风暴' }
])
</script>

<style scoped>
.ai-create-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
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

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.feature-card {
  background: white;
  border: 1px solid #e5e4e7;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s;
}

.feature-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 16px;
  font-weight: 500;
  color: #08060d;
  margin: 0 0 8px 0;
}

.feature-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>