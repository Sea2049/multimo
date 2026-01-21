import { ref } from 'vue'

const errorAlertsRef = ref(null)

export const setErrorAlertsRef = (ref) => {
  errorAlertsRef.value = ref
}

export const useErrorHandler = () => {
  const handleApiError = (errorData) => {
    if (errorAlertsRef.value) {
      errorAlertsRef.value.addAlert({
        type: errorData.type || 'error',
        message: errorData.message || '发生错误',
        suggestion: errorData.suggestion || '',
        showRetry: errorData.showRetry || false,
        duration: 0
      })
    } else {
      console.error('ErrorAlert component not mounted:', errorData)
    }
  }

  const handleError = (error, fallbackMessage = '发生错误') => {
    if (error.isApiError && error.errorData) {
      handleApiError(error.errorData)
    } else {
      handleApiError({
        message: error.message || fallbackMessage,
        suggestion: '请刷新页面后重试。如果问题持续，请联系管理员。',
        type: 'error',
        showRetry: true
      })
    }
  }

  const showSuccess = (message) => {
    if (errorAlertsRef.value) {
      errorAlertsRef.value.addAlert({
        type: 'info',
        message: message,
        showRetry: false,
        duration: 3000
      })
    }
  }

  const showWarning = (message, suggestion = '') => {
    if (errorAlertsRef.value) {
      errorAlertsRef.value.addAlert({
        type: 'warning',
        message: message,
        suggestion: suggestion,
        showRetry: false,
        duration: 5000
      })
    }
  }

  return {
    handleApiError,
    handleError,
    showSuccess,
    showWarning
  }
}

export const withErrorHandling = (asyncFn, errorHandler) => {
  return async (...args) => {
    try {
      return await asyncFn(...args)
    } catch (error) {
      if (errorHandler) {
        errorHandler(error)
      } else {
        const { handleError } = useErrorHandler()
        handleError(error)
      }
      throw error
    }
  }
}
