/**
 * Markdown 渲染工具模块
 * 
 * 提供轻量级的 Markdown 到 HTML 转换，用于在 Vue 组件中渲染 Markdown 内容。
 * 注意：输出用于 v-html，需确保内容来源可信。
 * 
 * @module utils/markdown
 */

/**
 * 渲染 Markdown 内容为 HTML
 * 
 * 支持的语法：
 * - 标题 (#, ##, ###, ####)
 * - 代码块 (```)
 * - 行内代码 (`)
 * - 粗体 (**text**)
 * - 斜体 (*text* 或 _text_)
 * - 引用块 (>)
 * - 无序列表 (-)
 * - 有序列表 (1. 2. 3.)
 * - 分隔线 (---)
 * 
 * @param {string} content - Markdown 内容
 * @param {Object} options - 渲染选项
 * @param {boolean} options.removeFirstHeading - 是否移除第一个二级标题（默认 true）
 * @param {boolean} options.supportNestedList - 是否支持嵌套列表（默认 false）
 * @returns {string} HTML 字符串
 * 
 * @example
 * const html = renderMarkdown('## Hello\n\nThis is **bold** text.')
 * // <h3 class="md-h3">Hello</h3><p class="md-p">This is <strong>bold</strong> text.</p>
 */
export const renderMarkdown = (content, options = {}) => {
  if (!content) return ''
  
  const {
    removeFirstHeading = true,
    supportNestedList = false
  } = options
  
  let processedContent = content
  
  // 去掉开头的二级标题（## xxx），因为章节标题已在外层显示
  if (removeFirstHeading) {
    processedContent = processedContent.replace(/^##\s+.+\n+/, '')
  }
  
  // 处理代码块（必须最先处理，避免内部内容被其他规则匹配）
  let html = processedContent.replace(
    /```(\w*)\n([\s\S]*?)```/g, 
    '<pre class="code-block"><code>$2</code></pre>'
  )
  
  // 处理行内代码
  html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
  
  // 处理标题（从小到大处理，避免 # 被 ## 匹配）
  html = html.replace(/^#### (.+)$/gm, '<h5 class="md-h5">$1</h5>')
  html = html.replace(/^### (.+)$/gm, '<h4 class="md-h4">$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3 class="md-h3">$1</h3>')
  html = html.replace(/^# (.+)$/gm, '<h2 class="md-h2">$1</h2>')
  
  // 处理引用块
  html = html.replace(/^> (.+)$/gm, '<blockquote class="md-quote">$1</blockquote>')
  
  // 处理列表
  if (supportNestedList) {
    // 支持嵌套列表 - 根据缩进确定层级
    html = html.replace(/^(\s*)- (.+)$/gm, (match, indent, text) => {
      const level = Math.floor(indent.length / 2)
      return `<li class="md-li" data-level="${level}">${text}</li>`
    })
    html = html.replace(/^(\s*)(\d+)\. (.+)$/gm, (match, indent, num, text) => {
      const level = Math.floor(indent.length / 2)
      return `<li class="md-oli" data-level="${level}">${text}</li>`
    })
  } else {
    // 简单列表
    html = html.replace(/^- (.+)$/gm, '<li class="md-li">$1</li>')
    html = html.replace(/^\d+\. (.+)$/gm, '<li class="md-oli">$1</li>')
  }
  
  // 包装无序列表
  html = html.replace(/(<li class="md-li"[^>]*>[\s\S]*?<\/li>\s*)+/g, '<ul class="md-ul">$&</ul>')
  // 包装有序列表
  html = html.replace(/(<li class="md-oli"[^>]*>[\s\S]*?<\/li>\s*)+/g, '<ol class="md-ol">$&</ol>')
  
  // 清理列表格式
  html = html.replace(/<\/li>\s+<li/g, '</li><li')
  html = html.replace(/<ul class="md-ul">\s+/g, '<ul class="md-ul">')
  html = html.replace(/<ol class="md-ol">\s+/g, '<ol class="md-ol">')
  html = html.replace(/\s+<\/ul>/g, '</ul>')
  html = html.replace(/\s+<\/ol>/g, '</ol>')
  
  // 处理粗体和斜体
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/_(.+?)_/g, '<em>$1</em>')
  
  // 处理分隔线
  html = html.replace(/^---$/gm, '<hr class="md-hr">')
  
  // 处理换行 - 空行变成段落分隔，单换行变成 <br>
  html = html.replace(/\n\n/g, '</p><p class="md-p">')
  html = html.replace(/\n/g, '<br>')
  
  // 包装在段落中
  html = '<p class="md-p">' + html + '</p>'
  
  // 清理空段落和错误嵌套
  html = html.replace(/<p class="md-p"><\/p>/g, '')
  html = html.replace(/<p class="md-p">(<h[2-5])/g, '$1')
  html = html.replace(/(<\/h[2-5]>)<\/p>/g, '$1')
  html = html.replace(/<p class="md-p">(<ul|<ol|<blockquote|<pre|<hr)/g, '$1')
  html = html.replace(/(<\/ul>|<\/ol>|<\/blockquote>|<\/pre>)<\/p>/g, '$1')
  
  return html
}

/**
 * 简单的 Markdown 渲染（仅处理基本格式）
 * 
 * 适用于短文本，如消息、评论等。
 * 
 * @param {string} content - Markdown 内容
 * @returns {string} HTML 字符串
 */
export const renderSimpleMarkdown = (content) => {
  if (!content) return ''
  
  let html = content
  
  // 处理行内代码
  html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
  
  // 处理粗体和斜体
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  
  // 处理换行
  html = html.replace(/\n/g, '<br>')
  
  return html
}

/**
 * 从 Markdown 内容中提取纯文本
 * 
 * 移除所有 Markdown 语法，只保留文本内容。
 * 
 * @param {string} content - Markdown 内容
 * @returns {string} 纯文本
 * 
 * @example
 * extractText('**Hello** _world_')  // "Hello world"
 */
export const extractText = (content) => {
  if (!content) return ''
  
  let text = content
  
  // 移除代码块
  text = text.replace(/```[\s\S]*?```/g, '')
  // 移除行内代码
  text = text.replace(/`[^`]+`/g, '')
  // 移除标题标记
  text = text.replace(/^#{1,6}\s+/gm, '')
  // 移除粗体/斜体标记
  text = text.replace(/\*\*(.+?)\*\*/g, '$1')
  text = text.replace(/\*(.+?)\*/g, '$1')
  text = text.replace(/_(.+?)_/g, '$1')
  // 移除列表标记
  text = text.replace(/^[-*+]\s+/gm, '')
  text = text.replace(/^\d+\.\s+/gm, '')
  // 移除引用标记
  text = text.replace(/^>\s+/gm, '')
  // 移除分隔线
  text = text.replace(/^---$/gm, '')
  // 压缩多余空白
  text = text.replace(/\n{3,}/g, '\n\n')
  text = text.trim()
  
  return text
}

/**
 * 判断内容是否可能是 Markdown
 * 
 * @param {string} content - 内容
 * @returns {boolean} 是否可能是 Markdown
 */
export const isMarkdown = (content) => {
  if (!content || typeof content !== 'string') return false
  
  // 常见 Markdown 特征
  const patterns = [
    /^#{1,6}\s+/m,        // 标题
    /\*\*.+?\*\*/,        // 粗体
    /```[\s\S]*?```/,     // 代码块
    /^[-*+]\s+/m,         // 无序列表
    /^\d+\.\s+/m,         // 有序列表
    /^>\s+/m,             // 引用
    /\[.+?\]\(.+?\)/      // 链接
  ]
  
  return patterns.some(pattern => pattern.test(content))
}

/**
 * Markdown 渲染所需的 CSS 类名定义
 * 
 * 可以在全局样式或组件样式中使用这些类名来定制样式。
 * 
 * @constant
 * @type {string[]}
 */
export const MARKDOWN_CSS_CLASSES = [
  'md-h2',      // h2 标题
  'md-h3',      // h3 标题
  'md-h4',      // h4 标题
  'md-h5',      // h5 标题
  'md-p',       // 段落
  'md-ul',      // 无序列表
  'md-ol',      // 有序列表
  'md-li',      // 无序列表项
  'md-oli',     // 有序列表项
  'md-quote',   // 引用块
  'md-hr',      // 分隔线
  'code-block', // 代码块
  'inline-code' // 行内代码
]
