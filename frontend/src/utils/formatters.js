/**
 * 日期时间格式化工具模块
 * 
 * 提供统一的日期时间格式化函数，避免各组件中重复实现。
 * 
 * @module utils/formatters
 */

/**
 * 格式化时间为 HH:MM 格式
 * 
 * @param {string|Date|number} timestamp - 时间戳或日期对象
 * @returns {string} 格式化后的时间字符串，如 "14:30"
 * 
 * @example
 * formatTime(new Date())  // "14:30"
 * formatTime('2024-01-15T14:30:00Z')  // "14:30"
 */
export const formatTime = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit'
    })
  } catch {
    return ''
  }
}

/**
 * 格式化时间为完整格式 HH:MM:SS
 * 
 * @param {string|Date|number} timestamp - 时间戳或日期对象
 * @returns {string} 格式化后的时间字符串，如 "14:30:45"
 */
export const formatTimeWithSeconds = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return ''
  }
}

/**
 * 格式化日期为本地日期字符串
 * 
 * @param {string|Date|number} dateStr - 日期字符串或日期对象
 * @returns {string} 格式化后的日期字符串，如 "2024/01/15 14:30"
 * 
 * @example
 * formatDate('2024-01-15T14:30:00Z')  // "2024/01/15 14:30"
 * formatDate(new Date())  // "2024/01/15 14:30"
 */
export const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return '-'
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '-'
  }
}

/**
 * 格式化日期为短日期格式（仅日期部分）
 * 
 * @param {string|Date|number} dateStr - 日期字符串或日期对象
 * @returns {string} 格式化后的日期字符串，如 "2024/01/15"
 */
export const formatDateShort = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return '-'
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch {
    return '-'
  }
}

/**
 * 格式化经过的时间（秒数转为可读格式）
 * 
 * @param {number} seconds - 秒数
 * @returns {string} 格式化后的时间字符串，如 "5m 30s" 或 "45s"
 * 
 * @example
 * formatElapsedTime(45)   // "45s"
 * formatElapsedTime(330)  // "5m 30s"
 * formatElapsedTime(3661) // "1h 1m 1s"
 */
export const formatElapsedTime = (seconds) => {
  if (seconds === null || seconds === undefined || isNaN(seconds)) return '0s'
  
  seconds = Math.round(seconds)
  
  if (seconds < 60) {
    return `${seconds}s`
  }
  
  if (seconds < 3600) {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return secs > 0 ? `${mins}m ${secs}s` : `${mins}m`
  }
  
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  let result = `${hours}h`
  if (mins > 0) result += ` ${mins}m`
  if (secs > 0) result += ` ${secs}s`
  
  return result
}

/**
 * 格式化持续时间（毫秒转为可读格式）
 * 
 * @param {number} ms - 毫秒数
 * @returns {string} 格式化后的时间字符串
 */
export const formatDuration = (ms) => {
  if (ms === null || ms === undefined || isNaN(ms)) return '0ms'
  
  if (ms < 1000) {
    return `${Math.round(ms)}ms`
  }
  
  return formatElapsedTime(ms / 1000)
}

/**
 * 格式化相对时间（距今多久）
 * 
 * @param {string|Date|number} timestamp - 时间戳
 * @returns {string} 相对时间描述，如 "5分钟前"、"2小时前"
 * 
 * @example
 * formatRelativeTime(Date.now() - 300000)  // "5分钟前"
 */
export const formatRelativeTime = (timestamp) => {
  if (!timestamp) return ''
  
  try {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffSecs = Math.floor(diffMs / 1000)
    
    if (diffSecs < 60) {
      return '刚刚'
    }
    
    const diffMins = Math.floor(diffSecs / 60)
    if (diffMins < 60) {
      return `${diffMins}分钟前`
    }
    
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) {
      return `${diffHours}小时前`
    }
    
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays < 30) {
      return `${diffDays}天前`
    }
    
    const diffMonths = Math.floor(diffDays / 30)
    if (diffMonths < 12) {
      return `${diffMonths}个月前`
    }
    
    const diffYears = Math.floor(diffMonths / 12)
    return `${diffYears}年前`
  } catch {
    return ''
  }
}

/**
 * 截断文本并添加省略号
 * 
 * @param {string} text - 原始文本
 * @param {number} maxLen - 最大长度
 * @returns {string} 截断后的文本
 * 
 * @example
 * truncateText('这是一段很长的文本', 5)  // "这是一段很..."
 */
export const truncateText = (text, maxLen = 100) => {
  if (!text) return ''
  if (text.length <= maxLen) return text
  return text.substring(0, maxLen) + '...'
}

/**
 * 格式化文件大小
 * 
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的大小，如 "1.5 MB"
 * 
 * @example
 * formatFileSize(1536)      // "1.5 KB"
 * formatFileSize(1572864)   // "1.5 MB"
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  if (!bytes || isNaN(bytes)) return '-'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i]
}

/**
 * 格式化数字（添加千位分隔符）
 * 
 * @param {number} num - 数字
 * @returns {string} 格式化后的数字，如 "1,234,567"
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined || isNaN(num)) return '-'
  return num.toLocaleString('en-US')
}

/**
 * 格式化百分比
 * 
 * @param {number} value - 小数值（0-1）
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化后的百分比，如 "85.5%"
 */
export const formatPercent = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) return '-'
  return (value * 100).toFixed(decimals) + '%'
}
