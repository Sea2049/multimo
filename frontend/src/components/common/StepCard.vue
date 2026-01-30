<template>
  <!-- 
    步骤卡片组件
    
    用于流程中的每个步骤展示，支持状态、标题、描述和操作按钮。
    
    Props:
      - step: 步骤编号
      - title: 标题
      - description: 描述
      - status: 状态 (pending/active/completed/error)
      - expanded: 是否展开
      - collapsible: 是否可折叠
  -->
  <div 
    class="step-card"
    :class="[`status-${status}`, { 'is-expanded': expanded, 'is-collapsible': collapsible }]"
  >
    <!-- 头部 -->
    <div 
      class="step-header"
      @click="handleHeaderClick"
    >
      <div class="step-indicator">
        <span class="step-number">{{ step }}</span>
        <span v-if="status === 'completed'" class="step-check">✓</span>
      </div>
      <div class="step-info">
        <h3 class="step-title">{{ title }}</h3>
        <p v-if="description" class="step-description">{{ description }}</p>
      </div>
      <div class="step-status">
        <StatusBadge v-if="statusLabel" :status="status" :label="statusLabel" />
        <svg 
          v-if="collapsible"
          class="collapse-icon"
          :class="{ 'is-expanded': expanded }"
          width="20" 
          height="20" 
          viewBox="0 0 20 20"
        >
          <path 
            d="M5 7.5L10 12.5L15 7.5" 
            stroke="currentColor" 
            stroke-width="2" 
            stroke-linecap="round" 
            stroke-linejoin="round"
            fill="none"
          />
        </svg>
      </div>
    </div>
    
    <!-- 内容区域 -->
    <transition name="expand">
      <div v-if="expanded || !collapsible" class="step-content">
        <slot></slot>
      </div>
    </transition>
    
    <!-- 底部操作区 -->
    <div v-if="$slots.actions" class="step-actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
/**
 * 步骤卡片组件
 * 
 * 用于流程向导中的步骤展示，提供统一的样式和交互。
 */

import StatusBadge from './StatusBadge.vue'

const props = defineProps({
  // 步骤编号
  step: {
    type: [Number, String],
    required: true
  },
  // 标题
  title: {
    type: String,
    required: true
  },
  // 描述
  description: {
    type: String,
    default: ''
  },
  // 状态
  status: {
    type: String,
    default: 'pending',
    validator: (v) => ['pending', 'active', 'completed', 'error'].includes(v)
  },
  // 状态标签文本
  statusLabel: {
    type: String,
    default: ''
  },
  // 是否展开
  expanded: {
    type: Boolean,
    default: true
  },
  // 是否可折叠
  collapsible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:expanded'])

const handleHeaderClick = () => {
  if (props.collapsible) {
    emit('update:expanded', !props.expanded)
  }
}
</script>

<style scoped>
.step-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: all 0.3s;
}

.step-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* 状态样式 */
.step-card.status-active {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.step-card.status-completed {
  border-color: #10b981;
}

.step-card.status-error {
  border-color: #ef4444;
}

/* 头部 */
.step-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  cursor: default;
}

.is-collapsible .step-header {
  cursor: pointer;
}

.is-collapsible .step-header:hover {
  background: #f9fafb;
}

/* 步骤指示器 */
.step-indicator {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f3f4f6;
  flex-shrink: 0;
}

.status-active .step-indicator {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.status-completed .step-indicator {
  background: #10b981;
}

.status-error .step-indicator {
  background: #ef4444;
}

.step-number {
  font-size: 16px;
  font-weight: 600;
  color: #6b7280;
}

.status-active .step-number,
.status-completed .step-number,
.status-error .step-number {
  color: #fff;
}

.step-check {
  position: absolute;
  font-size: 18px;
  color: #fff;
}

/* 信息区域 */
.step-info {
  flex: 1;
  min-width: 0;
}

.step-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.step-description {
  margin: 4px 0 0;
  font-size: 13px;
  color: #6b7280;
}

/* 状态区域 */
.step-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.collapse-icon {
  color: #9ca3af;
  transition: transform 0.3s;
}

.collapse-icon.is-expanded {
  transform: rotate(180deg);
}

/* 内容区域 */
.step-content {
  padding: 0 20px 20px;
  border-top: 1px solid #f3f4f6;
}

/* 操作区域 */
.step-actions {
  padding: 16px 20px;
  background: #f9fafb;
  border-top: 1px solid #f3f4f6;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 展开动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
