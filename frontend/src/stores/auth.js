import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)

  async function login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    await fetchUser()
  }

  async function fetchUser() {
    try {
      const { data } = await api.get('/auth/me')
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  async function updateProfile(payload) {
    const { data } = await api.patch('/auth/me', payload)
    user.value = data
  }

  return { user, token, isAuthenticated, login, fetchUser, logout, updateProfile }
})
