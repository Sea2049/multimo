<template>
  <div class="admin-container">
    <!-- 顶部导航 -->
    <nav class="navbar">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">MULTIMO</router-link>
        <span class="nav-separator">/</span>
        <span class="nav-current">管理后台</span>
      </div>
      <div class="nav-user">
        <span class="user-name">{{ currentUser?.username }}</span>
        <button class="logout-btn" @click="handleLogout">登出</button>
      </div>
    </nav>

    <div class="admin-content">
      <div class="admin-header">
        <h1 class="admin-title">邀请码管理</h1>
        <button class="create-btn" @click="showCreateModal = true">
          + 创建邀请码
        </button>
      </div>

      <!-- 邀请码列表 -->
      <div class="table-container">
        <div v-if="loading" class="loading-state">加载中...</div>
        <div v-else-if="invitations.length === 0" class="empty-state">
          暂无邀请码，点击上方按钮创建
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>邀请码</th>
              <th>使用情况</th>
              <th>状态</th>
              <th>过期时间</th>
              <th>备注</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inv in invitations" :key="inv.id">
              <td class="code-cell">{{ inv.code }}</td>
              <td>{{ inv.used_count }} / {{ inv.max_uses }}</td>
              <td>
                <span :class="['status-badge', inv.is_active ? 'active' : 'inactive']">
                  {{ inv.is_active ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ formatDate(inv.expires_at) }}</td>
              <td class="note-cell">{{ inv.note || '-' }}</td>
              <td>{{ formatDate(inv.created_at) }}</td>
              <td class="action-cell">
                <button 
                  class="action-btn toggle-btn"
                  @click="toggleStatus(inv)"
                  :title="inv.is_active ? '禁用' : '启用'"
                >
                  {{ inv.is_active ? '禁用' : '启用' }}
                </button>
                <button 
                  class="action-btn delete-btn"
                  @click="handleDelete(inv)"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 创建邀请码弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">创建邀请码</h2>
          <button class="modal-close" @click="showCreateModal = false">&times;</button>
        </div>
        <form class="modal-form" @submit.prevent="handleCreate">
          <div class="form-group">
            <label class="form-label">使用次数上限</label>
            <input
              v-model.number="createForm.maxUses"
              type="number"
              class="form-input"
              min="1"
              max="100"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">过期时间（可选）</label>
            <input
              v-model="createForm.expiresAt"
              type="datetime-local"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">备注（可选）</label>
            <input
              v-model="createForm.note"
              type="text"
              class="form-input"
              placeholder="例如：测试用户"
            />
          </div>
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="showCreateModal = false">取消</button>
            <button type="submit" class="confirm-btn" :disabled="creating">
              {{ creating ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import invitationApi from '../api/invitation'

const router = useRouter()
const { currentUser, logout } = useAuth()

const invitations = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const creating = ref(false)

const createForm = ref({
  maxUses: 1,
  expiresAt: '',
  note: ''
})

// 加载邀请码列表
const loadInvitations = async () => {
  loading.value = true
  try {
    const result = await invitationApi.list({ includeInactive: true })
    invitations.value = result.invitations || []
  } catch (error) {
    console.error('加载邀请码失败:', error)
  } finally {
    loading.value = false
  }
}

// 创建邀请码
const handleCreate = async () => {
  if (creating.value) return
  
  creating.value = true
  try {
    const data = {
      maxUses: createForm.value.maxUses,
      note: createForm.value.note || undefined
    }
    
    if (createForm.value.expiresAt) {
      data.expiresAt = new Date(createForm.value.expiresAt).toISOString()
    }
    
    await invitationApi.create(data)
    showCreateModal.value = false
    createForm.value = { maxUses: 1, expiresAt: '', note: '' }
    await loadInvitations()
  } catch (error) {
    alert(error.message || '创建失败')
  } finally {
    creating.value = false
  }
}

// 切换状态
const toggleStatus = async (inv) => {
  try {
    await invitationApi.toggleStatus(inv.id, !inv.is_active)
    await loadInvitations()
  } catch (error) {
    alert(error.message || '操作失败')
  }
}

// 删除邀请码
const handleDelete = async (inv) => {
  if (!confirm(`确定删除邀请码 ${inv.code} 吗？`)) return
  
  try {
    await invitationApi.remove(inv.id)
    await loadInvitations()
  } catch (error) {
    alert(error.message || '删除失败')
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '永久有效'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 登出
const handleLogout = () => {
  logout()
  router.push('/login')
}

onMounted(() => {
  loadInvitations()
})
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.navbar {
  height: 60px;
  background: #000;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'JetBrains Mono', monospace;
}

.brand-link {
  color: #fff;
  text-decoration: none;
  font-weight: 800;
  letter-spacing: 1px;
}

.nav-separator {
  color: #666;
}

.nav-current {
  color: #999;
  font-size: 0.9rem;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-name {
  font-size: 0.9rem;
  color: #ccc;
}

.logout-btn {
  padding: 6px 15px;
  background: transparent;
  border: 1px solid #666;
  color: #fff;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  border-color: #fff;
}

.admin-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.admin-title {
  font-size: 1.5rem;
  font-weight: 400;
  margin: 0;
}

.create-btn {
  padding: 10px 20px;
  background: #000;
  color: #fff;
  border: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}

.create-btn:hover {
  background: #333;
}

.table-container {
  background: #fff;
  border: 1px solid #ddd;
}

.loading-state,
.empty-state {
  padding: 60px;
  text-align: center;
  color: #999;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  background: #fafafa;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 1px;
  color: #666;
}

.code-cell {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  letter-spacing: 2px;
}

.note-cell {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  font-size: 0.75rem;
  border-radius: 2px;
}

.status-badge.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.inactive {
  background: #ffebee;
  color: #c62828;
}

.action-cell {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 5px 10px;
  font-size: 0.75rem;
  border: 1px solid #ddd;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: #000;
}

.delete-btn:hover {
  background: #ffebee;
  border-color: #c62828;
  color: #c62828;
}

/* 弹窗样式 */
.modal-overlay {
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
}

.modal-content {
  background: #fff;
  width: 100%;
  max-width: 400px;
  border: 1px solid #000;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
}

.modal-close:hover {
  color: #000;
}

.modal-form {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 600;
  color: #333;
}

.form-input {
  padding: 10px;
  border: 1px solid #ddd;
  font-size: 0.9rem;
}

.form-input:focus {
  outline: none;
  border-color: #000;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 10px;
}

.cancel-btn,
.confirm-btn {
  padding: 10px 20px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #fff;
  border: 1px solid #ddd;
}

.cancel-btn:hover {
  border-color: #000;
}

.confirm-btn {
  background: #000;
  color: #fff;
  border: none;
}

.confirm-btn:hover:not(:disabled) {
  background: #333;
}

.confirm-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
