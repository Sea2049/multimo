import axios from 'axios'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 600000,
  headers: {
    'Content-Type': 'application/json'
  }
})

service.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

const ERROR_MESSAGES = {
  TIMEOUT: {
    message: '请求超时',
    suggestion: '服务器响应时间过长，请刷新页面或稍后重试。如果问题持续，请联系管理员。',
    type: 'warning',
    showRetry: true
  },
  NETWORK: {
    message: '网络连接失败',
    suggestion: '请检查您的网络连接，确保网络稳定后重试。',
    type: 'error',
    showRetry: true
  },
  SERVER_ERROR: {
    message: '服务器错误',
    suggestion: '服务器内部发生错误，请稍后重试或联系管理员。',
    type: 'error',
    showRetry: true
  },
  BAD_REQUEST: {
    message: '请求参数错误',
    suggestion: '请检查输入参数是否正确，刷新页面后重试。',
    type: 'warning',
    showRetry: false
  },
  NOT_FOUND: {
    message: '资源不存在',
    suggestion: '请求的资源可能已被删除，请刷新页面后重试。',
    type: 'warning',
    showRetry: true
  },
  UNAUTHORIZED: {
    message: '未授权访问',
    suggestion: '请登录后重试，或检查您的登录状态是否过期。',
    type: 'warning',
    showRetry: false
  },
  FORBIDDEN: {
    message: '权限不足',
    suggestion: '您没有权限执行此操作，请联系管理员获取权限。',
    type: 'error',
    showRetry: false
  },
  RATE_LIMIT: {
    message: '请求过于频繁',
    suggestion: '请稍后再试，短时间内不要频繁发起请求。',
    type: 'warning',
    showRetry: true
  },
  UNKNOWN: {
    message: '发生未知错误',
    suggestion: '请刷新页面后重试。如果问题持续，请联系管理员。',
    type: 'error',
    showRetry: true
  }
}

const classifyError = (error) => {
  if (!error.response) {
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return { ...ERROR_MESSAGES.TIMEOUT, errorCode: 'TIMEOUT_ERROR' }
    }
    if (error.message === 'Network Error' || !navigator.onLine) {
      return { ...ERROR_MESSAGES.NETWORK, errorCode: 'NETWORK_ERROR' }
    }
    return { ...ERROR_MESSAGES.UNKNOWN, errorCode: 'UNKNOWN_ERROR' }
  }

  const status = error.response.status

  switch (status) {
    case 400:
      return { ...ERROR_MESSAGES.BAD_REQUEST, errorCode: 'INVALID_INPUT' }
    case 401:
      return { ...ERROR_MESSAGES.UNAUTHORIZED, errorCode: 'UNAUTHORIZED' }
    case 403:
      return { ...ERROR_MESSAGES.FORBIDDEN, errorCode: 'FORBIDDEN' }
    case 404:
      return { ...ERROR_MESSAGES.NOT_FOUND, errorCode: 'RESOURCE_NOT_FOUND' }
    case 429:
      return { ...ERROR_MESSAGES.RATE_LIMIT, errorCode: 'RATE_LIMIT_EXCEEDED' }
    case 500:
    case 502:
    case 503:
      return { ...ERROR_MESSAGES.SERVER_ERROR, errorCode: 'INTERNAL_ERROR' }
    default:
      return { ...ERROR_MESSAGES.UNKNOWN, errorCode: 'UNKNOWN_ERROR' }
  }
}

const formatErrorMessage = (error) => {
  const response = error.response?.data

  if (response?.recovery_suggestion) {
    return {
      message: response.message || '发生错误',
      suggestion: response.recovery_suggestion,
      errorCode: response.error_code || 'UNKNOWN_ERROR',
      type: 'error',
      showRetry: true
    }
  }

  const classified = classifyError(error)

  if (response?.message && !classified.message.includes('未知')) {
    classified.message = response.message
  }

  return classified
}

service.interceptors.response.use(
  response => {
    const res = response.data

    if (!res.success && res.success !== undefined) {
      const formattedError = formatErrorMessage({
        response: {
          status: res.status_code || 400,
          data: res
        }
      })

      const error = new Error(formattedError.message)
      error.isApiError = true
      error.errorData = {
        ...formattedError,
        originalError: res
      }

      return Promise.reject(error)
    }

    return res
  },
  error => {
    console.error('Response error:', error)

    const formattedError = formatErrorMessage(error)

    const apiError = new Error(formattedError.message)
    apiError.isApiError = true
    apiError.errorData = formattedError

    return Promise.reject(apiError)
  }
)

export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error

      const shouldRetry = error.errorData?.showRetry &&
                         (error.errorData?.type === 'warning' ||
                          error.errorData?.type === 'info')

      if (!shouldRetry) {
        throw error
      }

      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export const createErrorHandler = (onError) => {
  return (error) => {
    if (error.isApiError && error.errorData) {
      onError(error.errorData)
    } else {
      onError({
        message: error.message || '发生未知错误',
        suggestion: '请刷新页面后重试。如果问题持续，请联系管理员。',
        errorCode: 'UNKNOWN_ERROR',
        type: 'error',
        showRetry: true
      })
    }
  }
}

export { classifyError, formatErrorMessage, ERROR_MESSAGES }

export default service
