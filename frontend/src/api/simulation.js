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
 * @param {string} taskId
 */
export const getPrepareStatus = (taskId) => {
  return requestWithRetry(() => service.get(`/api/simulation/prepare/status/${taskId}`), 3, 1000)
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
 * 获取运行状态
 * @param {string} simulationId
 */
export const getRunStatus = (simulationId) => {
  return requestWithRetry(() => service.get(`/api/simulation/${simulationId}/run-status`), 3, 1000)
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
 * 获取模拟历史
 * @param {number} limit
 */
export const getSimulationHistory = (limit = 20) => {
  return requestWithRetry(() => service.get(`/api/simulation/history`, { params: { limit } }), 3, 1000)
}

/**
 * 导出模拟数据
 * @param {string} simulationId
 */
export const exportSimulationData = (simulationId) => {
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001'}/api/simulation/${simulationId}/export`
}
