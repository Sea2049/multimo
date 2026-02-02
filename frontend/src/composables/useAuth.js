/**
 * 用户认证状态管理 Composable
 * 
 * 提供响应式的认证状态和认证操作方法
 */

import { ref, computed, readonly } from 'vue'
import { useRouter } from 'vue-router'
import authApi from '../api/auth'

// 全局响应式状态
const user = ref(null)
const loading = ref(false)
const initialized = ref(false)

/**
 * 初始化认证状态
 * 从 localStorage 恢复登录状态
 */
const initAuth = async () => {
  if (initialized.value) return
  
  const token = authApi.getToken()
  const storedUser = authApi.getUser()
  
  if (token && storedUser) {
    user.value = storedUser
    
    // 尝试验证 token 是否有效
    try {
      const result = await authApi.getMe()
      if (result?.user) {
        user.value = result.user
      }
    } catch (error) {
      // Token 无效，清除状态
      console.warn('Token 验证失败，清除登录状态')
      user.value = null
      authApi.logout()
    }
  }
  
  initialized.value = true
}

/**
 * 用户认证 Composable
 */
export const useAuth = () => {
  const router = useRouter()
  
  // 计算属性
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const currentUser = computed(() => user.value)
  
  /**
   * 用户登录
   * @param {string} email - 邮箱
   * @param {string} password - 密码
   * @returns {Promise<Object>} 登录结果
   */
  const login = async (email, password) => {
    loading.value = true
    try {
      const result = await authApi.login(email, password)
      if (result?.user) {
        user.value = result.user
      }
      return result
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 用户注册
   * @param {string} username - 用户名
   * @param {string} email - 邮箱
   * @param {string} password - 密码
   * @param {string} invitationCode - 邀请码
   * @returns {Promise<Object>} 注册结果
   */
  const register = async (username, email, password, invitationCode) => {
    loading.value = true
    try {
      const result = await authApi.register(username, email, password, invitationCode)
      if (result?.user) {
        user.value = result.user
      }
      return result
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 用户登出
   * @param {boolean} redirect - 是否跳转到登录页
   */
  const logout = (redirect = true) => {
    authApi.logout()
    user.value = null
    
    if (redirect) {
      router.push('/login')
    }
  }
  
  /**
   * 检查认证状态
   * 验证当前 token 是否有效
   * @returns {Promise<boolean>}
   */
  const checkAuth = async () => {
    const token = authApi.getToken()
    if (!token) {
      user.value = null
      return false
    }
    
    try {
      const result = await authApi.getMe()
      if (result?.user) {
        user.value = result.user
        return true
      }
      return false
    } catch (error) {
      user.value = null
      authApi.logout()
      return false
    }
  }
  
  /**
   * 刷新 Token
   * @returns {Promise<string>} 新的 token
   */
  const refreshToken = async () => {
    try {
      const result = await authApi.refreshToken()
      return result?.token
    } catch (error) {
      // Token 刷新失败，清除登录状态
      logout(true)
      throw error
    }
  }
  
  return {
    // 状态
    user: readonly(user),
    currentUser,
    loading: readonly(loading),
    isAuthenticated,
    isAdmin,
    initialized: readonly(initialized),
    
    // 方法
    login,
    register,
    logout,
    checkAuth,
    refreshToken,
    initAuth
  }
}

// 导出初始化函数供 App.vue 使用
export { initAuth }

export default useAuth
