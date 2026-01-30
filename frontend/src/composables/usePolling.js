/**
 * 轮询 Composable 模块
 * 
 * 提供统一的轮询逻辑，替代各组件中分散的 setInterval/clearInterval。
 * 自动处理组件卸载时的清理，避免内存泄漏。
 * 
 * @module composables/usePolling
 */

import { ref, onMounted, onBeforeUnmount, onUnmounted } from 'vue'

/**
 * 轮询 Composable
 * 
 * @param {Function} fetchFn - 轮询时执行的异步函数
 * @param {number} interval - 轮询间隔（毫秒）
 * @param {Object} options - 配置选项
 * @param {boolean} options.immediate - 是否立即执行一次（默认 false）
 * @param {boolean} options.autoStart - 是否在 onMounted 时自动开始（默认 false）
 * @param {Function} options.onError - 错误处理回调
 * @param {Function} options.shouldContinue - 判断是否继续轮询的函数，返回 false 停止
 * @param {number} options.maxRetries - 连续失败后停止的最大重试次数（默认 0 表示不限制）
 * @returns {Object} 轮询控制对象
 * 
 * @example
 * // 基本用法
 * const { start, stop, isPolling } = usePolling(
 *   async () => {
 *     const data = await fetchStatus()
 *     status.value = data
 *   },
 *   2000
 * )
 * 
 * // 带条件停止
 * const { start, stop } = usePolling(
 *   fetchData,
 *   3000,
 *   {
 *     immediate: true,
 *     shouldContinue: () => status.value !== 'completed'
 *   }
 * )
 */
export function usePolling(fetchFn, interval, options = {}) {
  const {
    immediate = false,
    autoStart = false,
    onError = null,
    shouldContinue = null,
    maxRetries = 0
  } = options

  // 轮询状态
  const isPolling = ref(false)
  const isPaused = ref(false)
  const errorCount = ref(0)
  const lastError = ref(null)
  
  // 定时器 ID
  let timerId = null

  /**
   * 执行一次轮询
   */
  const execute = async () => {
    if (isPaused.value) return
    
    try {
      await fetchFn()
      errorCount.value = 0  // 成功后重置错误计数
      lastError.value = null
      
      // 检查是否应该继续
      if (shouldContinue && !shouldContinue()) {
        stop()
        return
      }
    } catch (error) {
      errorCount.value++
      lastError.value = error
      
      if (onError) {
        onError(error, errorCount.value)
      }
      
      // 达到最大重试次数后停止
      if (maxRetries > 0 && errorCount.value >= maxRetries) {
        console.warn(`[usePolling] 达到最大重试次数 (${maxRetries})，停止轮询`)
        stop()
        return
      }
    }
  }

  /**
   * 开始轮询
   * 
   * @param {boolean} executeImmediately - 是否立即执行一次
   */
  const start = (executeImmediately = immediate) => {
    if (isPolling.value) return  // 已在轮询中
    
    isPolling.value = true
    isPaused.value = false
    errorCount.value = 0
    
    // 立即执行一次
    if (executeImmediately) {
      execute()
    }
    
    // 设置定时器
    timerId = setInterval(execute, interval)
  }

  /**
   * 停止轮询
   */
  const stop = () => {
    if (timerId !== null) {
      clearInterval(timerId)
      timerId = null
    }
    isPolling.value = false
    isPaused.value = false
  }

  /**
   * 暂停轮询（定时器继续运行但不执行函数）
   */
  const pause = () => {
    isPaused.value = true
  }

  /**
   * 恢复轮询
   */
  const resume = () => {
    isPaused.value = false
  }

  /**
   * 重启轮询（停止后重新开始）
   * 
   * @param {boolean} executeImmediately - 是否立即执行一次
   */
  const restart = (executeImmediately = immediate) => {
    stop()
    start(executeImmediately)
  }

  /**
   * 修改轮询间隔
   * 
   * @param {number} newInterval - 新的轮询间隔（毫秒）
   */
  const setInterval = (newInterval) => {
    if (isPolling.value) {
      stop()
      interval = newInterval
      start()
    } else {
      interval = newInterval
    }
  }

  // 自动开始
  if (autoStart) {
    onMounted(() => {
      start()
    })
  }

  // 组件卸载时自动清理（双重保险）
  onBeforeUnmount(() => {
    stop()
  })
  
  onUnmounted(() => {
    stop()
  })

  return {
    // 状态
    isPolling,
    isPaused,
    errorCount,
    lastError,
    
    // 方法
    start,
    stop,
    pause,
    resume,
    restart,
    setInterval,
    execute  // 暴露单次执行方法，用于手动触发
  }
}

/**
 * 多轮询管理 Composable
 * 
 * 用于同时管理多个轮询任务。
 * 
 * @returns {Object} 轮询管理器
 * 
 * @example
 * const { add, remove, startAll, stopAll } = usePollingManager()
 * 
 * add('status', async () => { ... }, 2000)
 * add('logs', async () => { ... }, 1000)
 * 
 * startAll()
 * // ...
 * stopAll()
 */
export function usePollingManager() {
  const pollers = new Map()

  /**
   * 添加轮询任务
   * 
   * @param {string} name - 任务名称
   * @param {Function} fetchFn - 轮询函数
   * @param {number} interval - 轮询间隔
   * @param {Object} options - 配置选项
   * @returns {Object} 轮询控制对象
   */
  const add = (name, fetchFn, interval, options = {}) => {
    if (pollers.has(name)) {
      console.warn(`[usePollingManager] 任务 "${name}" 已存在，将被覆盖`)
      remove(name)
    }
    
    const poller = usePolling(fetchFn, interval, options)
    pollers.set(name, poller)
    return poller
  }

  /**
   * 移除轮询任务
   * 
   * @param {string} name - 任务名称
   */
  const remove = (name) => {
    const poller = pollers.get(name)
    if (poller) {
      poller.stop()
      pollers.delete(name)
    }
  }

  /**
   * 获取轮询任务
   * 
   * @param {string} name - 任务名称
   * @returns {Object|undefined} 轮询控制对象
   */
  const get = (name) => {
    return pollers.get(name)
  }

  /**
   * 启动所有轮询
   */
  const startAll = () => {
    pollers.forEach(poller => poller.start())
  }

  /**
   * 停止所有轮询
   */
  const stopAll = () => {
    pollers.forEach(poller => poller.stop())
  }

  /**
   * 暂停所有轮询
   */
  const pauseAll = () => {
    pollers.forEach(poller => poller.pause())
  }

  /**
   * 恢复所有轮询
   */
  const resumeAll = () => {
    pollers.forEach(poller => poller.resume())
  }

  // 组件卸载时自动清理所有轮询
  onBeforeUnmount(() => {
    stopAll()
  })

  onUnmounted(() => {
    stopAll()
  })

  return {
    add,
    remove,
    get,
    startAll,
    stopAll,
    pauseAll,
    resumeAll,
    
    // 暴露 Map 以便查看当前所有任务
    pollers
  }
}

/**
 * 带退避策略的轮询 Composable
 * 
 * 在连续失败时自动增加轮询间隔，成功后恢复。
 * 
 * @param {Function} fetchFn - 轮询函数
 * @param {number} baseInterval - 基础轮询间隔（毫秒）
 * @param {Object} options - 配置选项
 * @param {number} options.maxInterval - 最大轮询间隔（默认 30000ms）
 * @param {number} options.backoffFactor - 退避因子（默认 2）
 * @returns {Object} 轮询控制对象
 * 
 * @example
 * const { start, stop } = useBackoffPolling(
 *   fetchStatus,
 *   2000,
 *   { maxInterval: 30000, backoffFactor: 2 }
 * )
 */
export function useBackoffPolling(fetchFn, baseInterval, options = {}) {
  const {
    maxInterval = 30000,
    backoffFactor = 2,
    ...restOptions
  } = options

  let currentInterval = baseInterval
  const isPolling = ref(false)
  let timerId = null

  const execute = async () => {
    try {
      await fetchFn()
      // 成功后恢复基础间隔
      currentInterval = baseInterval
    } catch (error) {
      // 失败后增加间隔
      currentInterval = Math.min(currentInterval * backoffFactor, maxInterval)
      console.warn(`[useBackoffPolling] 执行失败，下次间隔: ${currentInterval}ms`)
      
      if (restOptions.onError) {
        restOptions.onError(error)
      }
    }
    
    // 设置下一次执行
    if (isPolling.value) {
      timerId = setTimeout(execute, currentInterval)
    }
  }

  const start = (immediate = false) => {
    if (isPolling.value) return
    
    isPolling.value = true
    currentInterval = baseInterval
    
    if (immediate) {
      execute()
    } else {
      timerId = setTimeout(execute, currentInterval)
    }
  }

  const stop = () => {
    isPolling.value = false
    if (timerId !== null) {
      clearTimeout(timerId)
      timerId = null
    }
  }

  onBeforeUnmount(() => {
    stop()
  })

  onUnmounted(() => {
    stop()
  })

  return {
    isPolling,
    start,
    stop,
    getCurrentInterval: () => currentInterval
  }
}
