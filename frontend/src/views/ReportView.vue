<template>
  <div class="main-view">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <div class="brand" @click="router.push('/')">MULTIMO</div>
      </div>
      
      <div class="header-center">
        <div class="view-switcher">
          <button 
            v-for="mode in ['graph', 'split', 'workbench']" 
            :key="mode"
            class="switch-btn"
            :class="{ active: viewMode === mode }"
            @click="viewMode = mode"
          >
            {{ { graph: '图谱', split: '双栏', workbench: '工作台' }[mode] }}
          </button>
        </div>
      </div>

      <div class="header-right">
        <div class="workflow-step">
          <span class="step-num">Step 4/5</span>
          <span class="step-name">报告生成</span>
        </div>
        <div class="step-divider"></div>
        <button v-if="projectData" class="export-btn secondary" @click="handleAddDocuments" title="补充文档到知识库">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="12" y1="18" x2="12" y2="12"></line>
            <line x1="9" y1="15" x2="15" y2="15"></line>
          </svg>
          补充文档
        </button>
        <button v-if="simulationId" class="export-btn secondary" @click="handleExportReport" title="导出报告Markdown">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Export Report
        </button>
        <button v-if="simulationId" class="export-btn" @click="handleFullExport" title="导出全量数据">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Export All Data
        </button>
        <span class="status-indicator" :class="statusClass">
          <span class="dot"></span>
          {{ statusText }}
        </span>
      </div>
    </header>

    <!-- 补充文档上传弹窗 -->
    <div v-if="showAddDocModal" class="modal-overlay" @click.self="closeAddDocModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>补充文档到知识库</h3>
          <button class="close-btn" @click="closeAddDocModal">×</button>
        </div>
        
        <div class="modal-body">
          <p class="modal-desc">上传新文档将自动更新 Agent 的知识库，Agent 在下次思考时即可检索到新知识。</p>
          
          <div 
            class="upload-zone"
            :class="{ 'drag-over': isDragOver, 'has-files': uploadFiles.length > 0 }"
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
            />
            
            <div v-if="uploadFiles.length === 0" class="upload-placeholder">
              <div class="upload-icon">↑</div>
              <div class="upload-title">拖拽文件上传</div>
              <div class="upload-hint">或点击浏览文件系统 (支持 PDF, MD, TXT)</div>
            </div>
            
            <div v-else class="file-list">
              <div v-for="(file, index) in uploadFiles" :key="index" class="file-item">
                <span class="file-icon">📄</span>
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
                <button @click.stop="removeFile(index)" class="remove-btn">×</button>
              </div>
            </div>
          </div>
          
          <div v-if="uploadStatus" class="upload-status" :class="uploadStatus.type">
            {{ uploadStatus.message }}
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeAddDocModal" :disabled="uploading">取消</button>
          <button 
            class="btn-submit" 
            @click="submitDocuments" 
            :disabled="uploadFiles.length === 0 || uploading"
          >
            <span v-if="!uploading">开始上传</span>
            <span v-else>上传中...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <main class="content-area">
      <!-- Left Panel: Graph -->
      <div class="panel-wrapper left" :style="leftPanelStyle">
        <GraphPanel 
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="4"
          :isSimulating="false"
          @refresh="refreshGraph"
          @toggle-maximize="toggleMaximize('graph')"
        />
      </div>

      <!-- Right Panel: Step4 报告生成 -->
      <div class="panel-wrapper right" :style="rightPanelStyle">
        <Step4Report
          :reportId="currentReportId"
          :simulationId="simulationId"
          :systemLogs="systemLogs"
          @add-log="addLog"
          @update-status="updateStatus"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../components/GraphPanel.vue'
import Step4Report from '../components/Step4Report.vue'
import { getProject, getGraphData, addDocuments, getTaskStatus } from '../api/graph'
import { getSimulation, exportSimulationData } from '../api/simulation'
import { getReport } from '../api/report'

const route = useRoute()
const router = useRouter()

// Props
const props = defineProps({
  reportId: String
})

// Layout State - 默认切换到工作台视角
const viewMode = ref('workbench')

// Data State
const currentReportId = ref(route.params.reportId)
const simulationId = ref(null)
const projectData = ref(null)
const graphData = ref(null)
const graphLoading = ref(false)
const systemLogs = ref([])
const currentStatus = ref('processing') // processing | completed | error

// 补充文档相关状态
const showAddDocModal = ref(false)
const uploadFiles = ref([])
const isDragOver = ref(false)
const uploading = ref(false)
const uploadStatus = ref(null)
const fileInput = ref(null)

// --- Computed Layout Styles ---
const leftPanelStyle = computed(() => {
  if (viewMode.value === 'graph') return { width: '100%', opacity: 1, transform: 'translateX(0)' }
  if (viewMode.value === 'workbench') return { width: '0%', opacity: 0, transform: 'translateX(-20px)' }
  return { width: '50%', opacity: 1, transform: 'translateX(0)' }
})

const rightPanelStyle = computed(() => {
  if (viewMode.value === 'workbench') return { width: '100%', opacity: 1, transform: 'translateX(0)' }
  if (viewMode.value === 'graph') return { width: '0%', opacity: 0, transform: 'translateX(20px)' }
  return { width: '50%', opacity: 1, transform: 'translateX(0)' }
})

// --- Status Computed ---
const statusClass = computed(() => {
  return currentStatus.value
})

const statusText = computed(() => {
  if (currentStatus.value === 'error') return 'Error'
  if (currentStatus.value === 'completed') return 'Completed'
  return 'Generating'
})

// --- Helpers ---
const addLog = (msg) => {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + new Date().getMilliseconds().toString().padStart(3, '0')
  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 200) {
    systemLogs.value.shift()
  }
}

const updateStatus = (status) => {
  currentStatus.value = status
}

// --- Layout Methods ---
const handleExportReport = () => {
  if (!simulationId.value) return
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001'
  const url = `${baseUrl}/api/v1/report/${simulationId.value}/download?format=markdown`
  window.open(url, '_blank')
}

const handleFullExport = () => {
  if (!simulationId.value) return
  const url = exportSimulationData(simulationId.value)
  window.open(url, '_blank')
}

const toggleMaximize = (target) => {
  if (viewMode.value === target) {
    viewMode.value = 'split'
  } else {
    viewMode.value = target
  }
}

// --- 补充文档相关方法 ---
const handleAddDocuments = () => {
  showAddDocModal.value = true
  uploadFiles.value = []
  uploadStatus.value = null
}

const closeAddDocModal = () => {
  if (uploading.value) return
  showAddDocModal.value = false
  uploadFiles.value = []
  uploadStatus.value = null
}

const triggerFileInput = () => {
  if (!uploading.value) {
    fileInput.value?.click()
  }
}

const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

const handleDragOver = (e) => {
  if (!uploading.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e) => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  isDragOver.value = false
  if (uploading.value) return
  
  const droppedFiles = Array.from(e.dataTransfer.files)
  addFiles(droppedFiles)
}

const addFiles = (newFiles) => {
  const validFiles = newFiles.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  uploadFiles.value.push(...validFiles)
}

const removeFile = (index) => {
  uploadFiles.value.splice(index, 1)
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const submitDocuments = async () => {
  if (uploadFiles.value.length === 0 || !projectData.value) return
  
  uploading.value = true
  uploadStatus.value = { type: 'info', message: '正在上传文档...' }
  
  try {
    const formData = new FormData()
    uploadFiles.value.forEach(file => {
      formData.append('files', file)
    })
    
    const res = await addDocuments(projectData.value.project_id, formData)
    
    if (res.success) {
      uploadStatus.value = { type: 'success', message: '文档上传成功！正在处理...' }
      addLog(`文档上传成功，任务ID: ${res.data.task_id}`)
      
      // 轮询任务状态
      const taskId = res.data.task_id
      await pollTaskStatus(taskId)
      
      uploadStatus.value = { type: 'success', message: '文档已成功添加到知识库！' }
      
      // 2秒后关闭弹窗并刷新图谱
      setTimeout(() => {
        closeAddDocModal()
        refreshGraph()
      }, 2000)
    } else {
      uploadStatus.value = { type: 'error', message: `上传失败: ${res.error}` }
    }
  } catch (err) {
    uploadStatus.value = { type: 'error', message: `上传异常: ${err.message}` }
    addLog(`文档上传失败: ${err.message}`)
  } finally {
    uploading.value = false
  }
}

const pollTaskStatus = async (taskId, maxAttempts = 60) => {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const res = await getTaskStatus(taskId)
      if (res.success && res.data) {
        const task = res.data
        
        if (task.status === 'completed') {
          addLog('文档处理完成')
          return true
        } else if (task.status === 'failed') {
          throw new Error(task.error || '任务失败')
        }
        
        // 更新进度
        if (task.message) {
          uploadStatus.value = { type: 'info', message: task.message }
        }
      }
    } catch (err) {
      console.error('轮询任务状态失败:', err)
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000))
  }
  
  throw new Error('任务超时')
}

// --- Data Logic ---
const loadReportData = async () => {
  try {
    addLog(`加载报告数据: ${currentReportId.value}`)
    
    // 获取 report 信息以获取 simulation_id
    const reportRes = await getReport(currentReportId.value)
    if (reportRes.success && reportRes.data) {
      const reportData = reportRes.data
      simulationId.value = reportData.simulation_id
      
      if (simulationId.value) {
        // 获取 simulation 信息
        const simRes = await getSimulation(simulationId.value)
        if (simRes.success && simRes.data) {
          const simData = simRes.data
          
          // 获取 project 信息
          if (simData.project_id) {
            const projRes = await getProject(simData.project_id)
            if (projRes.success && projRes.data) {
              projectData.value = projRes.data
              addLog(`项目加载成功: ${projRes.data.project_id}`)
              
              // 获取 graph 数据
              if (projRes.data.graph_id) {
                await loadGraph(projRes.data.graph_id)
              }
            }
          }
        }
      }
    } else {
      addLog(`获取报告信息失败: ${reportRes.error || '未知错误'}`)
    }
  } catch (err) {
    addLog(`加载异常: ${err.message}`)
  }
}

const loadGraph = async (graphId) => {
  graphLoading.value = true
  
  try {
    const res = await getGraphData(graphId)
    if (res.success) {
      graphData.value = res.data
      addLog('图谱数据加载成功')
    }
  } catch (err) {
    addLog(`图谱加载失败: ${err.message}`)
  } finally {
    graphLoading.value = false
  }
}

const refreshGraph = () => {
  if (projectData.value?.graph_id) {
    loadGraph(projectData.value.graph_id)
  }
}

// Watch route params
watch(() => route.params.reportId, (newId) => {
  if (newId && newId !== currentReportId.value) {
    currentReportId.value = newId
    loadReportData()
  }
}, { immediate: true })

onMounted(() => {
  addLog('ReportView 初始化')
  loadReportData()
})
</script>

<style scoped>
.main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #FFF;
  overflow: hidden;
  font-family: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
}

/* Header */
.app-header {
  height: 60px;
  border-bottom: 1px solid #EAEAEA;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #FFF;
  z-index: 100;
  position: relative;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.brand {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 18px;
  letter-spacing: 1px;
  cursor: pointer;
}

.view-switcher {
  display: flex;
  background: #F5F5F5;
  padding: 4px;
  border-radius: 6px;
  gap: 4px;
}

.switch-btn {
  border: none;
  background: transparent;
  padding: 6px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.switch-btn.active {
  background: #FFF;
  color: #000;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #000;
  color: #FFF;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 12px;
}

.export-btn:hover {
  background: #333;
  transform: translateY(-1px);
}

.export-btn.secondary {
  background: #FFF;
  color: #333;
  border: 1px solid #E0E0E0;
}

.export-btn.secondary:hover {
  background: #F5F5F5;
  border-color: #CCC;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.workflow-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #999;
}

.step-name {
  font-weight: 700;
  color: #000;
}

.step-divider {
  width: 1px;
  height: 14px;
  background-color: #E0E0E0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #CCC;
}

.status-indicator.processing .dot { background: #FF9800; animation: pulse 1s infinite; }
.status-indicator.completed .dot { background: #4CAF50; }
.status-indicator.error .dot { background: #F44336; }

@keyframes pulse { 50% { opacity: 0.5; } }

/* Content */
.content-area {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.panel-wrapper {
  height: 100%;
  overflow: hidden;
  transition: width 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.3s ease, transform 0.3s ease;
  will-change: width, opacity, transform;
}

.panel-wrapper.left {
  border-right: 1px solid #EAEAEA;
}

/* 补充文档弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: #FFF;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #EAEAEA;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #F5F5F5;
  color: #333;
}

.modal-body {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.modal-desc {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.upload-zone {
  border: 2px dashed #DDD;
  border-radius: 8px;
  min-height: 200px;
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

.upload-zone.drag-over {
  background: #E3F2FD;
  border-color: #2196F3;
}

.upload-zone.has-files {
  cursor: default;
  background: #FFF;
  border-style: solid;
  border-color: #E0E0E0;
}

.upload-placeholder {
  text-align: center;
  padding: 40px 20px;
}

.upload-icon {
  width: 48px;
  height: 48px;
  border: 2px solid #DDD;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #999;
  font-size: 24px;
  border-radius: 4px;
}

.upload-title {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 8px;
  color: #333;
}

.upload-hint {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #999;
}

.file-list {
  width: 100%;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  background: #F9F9F9;
  padding: 12px 16px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  transition: all 0.2s;
}

.file-item:hover {
  background: #F0F0F0;
}

.file-icon {
  font-size: 18px;
  margin-right: 12px;
}

.file-name {
  flex: 1;
  margin-right: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: #999;
  font-size: 11px;
  margin-right: 12px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 20px;
  color: #999;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: #E0E0E0;
  color: #333;
}

.upload-status {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
}

.upload-status.info {
  background: #E3F2FD;
  color: #1976D2;
  border: 1px solid #BBDEFB;
}

.upload-status.success {
  background: #E8F5E9;
  color: #388E3C;
  border: 1px solid #C8E6C9;
}

.upload-status.error {
  background: #FFEBEE;
  color: #D32F2F;
  border: 1px solid #FFCDD2;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #EAEAEA;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel,
.btn-submit {
  padding: 10px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-cancel {
  background: #F5F5F5;
  color: #666;
}

.btn-cancel:hover:not(:disabled) {
  background: #E0E0E0;
}

.btn-submit {
  background: #000;
  color: #FFF;
}

.btn-submit:hover:not(:disabled) {
  background: #333;
  transform: translateY(-1px);
}

.btn-cancel:disabled,
.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

</style>
