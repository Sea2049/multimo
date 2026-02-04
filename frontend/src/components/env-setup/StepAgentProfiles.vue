<template>
  <!-- Step 02: 生成 Agent 人设 -->
  <div class="step-card" :class="{ 'active': isActive, 'completed': isCompleted }">
    <div class="card-header">
      <div class="step-info">
        <span class="step-num">02</span>
        <span class="step-title">生成 Agent 人设</span>
      </div>
      <div class="step-status">
        <span v-if="isCompleted" class="badge success">已完成</span>
        <span v-else-if="isActive" class="badge processing">{{ prepareProgress }}%</span>
        <span v-else class="badge pending">等待</span>
      </div>
    </div>

    <div class="card-content">
      <p class="api-note">POST /api/simulation/prepare</p>
      <p class="description">
        结合上下文，自动调用工具从知识图谱梳理实体与关系，初始化模拟个体，并基于现实种子赋予他们独特的行为与记忆
      </p>

      <!-- Profiles Stats -->
      <div v-if="profiles.length > 0" class="stats-grid">
        <div class="stat-card">
          <span class="stat-value">{{ profiles.length }}</span>
          <span class="stat-label">当前Agent数</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ expectedTotal || '-' }}</span>
          <span class="stat-label">预期Agent总数</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ totalTopicsCount }}</span>
          <span class="stat-label">现实种子当前关联话题数</span>
        </div>
      </div>

      <!-- Profiles List Preview -->
      <div v-if="profiles.length > 0" class="profiles-preview">
        <div class="preview-header">
          <span class="preview-title">已生成的 Agent 人设</span>
        </div>
        <div class="profiles-list">
          <div 
            v-for="(profile, idx) in profiles" 
            :key="idx" 
            class="profile-card"
            @click="$emit('select-profile', profile)"
          >
            <div class="profile-header">
              <span class="profile-realname">{{ profile.username || 'Unknown' }}</span>
              <span class="profile-username">@{{ profile.name || `agent_${idx}` }}</span>
            </div>
            <div class="profile-meta">
              <span class="profile-profession">{{ profile.profession || '未知职业' }}</span>
            </div>
            <p class="profile-bio">{{ profile.bio || '暂无简介' }}</p>
            <div v-if="profile.interested_topics?.length" class="profile-topics">
              <span 
                v-for="topic in profile.interested_topics.slice(0, 3)" 
                :key="topic" 
                class="topic-tag"
              >{{ topic }}</span>
              <span v-if="profile.interested_topics.length > 3" class="topic-more">
                +{{ profile.interested_topics.length - 3 }}
              </span>
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
  prepareProgress: {
    type: Number,
    default: 0
  },
  profiles: {
    type: Array,
    default: () => []
  },
  expectedTotal: {
    type: Number,
    default: null
  }
})

defineEmits(['select-profile'])

const isActive = computed(() => props.phase === 1)
const isCompleted = computed(() => props.phase > 1)

// 计算所有人设的关联话题总数
const totalTopicsCount = computed(() => {
  return props.profiles.reduce((sum, p) => {
    return sum + (p.interested_topics?.length || 0)
  }, 0)
})
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-card {
  background: #F9FAFB;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1F2937;
}

.stat-label {
  font-size: 11px;
  color: #6B7280;
}

/* Profiles Preview */
.profiles-preview {
  margin-top: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.preview-title {
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
}

.profiles-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.profile-card {
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.profile-card:hover {
  border-color: #000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.profile-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 6px;
}

.profile-realname {
  font-size: 13px;
  font-weight: 600;
  color: #1F2937;
}

.profile-username {
  font-size: 11px;
  color: #6B7280;
  font-family: 'JetBrains Mono', monospace;
}

.profile-meta {
  margin-bottom: 8px;
}

.profile-profession {
  font-size: 11px;
  color: #059669;
  background: #D1FAE5;
  padding: 2px 8px;
  border-radius: 10px;
}

.profile-bio {
  font-size: 12px;
  color: #4B5563;
  line-height: 1.4;
  margin: 0 0 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.profile-topics {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.topic-tag {
  font-size: 10px;
  color: #6B7280;
  background: #E5E7EB;
  padding: 2px 6px;
  border-radius: 4px;
}

.topic-more {
  font-size: 10px;
  color: #9CA3AF;
}
</style>
