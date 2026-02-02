<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">MULTIMO</h1>
        <p class="auth-subtitle">登录您的账户</p>
      </div>
      
      <form class="auth-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label" for="email">邮箱</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="请输入邮箱"
            required
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label" for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="请输入密码"
            required
            :disabled="loading"
          />
        </div>
        
        <div v-if="error" class="form-error">
          {{ error }}
        </div>
        
        <button type="submit" class="submit-btn" :disabled="loading || !isFormValid">
          <span v-if="!loading">登 录</span>
          <span v-else>登录中...</span>
        </button>
      </form>
      
      <div class="auth-footer">
        <p>还没有账户？<router-link to="/register" class="auth-link">立即注册</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login } = useAuth()

const form = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

const isFormValid = computed(() => {
  return form.value.email.trim() !== '' && form.value.password.trim() !== ''
})

const handleLogin = async () => {
  if (!isFormValid.value || loading.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    await login(form.value.email, form.value.password)
    router.push('/')
  } catch (err) {
    error.value = err.message || '登录失败，请检查邮箱和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #F8F9FA 0%, #E8EAF0 50%, #F0F2F8 100%);
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border: 1px solid #000;
  padding: 40px;
}

.auth-header {
  text-align: center;
  margin-bottom: 40px;
}

.auth-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: 2px;
  margin: 0 0 10px 0;
}

.auth-subtitle {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.auth-form {
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
  letter-spacing: 1px;
  color: #333;
}

.form-input {
  padding: 12px 15px;
  border: 1px solid #ddd;
  font-size: 0.9rem;
  transition: border-color 0.2s;
  background: #fafafa;
}

.form-input:focus {
  outline: none;
  border-color: #000;
  background: #fff;
}

.form-input:disabled {
  background: #f0f0f0;
  cursor: not-allowed;
}

.form-error {
  padding: 10px 15px;
  background: #fff0f0;
  border: 1px solid #ffcdd2;
  color: #c62828;
  font-size: 0.85rem;
}

.submit-btn {
  padding: 15px;
  background: #000;
  color: #fff;
  border: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #333;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  font-size: 0.9rem;
  color: #666;
}

.auth-link {
  color: #000;
  font-weight: 600;
  text-decoration: none;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>
