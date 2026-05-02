# EnglishMate AI - 前端项目

基于 Vue3 + Vite + TypeScript 构建的 AI 聊天应用前端，UI 设计参考豆包。

## 技术栈

- Vue 3.5
- Vite 8
- TypeScript
- Vue Router 4
- 原生 CSS（无 UI 框架）

## 项目结构

```
src/
├── components/     # 可复用组件
│   ├── Sidebar.vue      # 侧边栏
│   ── InputArea.vue    # 输入区域
├── pages/          # 页面组件
│   ├── Home.vue         # 首页（新对话）
│   ├── Chat.vue         # 聊天页面
│   ├── AICreate.vue     # AI创作页面
│   ── Cloud.vue        # 云盘页面
── router/         # 路由配置
│   └── index.ts
├── assets/         # 静态资源
├── App.vue         # 根组件
├── main.ts         # 入口文件
└── style.css       # 全局样式
```

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5174/

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 功能特性

- ✅ 左侧菜单导航（新对话、AI创作、云盘）
- ✅ 历史对话列表
- ✅ 底部输入框（含功能按钮）
- ✅ 响应式设计
- ✅ 路由规范化管理
- ✅ 组件化架构

## 设计规范

- 完全按照豆包 UI 设计 1:1 复刻
- 左侧固定侧边栏（280px）
- 右侧主内容区域
- 简洁白色背景
- 圆角卡片设计
- 平滑过渡动画
