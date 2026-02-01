import service, { requestWithRetry } from './index'

/**
 * 创建模拟
 * @param {Object} data - { project_id, graph_id?, enable_twitter?, enable_reddit? }
 */
export const createSimulation = (data) => {
  return requestWithRetry(() => service.post('/api/simulation/create', data), 3, 1000)
}

/**
 * 准备模拟环境（异步任务）
 * @param {Object} data - { simulation_id, entity_types?, use_llm_for_profiles?, parallel_profile_count?, force_regenerate? }
 */
export const prepareSimulation = (data) => {
  return requestWithRetry(() => service.post('/api/simulation/prepare', data), 3, 1000)
}

/**
 * 获取准备状态
 * @param {Object} data - { task_id?, simulation_id? }
 */
export const getPrepareStatus = (data) => {
  return requestWithRetry(() => service.post('/api/simulation/prepare/status', data), 3, 1000)
}

/**
 * 开始模拟
 * @param {Object} data - { simulation_id, platform?, max_rounds? }
 */
export const startSimulation = (data) => {
  return requestWithRetry(() => service.post('/api/simulation/start', data), 3, 1000)
}

/**
 * 停止模拟
 * @param {Object} data - { simulation_id }
 */
export const stopSimulation = (data) => {
  return requestWithRetry(() => service.post('/api/simulation/stop', data), 3, 1000)
}

/**
 * 检查模拟是否可以恢复
 * @param {string} simulationId
 */
export const checkResumable = (simulationId) => {
  return requestWithRetry(() => service.get(`/api/simulation/${simulationId}/resumable`), 3, 1000)
}

/**
 * 获取运行状态
 * @param {string} simulationId
 */
export const getRunStatus = (simulationId) => {
  return requestWithRetry(() => service.get(`/api/simulation/${simulationId}/run-status`), 3, 1000)
}

/**
 * 获取运行状态详情（包含更多详细信息）
 * @param {string} simulationId
 */
export const getRunStatusDetail = (simulationId) => {
  return requestWithRetry(() => service.get(`/api/simulation/${simulationId}/run-status/detail`), 3, 1000)
}

/**
 * 获取模拟信息
 * @param {string} simulationId
 */
export const getSimulation = (simulationId) => {
  return requestWithRetry(() => service.get(`/api/simulation/${simulationId}`), 3, 1000)
}

/**
 * 获取模拟配置
 * @param {string} simulationId
 */
export const getSimulationConfig = (simulationId) => {
  return requestWithRetry(() => service.get(`/api/simulation/${simulationId}/config`), 3, 1000)
}

/**
 * 获取实时模拟配置状态（用于轮询配置生成进度）
 * @param {string} simulationId
 */
export const getSimulationConfigRealtime = (simulationId) => {
  return requestWithRetry(() => service.get(`/api/simulation/${simulationId}/config/realtime`), 3, 1000)
}

/**
 * 获取实时人设生成进度
 * @param {string} simulationId
 * @param {string} platform - 'twitter' 或 'reddit'
 */
export const getSimulationProfilesRealtime = (simulationId, platform) => {
  return requestWithRetry(() => service.get(`/api/simulation/${simulationId}/profiles/realtime`, {
    params: { platform }
  }), 3, 1000)
}

/**
 * 批量采访多个智能体
 * @param {string} simulationId
 * @param {Array} interviews - 采访列表 [{ agent_id, platform, prompt }]
 * @param {number} timeout - 超时时间（秒），默认根据采访数量动态计算
 */
export const interviewAgents = (simulationId, interviews, timeout = null) => {
  // 根据采访数量动态设置超时：每个 agent 约 15 秒，最少 120 秒，最多 900 秒
  const dynamicTimeout = timeout || Math.min(Math.max(interviews.length * 15, 120), 900)
  return requestWithRetry(() => service.post('/api/simulation/interview/batch', {
    simulation_id: simulationId,
    interviews,
    timeout: dynamicTimeout
  }), 1, 1000)  // 减少重试次数，避免长时间等待
}

/**
 * 获取环境状态
 * @param {string} simulationId
 */
export const getEnvStatus = (simulationId) => {
  return requestWithRetry(() => service.post('/api/simulation/env-status', {
    simulation_id: simulationId
  }), 3, 1000)
}

/**
 * 关闭模拟环境
 * @param {string} simulationId
 */
export const closeSimulationEnv = (simulationId) => {
  return requestWithRetry(() => service.post('/api/simulation/close-env', {
    simulation_id: simulationId
  }), 3, 1000)
}

/**
 * 获取模拟历史
 * @param {number} limit
 */
export const getSimulationHistory = (limit = 20) => {
  return requestWithRetry(() => service.get(`/api/simulation/history`, { params: { limit } }), 3, 1000)
}

/**
 * 列出所有模拟
 * @param {Object} params - { project_id? }
 */
export const listSimulations = (params) => {
  return requestWithRetry(() => service.get('/api/simulation/list', { params }), 3, 1000)
}

/**
 * 导出模拟数据
 * @param {string} simulationId
 */
export const exportSimulationData = (simulationId) => {
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001'}/api/simulation/${simulationId}/export`
}

/**
 * 获取模拟动作历史
 * @param {string} simulationId
 * @param {Object} params - { limit?, offset?, platform?, agent_id?, round_num? }
 */
export const getSimulationActions = (simulationId, params = {}) => {
  return requestWithRetry(() => service.get(`/api/simulation/${simulationId}/actions`, { params }), 3, 1000)
}
