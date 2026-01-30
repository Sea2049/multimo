<template>
  <!-- 
    通用模态框组件
    
    Props:
      - visible: 控制显示/隐藏
      - title: 模态框标题
      - width: 模态框宽度 (默认 600px)
      - showClose: 是否显示关闭按钮 (默认 true)
      - closeOnClickOverlay: 点击遮罩层是否关闭 (默认 true)
    
    Events:
      - update:visible: 双向绑定
      - close: 关闭时触发
    
    Slots:
      - default: 内容区域
      - header: 自定义头部
      - footer: 自定义底部
  -->
  <teleport to="body">
    <transition name="modal-fade">
      <div 
        v-if="visible" 
        class="modal-overlay"
        @click.self="handleOverlayClick"
      >
        <div 
          class="modal-container"
          :style="{ maxWidth: width }"
        >
          <!-- 头部 -->
          <div class="modal-header">
            <slot name="header">
              <h3 class="modal-title">{{ title }}</h3>
            </slot>
            <button 
              v-if="showClose"
              class="modal-close-btn"
              @click="handleClose"
              aria-label="关闭"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          
          <!-- 内容 -->
          <div class="modal-body">
            <slot></slot>
          </div>
          
          <!-- 底部 -->
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
/**
 * 通用模态框组件
 * 
 * 用于替代项目中分散的模态框实现，提供统一的样式和行为。
 */

import { watch } from 'vue'

const props = defineProps({
  // 是否显示模态框
  visible: {
    type: Boolean,
    default: false
  },
  // 模态框标题
  title: {
    type: String,
    default: ''
  },
  // 模态框宽度
  width: {
    type: String,
    default: '600px'
  },
  // 是否显示关闭按钮
  showClose: {
    type: Boolean,
    default: true
  },
  // 点击遮罩层是否关闭
  closeOnClickOverlay: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:visible', 'close'])

// 处理关闭
const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

// 处理遮罩层点击
const handleOverlayClick = () => {
  if (props.closeOnClickOverlay) {
    handleClose()
  }
}

// 监听 ESC 键关闭
watch(() => props.visible, (newVal) => {
  if (newVal) {
    document.addEventListener('keydown', handleEscKey)
    document.body.style.overflow = 'hidden'
  } else {
    document.removeEventListener('keydown', handleEscKey)
    document.body.style.overflow = ''
  }
})

const handleEscKey = (e) => {
  if (e.key === 'Escape') {
    handleClose()
  }
}
</script>

<style scoped>
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
  padding: 20px;
}

.modal-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.modal-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 过渡动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-active .modal-container,
.modal-fade-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-container,
.modal-fade-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
