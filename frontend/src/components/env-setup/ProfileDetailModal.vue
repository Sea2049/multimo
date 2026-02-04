<template>
  <!-- Profile Detail Modal -->
  <Transition name="modal">
    <div v-if="profile" class="profile-modal-overlay" @click.self="$emit('close')">
      <div class="profile-modal">
        <div class="modal-header">
          <div class="modal-header-info">
            <div class="modal-name-row">
              <span class="modal-realname">{{ profile.username }}</span>
              <span class="modal-username">@{{ profile.name }}</span>
            </div>
            <span class="modal-profession">{{ profile.profession }}</span>
          </div>
          <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <div class="modal-body">
          <!-- 基本信息 -->
          <div class="modal-info-grid">
            <div class="info-item">
              <span class="info-label">事件外显年龄</span>
              <span class="info-value">{{ profile.age || '-' }} 岁</span>
            </div>
            <div class="info-item">
              <span class="info-label">事件外显性别</span>
              <span class="info-value">{{ genderMap[profile.gender] || profile.gender }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">国家/地区</span>
              <span class="info-value">{{ profile.country || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">事件外显MBTI</span>
              <span class="info-value mbti">{{ profile.mbti || '-' }}</span>
            </div>
          </div>

          <!-- 简介 -->
          <div class="modal-section">
            <span class="section-label">人设简介</span>
            <p class="section-bio">{{ profile.bio || '暂无简介' }}</p>
          </div>

          <!-- 关注话题 -->
          <div class="modal-section" v-if="profile.interested_topics?.length">
            <span class="section-label">现实种子关联话题</span>
            <div class="topics-grid">
              <span 
                v-for="topic in profile.interested_topics" 
                :key="topic" 
                class="topic-item"
              >{{ topic }}</span>
            </div>
          </div>

          <!-- 详细人设 -->
          <div class="modal-section" v-if="profile.persona">
            <span class="section-label">详细人设背景</span>
            
            <!-- 人设维度概览 -->
            <div class="persona-dimensions">
              <div class="dimension-card">
                <span class="dim-title">事件全景经历</span>
                <span class="dim-desc">在此事件中的完整行为轨迹</span>
              </div>
              <div class="dimension-card">
                <span class="dim-title">行为模式侧写</span>
                <span class="dim-desc">经验总结与行事风格偏好</span>
              </div>
              <div class="dimension-card">
                <span class="dim-title">独特记忆印记</span>
                <span class="dim-desc">基于现实种子形成的记忆</span>
              </div>
              <div class="dimension-card">
                <span class="dim-title">社会关系网络</span>
                <span class="dim-desc">个体链接与交互图谱</span>
              </div>
            </div>

            <div class="persona-content">
              <p class="section-persona">{{ profile.persona }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  profile: {
    type: Object,
    default: null
  }
})

defineEmits(['close'])

const genderMap = {
  male: '男',
  female: '女',
  other: '其他'
}
</script>

<style scoped>
/* Modal Overlay */
.profile-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

/* Modal Container */
.profile-modal {
  background: #fff;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 24px;
  background: #F9FAFB;
  border-bottom: 1px solid #E5E7EB;
}

.modal-header-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.modal-name-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.modal-realname {
  font-size: 20px;
  font-weight: 700;
  color: #1F2937;
}

.modal-username {
  font-size: 14px;
  color: #6B7280;
  font-family: 'JetBrains Mono', monospace;
}

.modal-profession {
  font-size: 13px;
  color: #059669;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #E5E7EB;
  border-radius: 8px;
  font-size: 20px;
  color: #6B7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #D1D5DB;
  color: #1F2937;
}

/* Modal Body */
.modal-body {
  padding: 24px;
  overflow-y: auto;
}

/* Info Grid */
.modal-info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.info-item {
  text-align: center;
  padding: 12px;
  background: #F9FAFB;
  border-radius: 8px;
}

.info-label {
  display: block;
  font-size: 11px;
  color: #6B7280;
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #1F2937;
}

.info-value.mbti {
  color: #7C3AED;
}

/* Modal Sections */
.modal-section {
  margin-bottom: 24px;
}

.modal-section:last-child {
  margin-bottom: 0;
}

.section-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
  margin-bottom: 8px;
}

.section-bio {
  font-size: 14px;
  color: #4B5563;
  line-height: 1.6;
  margin: 0;
}

/* Topics Grid */
.topics-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.topic-item {
  font-size: 12px;
  color: #1F2937;
  background: #F3F4F6;
  padding: 6px 12px;
  border-radius: 16px;
}

/* Persona Dimensions */
.persona-dimensions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.dimension-card {
  background: #F9FAFB;
  border-radius: 8px;
  padding: 12px;
}

.dim-title {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 4px;
}

.dim-desc {
  font-size: 11px;
  color: #6B7280;
}

/* Persona Content */
.persona-content {
  background: #F9FAFB;
  border-radius: 8px;
  padding: 16px;
}

.section-persona {
  font-size: 13px;
  color: #4B5563;
  line-height: 1.7;
  margin: 0;
  white-space: pre-wrap;
}

/* Modal Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .profile-modal,
.modal-leave-active .profile-modal {
  transition: transform 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .profile-modal,
.modal-leave-to .profile-modal {
  transform: scale(0.95) translateY(20px);
}
</style>
