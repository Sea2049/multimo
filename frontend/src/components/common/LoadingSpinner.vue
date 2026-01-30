<template>
  <!-- 
    加载动画组件
    
    Props:
      - size: 尺寸 (small/medium/large)
      - color: 颜色
      - text: 加载文本
      - fullscreen: 是否全屏覆盖
  -->
  <div 
    class="loading-spinner"
    :class="{ 'loading-fullscreen': fullscreen }"
  >
    <div 
      class="spinner"
      :class="[`spinner-${size}`]"
      :style="spinnerStyle"
    ></div>
    <span v-if="text" class="loading-text">{{ text }}</span>
  </div>
</template>

<script setup>
/**
 * 加载动画组件
 * 
 * 提供统一的加载状态显示，支持多种尺寸和场景。
 */

import { computed } from 'vue'

const props = defineProps({
  // 尺寸
  size: {
    type: String,
    default: 'medium',
    validator: (v) => ['small', 'medium', 'large'].includes(v)
  },
  // 颜色
  color: {
    type: String,
    default: '#667eea'
  },
  // 加载文本
  text: {
    type: String,
    default: ''
  },
  // 是否全屏覆盖
  fullscreen: {
    type: Boolean,
    default: false
  }
})

const spinnerStyle = computed(() => ({
  borderTopColor: props.color
}))
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.loading-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  z-index: 9999;
}

.spinner {
  border-radius: 50%;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  animation: spin 0.8s linear infinite;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

.spinner-medium {
  width: 32px;
  height: 32px;
  border-width: 3px;
}

.spinner-large {
  width: 48px;
  height: 48px;
  border-width: 4px;
}

.loading-text {
  font-size: 14px;
  color: #6b7280;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
