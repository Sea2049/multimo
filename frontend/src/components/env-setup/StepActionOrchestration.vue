<template>
  <!-- Step 04: 初始激活编排 -->
  <div class="step-card" :class="{ 'active': isActive, 'completed': isCompleted }">
    <div class="card-header">
      <div class="step-info">
        <span class="step-num">04</span>
        <span class="step-title">初始激活编排</span>
      </div>
      <div class="step-status">
        <span v-if="isCompleted" class="badge success">已完成</span>
        <span v-else-if="isActive" class="badge processing">编排中</span>
        <span v-else class="badge pending">等待</span>
      </div>
    </div>

    <div class="card-content">
      <p class="api-note">POST /api/simulation/prepare</p>
      <p class="description">
        基于叙事方向，自动生成初始激活事件与热点话题，引导模拟世界的初始状态
      </p>

      <div v-if="eventConfig" class="orchestration-content">
        <!-- 叙事方向 -->
        <div class="narrative-box">
          <span class="box-label narrative-label">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="special-icon">
              <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="url(#paint0_linear)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16.24 7.76L14.12 14.12L7.76 16.24L9.88 9.88L16.24 7.76Z" fill="url(#paint0_linear)" stroke="url(#paint0_linear)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <defs>
                <linearGradient id="paint0_linear" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                  <stop stop-color="#FF5722"/>
                  <stop offset="1" stop-color="#FF9800"/>
                </linearGradient>
              </defs>
            </svg>
            叙事引导方向
          </span>
          <p class="narrative-text">{{ eventConfig.narrative_direction }}</p>
        </div>

        <!-- 热点话题 -->
        <div class="topics-section">
          <span class="box-label">初始热点话题</span>
          <div class="hot-topics-grid">
            <span v-for="topic in eventConfig.hot_topics" :key="topic" class="hot-topic-tag">
              # {{ topic }}
            </span>
          </div>
        </div>

        <!-- 初始帖子流 -->
        <div class="initial-posts-section">
          <span class="box-label">初始激活序列 ({{ eventConfig.initial_posts?.length || 0 }})</span>
          <div class="posts-timeline">
            <div v-for="(post, idx) in eventConfig.initial_posts" :key="idx" class="timeline-item">
              <div class="timeline-marker"></div>
              <div class="timeline-content">
                <div class="post-header">
                  <span class="post-role">{{ post.poster_type }}</span>
                  <span class="post-agent-info">
                    <span class="post-id">Agent {{ post.poster_agent_id }}</span>
                    <span class="post-username">@{{ getAgentUsername(post.poster_agent_id) }}</span>
                  </span>
                </div>
                <p class="post-text">{{ post.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  phase: {
    type: Number,
    required: true
  },
  eventConfig: {
    type: Object,
    default: null
  },
  profiles: {
    type: Array,
    default: () => []
  }
})

const isActive = computed(() => props.phase === 3)
const isCompleted = computed(() => props.phase > 3)

// 根据agent_id获取对应的username
const getAgentUsername = (agentId) => {
  if (props.profiles && props.profiles.length > agentId && agentId >= 0) {
    const profile = props.profiles[agentId]
    return profile?.username || `agent_${agentId}`
  }
  return `agent_${agentId}`
}
</script>

<style scoped>
.step-card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.step-card.active {
  border-color: #000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.step-card.completed {
  border-color: #10B981;
  background: #F0FDF4;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #F9FAFB;
  border-bottom: 1px solid #E5E7EB;
}

.step-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  color: #6B7280;
  background: #E5E7EB;
  padding: 4px 8px;
  border-radius: 4px;
}

.step-card.active .step-num,
.step-card.completed .step-num {
  background: #000;
  color: #fff;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: #1F2937;
}

.badge {
  font-size: 11px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
}

.badge.success {
  background: #D1FAE5;
  color: #059669;
}

.badge.processing {
  background: #000;
  color: #fff;
}

.badge.pending {
  background: #F3F4F6;
  color: #9CA3AF;
}

.card-content {
  padding: 20px;
}

.api-note {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #6B7280;
  margin: 0 0 8px 0;
}

.description {
  font-size: 13px;
  color: #4B5563;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

/* Orchestration Content */
.orchestration-content {
  margin-top: 16px;
}

/* Narrative Box */
.narrative-box {
  background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
  border: 1px solid #FDBA74;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.box-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
  margin-bottom: 8px;
}

.narrative-label {
  color: #EA580C;
}

.special-icon {
  flex-shrink: 0;
}

.narrative-text {
  font-size: 14px;
  color: #1F2937;
  line-height: 1.6;
  margin: 0;
}

/* Topics Section */
.topics-section {
  margin-bottom: 16px;
}

.hot-topics-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hot-topic-tag {
  font-size: 12px;
  font-weight: 500;
  color: #1F2937;
  background: #F3F4F6;
  padding: 6px 12px;
  border-radius: 20px;
  transition: all 0.2s;
}

.hot-topic-tag:hover {
  background: #E5E7EB;
}

/* Initial Posts Section */
.initial-posts-section {
  margin-top: 16px;
}

.posts-timeline {
  margin-top: 12px;
  border-left: 2px solid #E5E7EB;
  padding-left: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.timeline-item {
  position: relative;
  padding-bottom: 16px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: -26px;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #000;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #E5E7EB;
}

.timeline-content {
  background: #F9FAFB;
  border-radius: 8px;
  padding: 12px;
}

.post-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.post-role {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  color: #fff;
  background: #000;
  padding: 2px 8px;
  border-radius: 4px;
}

.post-agent-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.post-id {
  font-size: 10px;
  font-family: 'JetBrains Mono', monospace;
  color: #6B7280;
}

.post-username {
  font-size: 11px;
  color: #1F2937;
  font-weight: 500;
}

.post-text {
  font-size: 13px;
  color: #4B5563;
  line-height: 1.5;
  margin: 0;
}
</style>
