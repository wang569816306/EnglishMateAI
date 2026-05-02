<template>
  <div class="home-container">
    <div class="welcome-section">
      <h1 class="welcome-title">有什么我能帮你的吗？</h1>
    </div>
    
    <div class="suggestions-grid">
      <div class="suggestion-item" v-for="item in suggestions" :key="item">
        {{ item }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const suggestions = ref([
  '资讯：人工智能 ETF 易方达逆势获千万份净申购',
  'WLAN和WiFi有什么区别？',
  '如何训练自己的AI模型？',
  '如果没有网络，可以做哪些有趣的事情？',
  '资讯：创业板"七姐妹"五年平均回报率超 15 倍',
  '解释下产品经理与开发团队的协作方式',
  '为什么许多程序员喜欢使用 Dvorak 键盘布局？',
  '请推荐一些适合初学者的AI项目想法',
  '资讯：算力租赁概念涨势扩大 行云科技 20cm 涨停'
])
</script>

<style scoped>
.home-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  background: linear-gradient(180deg, var(--color-bg) 0%, var(--color-bg-secondary) 100%);
}

.welcome-section {
  margin-bottom: 40px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, var(--color-text-main) 0%, var(--color-text-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
  max-width: 900px;
  width: 100%;
  padding: 0 20px;
}

.suggestion-item {
  background: var(--color-bg);
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  font-weight: 500;
}

.suggestion-item:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-main);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
}

@media (max-width: 768px) {
  .home-container {
    padding: 24px 16px;
  }
  
  .welcome-section {
    margin-bottom: 24px;
  }
  
  .welcome-title {
    font-size: 22px;
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
    padding: 0;
    gap: 10px;
  }
  
  .suggestion-item {
    padding: 12px 14px;
    font-size: 13px;
  }
}
</style>
