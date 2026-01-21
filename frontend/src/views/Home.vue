<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-brand">MULTIMO</div>
      <div class="nav-links">
      </div>
    </nav>

    <div class="main-content">
      <!-- 上半部分：Hero 区域 -->
      <section class="hero-section">
        <div class="hero-left">
          <div class="tag-row">
            <span class="minimal-tag">简洁通用的群体智能引擎</span>
          </div>
          
          <h1 class="main-title">
            上传任意报告<br>
            即刻推演未来
          </h1>
          
          <div class="hero-desc">
            <p>
              即使只有一段文字，Multimo 也能基于其中的现实种子，全自动生成与之对应的至多百万级 Agent 构成的平行世界。通过上帝视角注入变量，在复杂的群体交互中寻找动态环境下的"局部最优解"。
            </p>
            <p class="slogan-text">
              让未来在 Agent 群中预演，让决策在百战后胜出
            </p>
          </div>
           
          <div class="decoration-line"></div>
        </div>
        
        <div class="hero-right">
          <!-- Logo 区域 -->
          <div class="logo-container">
            <img src="../assets/logo/multimo-logo.png" alt="Multimo Logo" class="hero-logo" />
          </div>
          
          <button class="scroll-down-btn" @click="scrollToBottom">
            ↓
          </button>
        </div>
      </section>

      <!-- 下半部分：双栏布局 -->
      <section class="dashboard-section">
        <!-- 左栏：状态与步骤 -->
        <div class="left-panel">
          <div class="panel-header">
            SYSTEM STATUS
          </div>
          
          <h2 class="section-title">准备就绪</h2>
          <p class="section-desc">
            预测引擎待命中，可上传多份非结构化数据以初始化模拟序列
          </p>
          
          <!-- 数据指标卡片 -->
          <div class="metrics-row">
            <div class="metric-card">
              <div class="metric-value">低成本</div>
              <div class="metric-label">常规模拟平均5$/次</div>
            </div>
            <div class="metric-divider"></div>
            <div class="metric-card">
              <div class="metric-value">高可用</div>
              <div class="metric-label">最多百万级Agent模拟</div>
            </div>
          </div>

          <!-- 项目模拟步骤介绍 (新增区域) -->
          <div class="steps-container">
            <div class="steps-header">
               WORKFLOW SEQUENCE
            </div>
            <div class="workflow-list">
              <div class="workflow-item">
                <span class="step-num">01</span>
                <div class="step-info">
                  <div class="step-title">图谱构建</div>
                  <div class="step-desc">现实种子提取 & 个体与群体记忆注入 & GraphRAG构建</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">02</span>
                <div class="step-info">
                  <div class="step-title">环境搭建</div>
                  <div class="step-desc">实体关系抽取 & 人设生成 & 环境配置Agent注入仿真参数</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">03</span>
                <div class="step-info">
                  <div class="step-title">开始模拟</div>
                  <div class="step-desc">双平台并行模拟 & 自动解析预测需求 & 动态更新时序记忆</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">04</span>
                <div class="step-info">
                  <div class="step-title">报告生成</div>
                  <div class="step-desc">ReportAgent拥有丰富的工具集与模拟后环境进行深度交互</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">05</span>
                <div class="step-info">
                  <div class="step-title">深度互动</div>
                  <div class="step-desc">与模拟世界中的任意一位进行对话 & 与ReportAgent进行对话</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右栏：交互控制台 -->
        <div class="right-panel">
          <div class="console-box">
            <!-- 上传区域 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">01 / 现实种子</span>
                <span class="console-meta">支持格式: PDF, MD, TXT</span>
              </div>
              
              <div 
                class="upload-zone"
                :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.md,.txt"
                  @change="handleFileSelect"
                  style="display: none"
                  :disabled="loading"
                />
                
                <div v-if="files.length === 0" class="upload-placeholder">
                  <div class="upload-icon">↑</div>
                  <div class="upload-title">拖拽文件上传</div>
                  <div class="upload-hint">或点击浏览文件系统</div>
                </div>
                
                <div v-else class="file-list">
                  <div v-for="(file, index) in files" :key="index" class="file-item">
                    <span class="file-icon">📄</span>
                    <span class="file-name">{{ file.name }}</span>
                    <button @click.stop="removeFile(index)" class="remove-btn">×</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分割线 -->
            <div class="console-divider">
              <span>输入参数</span>
            </div>

            <!-- 输入区域 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">>_ 02 / 模拟提示词</span>
              </div>
              <div class="input-wrapper">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="code-input"
                  placeholder="// 用自然语言输入模拟或预测需求（例.武大若发布撤销肖某处分的公告，会引发什么舆情走向）"
                  rows="6"
                  :disabled="loading"
                ></textarea>
                <div class="model-badge">引擎: Multimo-V1.0</div>
              </div>
            </div>

            <!-- 分割线 -->
            <div class="console-divider">
              <span>配置</span>
            </div>

            <!-- 模拟轮数 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">>_ 03 / 模拟轮数</span>
              </div>
              <div class="rounds-input-wrapper">
                <input 
                  type="number" 
                  v-model.number="formData.rounds" 
                  class="rounds-input"
                  min="1"
                  max="100"
                >
                <span class="rounds-unit">Rounds</span>
              </div>
              <div class="rounds-hints">
                <div class="hint-item">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                  </svg>
                  <span>建议: {{ recommendedRounds }} 轮</span>
                </div>
                <div class="hint-item">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                  </svg>
                  <span>预计: 约 {{ estimatedTime }} 分钟</span>
                </div>
              </div>
            </div>

            <!-- 高级选项 -->
            <div class="advanced-options">
              <div class="advanced-header" @click="showAdvanced = !showAdvanced">
                <div class="advanced-title">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="7" height="7"></rect>
                    <rect x="14" y="3" width="7" height="7"></rect>
                    <rect x="14" y="14" width="7" height="7"></rect>
                    <rect x="3" y="14" width="7" height="7"></rect>
                  </svg>
                  <span>高级选项</span>
                </div>
                <svg 
                  class="advanced-arrow" 
                  :class="{ expanded: showAdvanced }"
                  width="14" 
                  height="14" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  stroke-width="2"
                >
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </div>
              
              <Transition name="slide-fade">
                <div v-if="showAdvanced" class="advanced-content">
                  <div class="manual-mode-option">
                    <label class="checkbox-wrapper">
                      <input 
                        type="checkbox" 
                        v-model="enableManualMode"
                        @change="toggleManualMode"
                      >
                      <span class="checkbox-custom"></span>
                      <span class="checkbox-label">启用手动模式</span>
                    </label>
                    <div class="mode-explanation">
                      <p>启用后每个步骤将暂停等待您的确认。</p>
                      <p class="explanation-title">适用场景：</p>
                      <ul>
                        <li>需要查看中间结果</li>
                        <li>调整模拟参数</li>
                        <li>开发调试</li>
                      </ul>
                      <p class="explanation-note">💡 大多数情况下，推荐使用默认的自动驾驶模式。</p>
                    </div>
                  </div>
                </div>
              </Transition>
            </div>

            <!-- 启动按钮 -->
            <div class="console-section btn-section">
              <button 
                class="start-engine-btn"
                @click="startSimulation"
                :disabled="!canSubmit || loading"
              >
                <span v-if="!loading">启动引擎</span>
                <span v-else>初始化中...</span>
                <span class="btn-arrow">→</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 历史项目数据库 -->
      <HistoryDatabase />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'

const router = useRouter()

// 表单数据
const formData = ref({
  simulationRequirement: '',
  mode: 'auto', // 默认自动驾驶
  rounds: 15    // 默认15轮
})

// 文件列表
const files = ref([])

// 状态
const loading = ref(false)
const error = ref('')
const isDragOver = ref(false)

// 高级选项状态
const showAdvanced = ref(false)
const enableManualMode = ref(false)

// 文件输入引用
const fileInput = ref(null)

// 计算属性:是否可以提交
const canSubmit = computed(() => {
  return formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
})

// 计算属性:推荐轮数
const recommendedRounds = computed(() => {
  if (files.value.length === 0) return 15
  if (files.value.length <= 2) return 10
  if (files.value.length <= 5) return 15
  return 20
})

// 计算属性:预估时间
const estimatedTime = computed(() => {
  const baseTime = formData.value.rounds * 0.6
  return Math.round(baseTime)
})

// 监听手动模式切换
const toggleManualMode = () => {
  formData.value.mode = enableManualMode.value ? 'manual' : 'auto'
}

// 触发文件选择
const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

// 处理拖拽相关
const handleDragOver = (e) => {
  if (!loading.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e) => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  isDragOver.value = false
  if (loading.value) return
  
  const droppedFiles = Array.from(e.dataTransfer.files)
  addFiles(droppedFiles)
}

// 添加文件
const addFiles = (newFiles) => {
  const validFiles = newFiles.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  files.value.push(...validFiles)
}

// 移除文件
const removeFile = (index) => {
  files.value.splice(index, 1)
}

// 滚动到底部
const scrollToBottom = () => {
  window.scrollTo({
    top: document.body.scrollHeight,
    behavior: 'smooth'
  })
}

// 开始模拟 - 立即跳转，API调用在Process页面进行
const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  
  // 存储待上传的数据
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement, formData.value.mode)
    
    // 立即跳转到Process页面（使用特殊标识表示新建项目）
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}
</script>

<style scoped>
/* 全局变量与重置 */
:root {
  --black: #000000;
  --white: #FFFFFF;
  --orange: #FF4500;
  --gray-light: #F5F5F5;
  --gray-text: #666666;
  --border: #E5E5E5;
  /* 
    使用 Space Grotesk 作为主要标题字体，JetBrains Mono 作为代码/标签字体
    确保已在 index.html 引入这些 Google Fonts 
  */
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  --font-cn: 'Noto Sans SC', system-ui, sans-serif;
}

.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #F8F9FA 0%, #E8EAF0 50%, #F0F2F8 100%);
  font-family: var(--font-sans);
  color: var(--black);
}

/* 顶部导航 */
.navbar {
  height: 60px;
  background: var(--black);
  color: var(--white);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  font-family: var(--font-mono);
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.2rem;
}

.nav-links {
  display: flex;
  align-items: center;
}

/* 主要内容区 */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 60px 40px;
}

/* Hero 区域 */
.hero-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 80px;
  position: relative;
}

.hero-left {
  flex: 1;
  padding-right: 60px;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

.minimal-tag {
  border: 1px solid var(--black);
  color: var(--black);
  padding: 4px 12px;
  font-weight: 500;
  letter-spacing: 1px;
  font-size: 0.75rem;
  border-radius: 20px;
}

.main-title {
  font-size: 4rem;
  line-height: 1.1;
  font-weight: 400;
  margin: 0 0 40px 0;
  letter-spacing: -1px;
  color: var(--black);
}

.hero-desc {
  font-size: 1rem;
  line-height: 1.8;
  color: #555;
  max-width: 600px;
  margin-bottom: 50px;
  font-weight: 400;
  text-align: left;
}

.hero-desc p {
  margin-bottom: 1.5rem;
}

.slogan-text {
  font-size: 1.1rem;
  font-weight: 400;
  color: #888;
  letter-spacing: 0.5px;
  margin-top: 20px;
  font-style: italic;
}

.decoration-line {
  width: 40px;
  height: 2px;
  background: var(--black);
}

.hero-right {
  flex: 0.8;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
}

.logo-container {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  padding-right: 40px;
}

.hero-logo {
  max-width: 500px;
  width: 100%;
  opacity: 0.85;
  mix-blend-mode: multiply;
  filter: contrast(0.95) brightness(1.05);
  transition: all 0.3s ease;
}

.hero-logo:hover {
  opacity: 1;
  filter: contrast(1) brightness(1);
}

.scroll-down-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--orange);
  font-size: 1.2rem;
  transition: all 0.2s;
}

.scroll-down-btn:hover {
  border-color: var(--orange);
}

/* Dashboard 双栏布局 */
.dashboard-section {
  display: flex;
  gap: 60px;
  border-top: 1px solid var(--border);
  padding-top: 60px;
  align-items: flex-start;
}

.dashboard-section .left-panel,
.dashboard-section .right-panel {
  display: flex;
  flex-direction: column;
}

/* 左侧面板 */
.left-panel {
  flex: 0.8;
}

.panel-header {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--black);
  letter-spacing: 2px;
  margin-bottom: 30px;
  font-weight: 700;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 300;
  margin: 0 0 20px 0;
  letter-spacing: -1px;
}

.section-desc {
  color: #666;
  margin-bottom: 40px;
  line-height: 1.6;
  font-size: 0.95rem;
}

.metrics-row {
  display: flex;
  align-items: center;
  gap: 40px;
  margin-bottom: 40px;
  padding-bottom: 40px;
  border-bottom: 1px solid #EEE;
}

.metric-card {
  border: none;
  padding: 0;
  min-width: auto;
}

.metric-divider {
  width: 1px;
  height: 40px;
  background: #EEE;
}

.metric-value {
  font-family: var(--font-mono);
  font-size: 1.5rem;
  font-weight: 400;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 0.8rem;
  color: #999;
}

/* 项目模拟步骤介绍 */
.steps-container {
  border: none;
  padding: 0;
  position: relative;
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--black);
  letter-spacing: 2px;
  margin-bottom: 30px;
  font-weight: 700;
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.step-num {
  font-family: var(--font-mono);
  font-weight: 400;
  color: var(--black);
  opacity: 0.2;
  font-size: 0.9rem;
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 500;
  font-size: 0.95rem;
  margin-bottom: 4px;
  letter-spacing: 0.5px;
}

.step-desc {
  font-size: 0.85rem;
  color: var(--gray-text);
}

/* 右侧交互控制台 */
.right-panel {
  flex: 1.2;
}

.console-box {
  border: 1px solid #CCC; /* 外部实线 */
  padding: 8px; /* 内边距形成双重边框感 */
}

.console-section {
  padding: 20px;
}

.console-section.btn-section {
  padding-top: 0;
  margin-top: 0;
}

.console-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #666;
}

.upload-zone {
  border: 1px dashed #CCC;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #FAFAFA;
}

.upload-zone:hover {
  background: #F0F0F0;
  border-color: #999;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  width: 40px;
  height: 40px;
  border: 1px solid #DDD;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  color: #999;
}

.upload-title {
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.upload-hint {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #999;
}

.file-list {
  width: 100%;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  background: var(--white);
  padding: 8px 12px;
  border: 1px solid #EEE;
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

.file-name {
  flex: 1;
  margin: 0 10px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #999;
}

.console-divider {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #EEE;
}

.console-divider span {
  padding: 0 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #BBB;
  letter-spacing: 1px;
}

.input-wrapper {
  position: relative;
  border: 1px solid #DDD;
  background: #FAFAFA;
}

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 20px;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  min-height: 150px;
}

.model-badge {
  position: absolute;
  bottom: 10px;
  right: 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #AAA;
}

.start-engine-btn {
  width: 100%;
  background: var(--black);
  color: var(--white);
  border: 1px solid #CCC;
  padding: 20px;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

/* 可点击状态（非禁用） */
.start-engine-btn:not(:disabled) {
  background: var(--black);
  border: 1px solid var(--black);
  animation: pulse-border 2s infinite;
}

.start-engine-btn:hover:not(:disabled) {
  background: var(--orange);
  border-color: var(--orange);
  transform: translateY(-2px);
}

.start-engine-btn:active:not(:disabled) {
  transform: translateY(0);
}

.start-engine-btn:disabled {
  background: #E5E5E5;
  color: #999;
  cursor: not-allowed;
  transform: none;
  border: 1px solid #CCC;
}

/* 轮数输入样式 */
.rounds-input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #FAFAFA;
  border: 1px solid #DDD;
  padding: 10px 15px;
}

.rounds-input {
  border: none;
  background: transparent;
  font-family: var(--font-mono);
  font-size: 1.2rem;
  font-weight: 700;
  width: 60px;
  outline: none;
}

.rounds-unit {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #666;
}

.rounds-hints {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  padding: 0 4px;
}

.hint-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: #666;
}

.hint-item svg {
  color: #999;
  flex-shrink: 0;
}

/* 高级选项样式 */
.advanced-options {
  margin: 0 20px; /* 添加左右边距，与按钮对齐 */
  border: 1px solid #CCC;
  border-bottom: none; /* 与按钮连接时去掉底边框，或者保留看效果，这里先保留完整边框，通过margin控制 */
  border-radius: 0;
  overflow: hidden;
  background: #FAFAFA;
}

.advanced-header {
  padding: 20px;
  background: #FAFAFA;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.2s;
  user-select: none;
  /* 移除 header 的边框，由外层 options 容器控制 */
}

.advanced-header:hover {
  background: #F0F0F0;
  border-color: #CCC;
}

.advanced-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 600;
  color: #333;
}

.advanced-title svg {
  color: #666;
}

.advanced-arrow {
  color: #999;
  transition: transform 0.3s;
}

.advanced-arrow.expanded {
  transform: rotate(180deg);
}

.advanced-content {
  padding: 16px;
  background: #FAFAFA;
  border-top: 1px solid #EAEAEA;
}

.manual-mode-option {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.checkbox-wrapper input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
  margin: 0;
  padding: 0;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid #CCC;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  position: relative;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkbox-custom {
  background-color: #FFFFFF;
  border-color: #000000;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkbox-custom::after {
  content: '';
  display: block;
  width: 6px;
  height: 10px;
  border: solid #000000;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  margin-bottom: 2px;
}

.checkbox-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

.mode-explanation {
  padding: 12px;
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  font-size: 0.8rem;
  line-height: 1.6;
  color: #666;
}

.mode-explanation p {
  margin: 0 0 8px 0;
}

.mode-explanation .explanation-title {
  font-weight: 600;
  color: #333;
  margin-top: 12px;
  margin-bottom: 6px;
}

.mode-explanation ul {
  margin: 0;
  padding-left: 20px;
}

.mode-explanation li {
  margin: 4px 0;
}

.mode-explanation .explanation-note {
  margin-top: 12px;
  padding: 8px;
  background: #FFF9E6;
  border-left: 3px solid #FFD700;
  color: #666;
  font-size: 0.75rem;
}

/* 过渡动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

/* 引导动画：微妙的边框脉冲 */
@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.2); }
  70% { box-shadow: 0 0 0 6px rgba(0, 0, 0, 0); }
  100% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); }
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .dashboard-section {
    flex-direction: column;
  }
  
  .hero-section {
    flex-direction: column;
  }
  
  .hero-left {
    padding-right: 0;
    margin-bottom: 40px;
  }
  
  .hero-logo {
    max-width: 200px;
    margin-bottom: 20px;
  }
}
</style>
