/**
 * 用户认证 API 模块
 */

import service from './index'

const TOKEN_KEY = 'multimo_token'
const USER_KEY = 'multimo_user'

/**
 * 用户注册
 * @param {string} username - 用户名
 * @param {string} email - 邮箱
 * @param {string} password - 密码
 * @param {string} invitationCode - 邀请码
 * @returns {Promise<{user: Object, token: string}>}
 */
export async function register(username, email, password, invitationCode) {
  const response = await service.post('/api/v1/auth/register', {
    username,
    email,
    password,
    invitation_code: invitationCode
  })
  
  if (response.success && response.data) {
    // 保存 token 和用户信息
    setToken(response.data.token)
    setUser(response.data.user)
  }
  
  return response.data
}

/**
 * 用户登录
 * @param {string} email - 邮箱
 * @param {string} password - 密码
 * @returns {Promise<{user: Object, token: string}>}
 */
export async function login(email, password) {
  const response = await service.post('/api/v1/auth/login', {
    email,
    password
  })
  
  if (response.success && response.data) {
    // 保存 token 和用户信息
    setToken(response.data.token)
    setUser(response.data.user)
  }
  
  return response.data
}

/**
 * 获取当前用户信息
 * @returns {Promise<{user: Object}>}
 */
export async function getMe() {
  const response = await service.get('/api/v1/auth/me')
  
  if (response.success && response.data) {
    // 更新本地用户信息
    setUser(response.data.user)
  }
  
  return response.data
}

/**
 * 刷新 Token
 * @returns {Promise<{token: string}>}
 */
export async function refreshToken() {
  const response = await service.post('/api/v1/auth/refresh')
  
  if (response.success && response.data) {
    setToken(response.data.token)
  }
  
  return response.data
}

/**
 * 登出
 */
export function logout() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

/**
 * 获取存储的 Token
 * @returns {string|null}
 */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 设置 Token
 * @param {string} token
 */
export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

/**
 * 获取存储的用户信息
 * @returns {Object|null}
 */
export function getUser() {
  const userStr = localStorage.getItem(USER_KEY)
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }
  return null
}

/**
 * 设置用户信息
 * @param {Object} user
 */
export function setUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

/**
 * 检查是否已登录
 * @returns {boolean}
 */
export function isLoggedIn() {
  return !!getToken()
}

/**
 * 检查是否是管理员
 * @returns {boolean}
 */
export function isAdmin() {
  const user = getUser()
  return user?.role === 'admin'
}

export default {
  register,
  login,
  getMe,
  refreshToken,
  logout,
  getToken,
  setToken,
  getUser,
  setUser,
  isLoggedIn,
  isAdmin
}
