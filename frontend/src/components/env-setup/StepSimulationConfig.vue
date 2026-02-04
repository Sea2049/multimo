<template>
  <!-- Step 03: 生成双平台模拟配置 -->
  <div class="step-card" :class="{ 'active': isActive, 'completed': isCompleted }">
    <div class="card-header">
      <div class="step-info">
        <span class="step-num">03</span>
        <span class="step-title">生成双平台模拟配置</span>
      </div>
      <div class="step-status">
        <span v-if="isCompleted" class="badge success">已完成</span>
        <span v-else-if="isActive" class="badge processing">生成中</span>
        <span v-else class="badge pending">等待</span>
      </div>
    </div>

    <div class="card-content">
      <p class="api-note">POST /api/simulation/prepare</p>
      <p class="description">
        LLM 根据模拟需求与现实种子，智能设置世界时间流速、推荐算法、每个个体的活跃时间段、发言频率、事件触发等参数
      </p>
      
      <!-- Config Preview -->
      <div v-if="simulationConfig" class="config-detail-panel">
        <!-- 时间配置 -->
        <div class="config-block">
          <div class="config-grid">
            <div class="config-item">
              <span class="config-item-label">模拟时长</span>
              <span class="config-item-value">{{ simulationConfig.time_config?.total_simulation_hours || '-' }} 小时</span>
            </div>
            <div class="config-item">
              <span class="config-item-label">每轮时长</span>
              <span class="config-item-value">{{ simulationConfig.time_config?.minutes_per_round || '-' }} 分钟</span>
            </div>
            <div class="config-item">
              <span class="config-item-label">总轮次</span>
              <span class="config-item-value">{{ calculatedRounds }} 轮</span>
            </div>
            <div class="config-item">
              <span class="config-item-label">每小时活跃</span>
              <span class="config-item-value">{{ simulationConfig.time_config?.agents_per_hour_min }}-{{ simulationConfig.time_config?.agents_per_hour_max }}</span>
            </div>
          </div>
          <div class="time-periods">
            <div class="period-item">
              <span class="period-label">高峰时段</span>
              <span class="period-hours">{{ simulationConfig.time_config?.peak_hours?.join(':00, ') }}:00</span>
              <span class="period-multiplier">×{{ simulationConfig.time_config?.peak_activity_multiplier }}</span>
            </div>
            <div class="period-item">
              <span class="period-label">工作时段</span>
              <span class="period-hours">{{ simulationConfig.time_config?.work_hours?.[0] }}:00-{{ simulationConfig.time_config?.work_hours?.slice(-1)[0] }}:00</span>
              <span class="period-multiplier">×{{ simulationConfig.time_config?.work_activity_multiplier }}</span>
            </div>
            <div class="period-item">
              <span class="period-label">早间时段</span>
              <span class="period-hours">{{ simulationConfig.time_config?.morning_hours?.[0] }}:00-{{ simulationConfig.time_config?.morning_hours?.slice(-1)[0] }}:00</span>
              <span class="period-multiplier">×{{ simulationConfig.time_config?.morning_activity_multiplier }}</span>
            </div>
            <div class="period-item">
              <span class="period-label">低谷时段</span>
              <span class="period-hours">{{ simulationConfig.time_config?.off_peak_hours?.[0] }}:00-{{ simulationConfig.time_config?.off_peak_hours?.slice(-1)[0] }}:00</span>
              <span class="period-multiplier">×{{ simulationConfig.time_config?.off_peak_activity_multiplier }}</span>
            </div>
          </div>
        </div>

        <!-- Agent 配置 -->
        <div class="config-block">
          <div class="config-block-header">
            <span class="config-block-title">Agent 配置</span>
            <span class="config-block-badge">{{ simulationConfig.agent_configs?.length || 0 }} 个</span>
          </div>
          <div class="agents-cards">
            <div 
              v-for="agent in simulationConfig.agent_configs" 
              :key="agent.agent_id" 
              class="agent-card"
            >
              <!-- 卡片头部 -->
              <div class="agent-card-header">
                <div class="agent-identity">
                  <span class="agent-id">Agent {{ agent.agent_id }}</span>
                  <span class="agent-name">{{ agent.entity_name }}</span>
                </div>
                <div class="agent-tags">
                  <span class="agent-type">{{ agent.entity_type }}</span>
                  <span class="agent-stance" :class="'stance-' + agent.stance">{{ agent.stance }}</span>
                </div>
              </div>
              
              <!-- 活跃时间轴 -->
              <div class="agent-timeline">
                <span class="timeline-label">活跃时段</span>
                <div class="mini-timeline">
                  <div 
                    v-for="hour in 24" 
                    :key="hour - 1" 
                    class="timeline-hour"
                    :class="{ 'active': agent.active_hours?.includes(hour - 1) }"
                    :title="`${hour - 1}:00`"
                  ></div>
                </div>
                <div class="timeline-marks">
                  <span>0</span>
                  <span>6</span>
                  <span>12</span>
                  <span>18</span>
                  <span>24</span>
                </div>
              </div>

              <!-- 行为参数 -->
              <div class="agent-params">
                <div class="param-group">
                  <div class="param-item">
                    <span class="param-label">发帖/时</span>
                    <span class="param-value">{{ agent.posts_per_hour }}</span>
                  </div>
                  <div class="param-item">
                    <span class="param-label">评论/时</span>
                    <span class="param-value">{{ agent.comments_per_hour }}</span>
                  </div>
                  <div class="param-item">
                    <span class="param-label">响应延迟</span>
                    <span class="param-value">{{ agent.response_delay_min }}-{{ agent.response_delay_max }}min</span>
                  </div>
                </div>
                <div class="param-group">
                  <div class="param-item">
                    <span class="param-label">活跃度</span>
                    <span class="param-value with-bar">
                      <span class="mini-bar" :style="{ width: (agent.activity_level * 100) + '%' }"></span>
                      {{ (agent.activity_level * 100).toFixed(0) }}%
                    </span>
                  </div>
                  <div class="param-item">
                    <span class="param-label">情感倾向</span>
                    <span class="param-value" :class="agent.sentiment_bias > 0 ? 'positive' : agent.sentiment_bias < 0 ? 'negative' : 'neutral'">
                      {{ agent.sentiment_bias > 0 ? '+' : '' }}{{ agent.sentiment_bias?.toFixed(1) }}
                    </span>
                  </div>
                  <div class="param-item">
                    <span class="param-label">影响力</span>
                    <span class="param-value highlight">{{ agent.influence_weight?.toFixed(1) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 平台配置 -->
        <div class="config-block">
          <div class="config-block-header">
            <span class="config-block-title">推荐算法配置</span>
          </div>
          <div class="platforms-grid">
            <div v-if="simulationConfig.twitter_config" class="platform-card">
              <div class="platform-card-header">
                <span class="platform-name">平台 1：广场 / 信息流</span>
              </div>
              <div class="platform-params">
                <div class="param-row">
                  <span class="param-label">时效权重</span>
                  <span class="param-value">{{ simulationConfig.twitter_config.recency_weight }}</span>
                </div>
                <div class="param-row">
                  <span class="param-label">热度权重</span>
                  <span class="param-value">{{ simulationConfig.twitter_config.popularity_weight }}</span>
                </div>
                <div class="param-row">
                  <span class="param-label">相关性权重</span>
                  <span class="param-value">{{ simulationConfig.twitter_config.relevance_weight }}</span>
                </div>
                <div class="param-row">
                  <span class="param-label">病毒阈值</span>
                  <span class="param-value">{{ simulationConfig.twitter_config.viral_threshold }}</span>
                </div>
                <div class="param-row">
                  <span class="param-label">回音室强度</span>
                  <span class="param-value">{{ simulationConfig.twitter_config.echo_chamber_strength }}</span>
                </div>
              </div>
            </div>
            <div v-if="simulationConfig.reddit_config" class="platform-card">
              <div class="platform-card-header">
                <span class="platform-name">平台 2：话题 / 社区</span>
              </div>
              <div class="platform-params">
                <div class="param-row">
                  <span class="param-label">时效权重</span>
                  <span class="param-value">{{ simulationConfig.reddit_config.recency_weight }}</span>
                </div>
                <div class="param-row">
                  <span class="param-label">热度权重</span>
                  <span class="param-value">{{ simulationConfig.reddit_config.popularity_weight }}</span>
                </div>
                <div class="param-row">
                  <span class="param-label">相关性权重</span>
                  <span class="param-value">{{ simulationConfig.reddit_config.relevance_weight }}</span>
                </div>
                <div class="param-row">
                  <span class="param-label">病毒阈值</span>
                  <span class="param-value">{{ simulationConfig.reddit_config.viral_threshold }}</span>
                </div>
                <div class="param-row">
                  <span class="param-label">回音室强度</span>
                  <span class="param-value">{{ simulationConfig.reddit_config.echo_chamber_strength }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- LLM 配置推理 -->
        <div v-if="simulationConfig.generation_reasoning" class="config-block">
          <div class="config-block-header">
            <span class="config-block-title">LLM 配置推理</span>
          </div>
          <div class="reasoning-content">
            <div 
              v-for="(reason, idx) in simulationConfig.generation_reasoning.split('|').slice(0, 2)" 
              :key="idx" 
              class="reasoning-item"
            >
              <p class="reasoning-text">{{ reason.trim() }}</p>
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
  simulationConfig: {
    type: Object,
    default: null
  }
})

const isActive = computed(() => props.phase === 2)
const isCompleted = computed(() => props.phase > 2)

const calculatedRounds = computed(() => {
  if (!props.simulationConfig?.time_config) return '-'
  const totalHours = props.simulationConfig.time_config.total_simulation_hours
  const minutesPerRound = props.simulationConfig.time_config.minutes_per_round
  if (!totalHours || !minutesPerRound) return '-'
  return Math.floor((totalHours * 60) / minutesPerRound)
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

/* Config Detail Panel */
.config-detail-panel {
  margin-top: 16px;
}

.config-block {
  background: #F9FAFB;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.config-block:last-child {
  margin-bottom: 0;
}

.config-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.config-block-title {
  font-size: 12px;
  font-weight: 600;
  color: #1F2937;
}

.config-block-badge {
  font-size: 10px;
  background: #E5E7EB;
  color: #6B7280;
  padding: 2px 8px;
  border-radius: 10px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.config-item {
  text-align: center;
}

.config-item-label {
  display: block;
  font-size: 10px;
  color: #6B7280;
  margin-bottom: 4px;
}

.config-item-value {
  font-size: 14px;
  font-weight: 600;
  color: #1F2937;
}

/* Time Periods */
.time-periods {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.period-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #fff;
  border-radius: 6px;
}

.period-label {
  font-size: 11px;
  color: #6B7280;
  min-width: 60px;
}

.period-hours {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  color: #1F2937;
  flex: 1;
}

.period-multiplier {
  font-size: 11px;
  font-weight: 600;
  color: #059669;
}

/* Agent Cards */
.agents-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.agent-card {
  background: #fff;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 12px;
}

.agent-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.agent-identity {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.agent-id {
  font-size: 10px;
  font-family: 'JetBrains Mono', monospace;
  color: #6B7280;
}

.agent-name {
  font-size: 13px;
  font-weight: 600;
  color: #1F2937;
}

.agent-tags {
  display: flex;
  gap: 4px;
}

.agent-type {
  font-size: 10px;
  background: #E5E7EB;
  color: #6B7280;
  padding: 2px 6px;
  border-radius: 4px;
}

.agent-stance {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.agent-stance.stance-positive {
  background: #D1FAE5;
  color: #059669;
}

.agent-stance.stance-negative {
  background: #FEE2E2;
  color: #DC2626;
}

.agent-stance.stance-neutral {
  background: #E5E7EB;
  color: #6B7280;
}

/* Timeline */
.agent-timeline {
  margin-bottom: 12px;
}

.timeline-label {
  font-size: 10px;
  color: #6B7280;
  display: block;
  margin-bottom: 4px;
}

.mini-timeline {
  display: flex;
  gap: 1px;
  height: 16px;
  background: #E5E7EB;
  border-radius: 4px;
  overflow: hidden;
}

.timeline-hour {
  flex: 1;
  background: #E5E7EB;
  transition: background 0.2s;
}

.timeline-hour.active {
  background: #000;
}

.timeline-marks {
  display: flex;
  justify-content: space-between;
  margin-top: 2px;
}

.timeline-marks span {
  font-size: 8px;
  color: #9CA3AF;
}

/* Agent Params */
.agent-params {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-group {
  display: flex;
  gap: 12px;
}

.param-item {
  flex: 1;
}

.param-label {
  font-size: 10px;
  color: #6B7280;
  display: block;
}

.param-value {
  font-size: 12px;
  font-weight: 500;
  color: #1F2937;
}

.param-value.with-bar {
  display: flex;
  align-items: center;
  gap: 6px;
}

.mini-bar {
  height: 4px;
  background: #000;
  border-radius: 2px;
  max-width: 40px;
}

.param-value.positive {
  color: #059669;
}

.param-value.negative {
  color: #DC2626;
}

.param-value.neutral {
  color: #6B7280;
}

.param-value.highlight {
  color: #000;
  font-weight: 700;
}

/* Platform Cards */
.platforms-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.platform-card {
  background: #fff;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  overflow: hidden;
}

.platform-card-header {
  padding: 12px;
  background: #F9FAFB;
  border-bottom: 1px solid #E5E7EB;
}

.platform-name {
  font-size: 12px;
  font-weight: 600;
  color: #1F2937;
}

.platform-params {
  padding: 12px;
}

.param-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #F3F4F6;
}

.param-row:last-child {
  border-bottom: none;
}

.param-row .param-label {
  font-size: 11px;
  color: #6B7280;
}

.param-row .param-value {
  font-size: 11px;
  font-weight: 600;
  color: #1F2937;
}

/* Reasoning */
.reasoning-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reasoning-item {
  background: #fff;
  border-radius: 6px;
  padding: 12px;
}

.reasoning-text {
  font-size: 12px;
  color: #4B5563;
  line-height: 1.5;
  margin: 0;
}
</style>
