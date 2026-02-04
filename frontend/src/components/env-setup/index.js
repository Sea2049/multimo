/**
 * env-setup 子组件导出入口
 * 
 * 将 Step2EnvSetup.vue 拆分为多个子组件，提高可维护性
 */

export { default as StepInstanceInit } from './StepInstanceInit.vue'
export { default as StepAgentProfiles } from './StepAgentProfiles.vue'
export { default as StepSimulationConfig } from './StepSimulationConfig.vue'
export { default as StepActionOrchestration } from './StepActionOrchestration.vue'
export { default as StepAutoPilotConfig } from './StepAutoPilotConfig.vue'
export { default as ProfileDetailModal } from './ProfileDetailModal.vue'
