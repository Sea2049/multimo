/**
 * 通用组件导出模块
 * 
 * 统一导出所有通用 UI 组件，方便项目中使用。
 * 
 * 使用示例:
 *   import { Modal, StatusBadge, LoadingSpinner, StepCard } from '@/components/common'
 */

import Modal from './Modal.vue'
import StatusBadge from './StatusBadge.vue'
import LoadingSpinner from './LoadingSpinner.vue'
import StepCard from './StepCard.vue'

export {
  Modal,
  StatusBadge,
  LoadingSpinner,
  StepCard
}

export default {
  Modal,
  StatusBadge,
  LoadingSpinner,
  StepCard
}
