/**
 * 邀请码管理 API 模块
 */

import service from './index'

/**
 * 获取邀请码列表
 * @param {Object} params - 查询参数
 * @param {boolean} [params.includeInactive=true] - 是否包含已禁用的邀请码
 * @param {number} [params.limit=100] - 返回数量限制
 * @returns {Promise<{invitations: Array, total: number}>}
 */
export async function list(params = {}) {
  const response = await service.get('/api/v1/invitations', {
    params: {
      include_inactive: params.includeInactive ?? true,
      limit: params.limit ?? 100
    }
  })
  return response.data
}

/**
 * 创建邀请码
 * @param {Object} data - 邀请码数据
 * @param {number} [data.maxUses=1] - 使用次数上限
 * @param {string} [data.expiresAt] - 过期时间（ISO 格式）
 * @param {string} [data.note] - 备注
 * @param {string} [data.code] - 自定义邀请码（可选）
 * @returns {Promise<{invitation: Object}>}
 */
export async function create(data = {}) {
  const response = await service.post('/api/v1/invitations', {
    max_uses: data.maxUses ?? 1,
    expires_at: data.expiresAt,
    note: data.note,
    code: data.code
  })
  return response.data
}

/**
 * 获取单个邀请码详情
 * @param {number} id - 邀请码 ID
 * @returns {Promise<{invitation: Object}>}
 */
export async function get(id) {
  const response = await service.get(`/api/v1/invitations/${id}`)
  return response.data
}

/**
 * 更新邀请码
 * @param {number} id - 邀请码 ID
 * @param {Object} data - 更新数据
 * @param {number} [data.maxUses] - 使用次数上限
 * @param {string} [data.expiresAt] - 过期时间
 * @param {boolean} [data.isActive] - 是否启用
 * @param {string} [data.note] - 备注
 * @returns {Promise<{invitation: Object}>}
 */
export async function update(id, data = {}) {
  const payload = {}
  
  if (data.maxUses !== undefined) {
    payload.max_uses = data.maxUses
  }
  if (data.expiresAt !== undefined) {
    payload.expires_at = data.expiresAt
  }
  if (data.isActive !== undefined) {
    payload.is_active = data.isActive
  }
  if (data.note !== undefined) {
    payload.note = data.note
  }
  
  const response = await service.put(`/api/v1/invitations/${id}`, payload)
  return response.data
}

/**
 * 删除邀请码
 * @param {number} id - 邀请码 ID
 * @returns {Promise<void>}
 */
export async function remove(id) {
  await service.delete(`/api/v1/invitations/${id}`)
}

/**
 * 切换邀请码状态（启用/禁用）
 * @param {number} id - 邀请码 ID
 * @param {boolean} isActive - 是否启用
 * @returns {Promise<{invitation: Object}>}
 */
export async function toggleStatus(id, isActive) {
  return update(id, { isActive })
}

export default {
  list,
  create,
  get,
  update,
  remove,
  toggleStatus
}
