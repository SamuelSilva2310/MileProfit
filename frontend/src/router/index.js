import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
  },
  {
    path: '/activities',
    name: 'Activities',
    component: () => import('../views/ActivitiesView.vue'),
  },
  {
    path: '/earnings',
    name: 'Earnings',
    component: () => import('../views/EarningsView.vue'),
  },
  {
    path: '/expenses',
    name: 'Expenses',
    component: () => import('../views/ExpensesView.vue'),
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return '/login'
  }
  if (auth.isAuthenticated && !auth.user) {
    await auth.fetchUser()
  }
})

export default router
