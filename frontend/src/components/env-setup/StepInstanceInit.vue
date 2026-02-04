<template>
  <!-- Step 01: 模拟实例初始化 -->
  <div class="step-card" :class="{ 'active': isActive, 'completed': isCompleted }">
    <div class="card-header">
      <div class="step-info">
        <span class="step-num">01</span>
        <span class="step-title">模拟实例初始化</span>
      </div>
      <div class="step-status">
        <span v-if="isCompleted" class="badge success">已完成</span>
        <span v-else class="badge processing">初始化</span>
      </div>
    </div>
    
    <div class="card-content">
      <p class="api-note">POST /api/simulation/create</p>
      <p class="description">
        新建simulation实例，拉取模拟世界参数模版
      </p>

      <div v-if="simulationId" class="info-card">
        <div class="info-row">
          <span class="info-label">Project ID</span>
          <span class="info-value mono">{{ projectData?.project_id }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Graph ID</span>
          <span class="info-value mono">{{ projectData?.graph_id }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Simulation ID</span>
          <span class="info-value mono">{{ simulationId }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Task ID</span>
          <span class="info-value mono">{{ taskId || '异步任务已完成' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  phase: {
    type: Number,
    required: true
  },
  simulationId: {
    type: String,
    default: ''
  },
  projectData: {
    type: Object,
    default: () => ({})
  },
  taskId: {
    type: String,
    default: null
  }
})

const isActive = computed(() => props.phase === 0)
const isCompleted = computed(() => props.phase > 0)
</script>

<style scoped>
.step-card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.step-card.active {
  border-color: #000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.step-card.completed {
  border-color: #10B981;
  background: #F0FDF4;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #F9FAFB;
  border-bottom: 1px solid #E5E7EB;
}

.step-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  color: #6B7280;
  background: #E5E7EB;
  padding: 4px 8px;
  border-radius: 4px;
}

.step-card.active .step-num,
.step-card.completed .step-num {
  background: #000;
  color: #fff;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: #1F2937;
}

.badge {
  font-size: 11px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
}

.badge.success {
  background: #D1FAE5;
  color: #059669;
}

.badge.processing {
  background: #000;
  color: #fff;
}

.badge.pending {
  background: #F3F4F6;
  color: #9CA3AF;
}

.card-content {
  padding: 20px;
}

.api-note {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #6B7280;
  margin: 0 0 8px 0;
}

.description {
  font-size: 13px;
  color: #4B5563;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.info-card {
  background: #F9FAFB;
  border-radius: 8px;
  padding: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #E5E7EB;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 12px;
  color: #6B7280;
}

.info-value {
  font-size: 12px;
  color: #1F2937;
}

.info-value.mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
}
</style>
