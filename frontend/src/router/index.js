import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminView from '../views/AdminView.vue'
import { getToken, getUser } from '../api/auth'

const routes = [
  // 公开路由（无需登录）
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { public: true }
  },
  
  // 需要登录的路由
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true
  },
  
  // 管理员路由
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView,
    meta: { requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = getToken()
  const user = getUser()
  const isLoggedIn = !!token
  const isAdmin = user?.role === 'admin'
  
  // 公开路由：已登录用户访问登录/注册页时重定向到首页
  if (to.meta.public) {
    if (isLoggedIn) {
      next('/')
    } else {
      next()
    }
    return
  }
  
  // 需要登录的路由：未登录重定向到登录页
  if (!isLoggedIn) {
    next('/login')
    return
  }
  
  // 管理员路由：非管理员重定向到首页
  if (to.meta.requiresAdmin && !isAdmin) {
    next('/')
    return
  }
  
  // 其他情况正常通过
  next()
})

export default router
