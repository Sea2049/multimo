<template>
  <!-- 
    状态徽章组件
    
    用于显示各种状态标签，支持预设状态和自定义颜色。
    
    Props:
      - status: 状态值
      - size: 尺寸 (small/medium/large)
      - type: 预设类型 (success/warning/error/info/pending)
  -->
  <span 
    class="status-badge"
    :class="[`status-${computedType}`, `size-${size}`]"
  >
    <span v-if="showDot" class="status-dot"></span>
    <slot>{{ label || status }}</slot>
  </span>
</template>

<script setup>
/**
 * 状态徽章组件
 * 
 * 用于统一项目中的状态显示，替代分散的状态样式。
 */

import { computed } from 'vue'

const props = defineProps({
  // 状态值
  status: {
    type: String,
    default: ''
  },
  // 显示标签（可选，默认使用 status）
  label: {
    type: String,
    default: ''
  },
  // 预设类型
  type: {
    type: String,
    default: '',
    validator: (v) => ['', 'success', 'warning', 'error', 'info', 'pending'].includes(v)
  },
  // 尺寸
  size: {
    type: String,
    default: 'medium',
    validator: (v) => ['small', 'medium', 'large'].includes(v)
  },
  // 是否显示圆点
  showDot: {
    type: Boolean,
    default: true
  }
})

// 状态映射表
const statusTypeMap = {
  // 成功状态
  completed: 'success',
  success: 'success',
  ready: 'success',
  done: 'success',
  active: 'success',
  running: 'success',
  
  // 警告状态
  warning: 'warning',
  preparing: 'warning',
  generating: 'warning',
  paused: 'warning',
  
  // 错误状态
  error: 'error',
  failed: 'error',
  stopped: 'error',
  
  // 信息状态
  info: 'info',
  
  // 等待状态
  pending: 'pending',
  idle: 'pending',
  created: 'pending'
}

// 计算类型
const computedType = computed(() => {
  if (props.type) return props.type
  return statusTypeMap[props.status?.toLowerCase()] || 'info'
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 500;
  white-space: nowrap;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 尺寸 */
.size-small {
  font-size: 11px;
  padding: 2px 8px;
}

.size-small .status-dot {
  width: 5px;
  height: 5px;
}

.size-medium {
  font-size: 12px;
  padding: 4px 10px;
}

.size-large {
  font-size: 14px;
  padding: 6px 14px;
}

.size-large .status-dot {
  width: 8px;
  height: 8px;
}

/* 成功状态 */
.status-success {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.status-success .status-dot {
  background: #10b981;
}

/* 警告状态 */
.status-warning {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.status-warning .status-dot {
  background: #f59e0b;
  animation: pulse 2s infinite;
}

/* 错误状态 */
.status-error {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.status-error .status-dot {
  background: #ef4444;
}

/* 信息状态 */
.status-info {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.status-info .status-dot {
  background: #3b82f6;
}

/* 等待状态 */
.status-pending {
  background: rgba(107, 114, 128, 0.1);
  color: #4b5563;
}

.status-pending .status-dot {
  background: #9ca3af;
}

/* 脉冲动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
