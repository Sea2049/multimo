<template>
  <TransitionGroup name="error-alert" tag="div" class="error-alert-container">
    <div
      v-for="(item, index) in alerts"
      :key="item.id"
      class="error-alert"
      :class="[`error-${item.type}`, { 'has-retry': item.showRetry }]"
    >
      <div class="alert-icon">
        <span v-if="item.type === 'error'">⚠</span>
        <span v-else-if="item.type === 'warning'">⚡</span>
        <span v-else>ℹ</span>
      </div>
      
      <div class="alert-content">
        <div class="alert-message">{{ item.message }}</div>
        <div v-if="item.suggestion" class="alert-suggestion">{{ item.suggestion }}</div>
      </div>
      
      <div class="alert-actions">
        <button
          v-if="item.showRetry"
          class="retry-btn"
          @click="handleRetry(item)"
        >
          重试
        </button>
        <button class="close-btn" @click="removeAlert(item.id)" aria-label="关闭提示">
          ✕
        </button>
      </div>
    </div>
  </TransitionGroup>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  maxAlerts: {
    type: Number,
    default: 3
  }
})

const emit = defineEmits(['retry'])

const alerts = ref([])
let alertId = 0

const addAlert = (options) => {
  const {
    type = 'error',
    message,
    suggestion = '',
    showRetry = false,
    retryFn = null,
    duration = 0
  } = options
  
  if (alerts.value.length >= props.maxAlerts) {
    alerts.value.shift()
  }
  
  const id = ++alertId
  alerts.value.push({
    id,
    type,
    message,
    suggestion,
    showRetry,
    retryFn
  })
  
  if (duration > 0) {
    setTimeout(() => {
      removeAlert(id)
    }, duration)
  }
  
  return id
}

const removeAlert = (id) => {
  const index = alerts.value.findIndex(a => a.id === id)
  if (index > -1) {
    alerts.value.splice(index, 1)
  }
}

const handleRetry = (item) => {
  emit('retry', item)
  removeAlert(item.id)
}

const clearAll = () => {
  alerts.value = []
}

defineExpose({
  addAlert,
  removeAlert,
  clearAll
})

onUnmounted(() => {
  clearAll()
})
</script>

<style scoped>
.error-alert-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
}

.error-alert {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background: white;
  border-left: 4px solid;
}

.error-alert.error-error {
  border-left-color: #f5222d;
  background: #fff2f0;
}

.error-alert.error-warning {
  border-left-color: #faad14;
  background: #fffbe6;
}

.error-alert.error-info {
  border-left-color: #1890ff;
  background: #e6f7ff;
}

.alert-icon {
  font-size: 18px;
  margin-right: 12px;
  flex-shrink: 0;
}

.error-error .alert-icon {
  color: #f5222d;
}

.error-warning .alert-icon {
  color: #faad14;
}

.error-info .alert-icon {
  color: #1890ff;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-message {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  line-height: 1.4;
}

.alert-suggestion {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  line-height: 1.4;
}

.alert-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
  flex-shrink: 0;
}

.retry-btn {
  padding: 4px 12px;
  border: none;
  border-radius: 4px;
  background: #1890ff;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #40a9ff;
}

.close-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  color: #666;
}

.error-alert-enter-active,
.error-alert-leave-active {
  transition: all 0.3s ease;
}

.error-alert-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.error-alert-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.error-alert-move {
  transition: transform 0.3s ease;
}
</style>
