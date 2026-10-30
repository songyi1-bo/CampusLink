import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/Home/index.vue'
import { useAuthStore } from '../stores/auth'
import { safeRedirect } from './redirect'

declare module 'vue-router' {
  interface RouteMeta { requiresAuth?: boolean; guestOnly?: boolean }
}

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/ride', component: () => import('../views/Ride/index.vue') },
    { path: '/quest', component: () => import('../views/Quest/index.vue') },
    { path: '/book', component: () => import('../views/Book/index.vue') },
    { path: '/ride/mine', component: () => import('../views/Ride/Mine.vue'), meta: { requiresAuth: true } },
    { path: '/ride/new', component: () => import('../views/Ride/Edit.vue'), meta: { requiresAuth: true } },
    { path: '/ride/:id/edit', component: () => import('../views/Ride/Edit.vue'), meta: { requiresAuth: true } },
    { path: '/ride/:id', component: () => import('../views/Ride/Detail.vue') },
    { path: '/quest/mine', component: () => import('../views/Quest/Mine.vue'), meta: { requiresAuth: true } },
    { path: '/quest/new', component: () => import('../views/Quest/Edit.vue'), meta: { requiresAuth: true } },
    { path: '/quest/:id/edit', component: () => import('../views/Quest/Edit.vue'), meta: { requiresAuth: true } },
    { path: '/quest/:id', component: () => import('../views/Quest/Detail.vue') },
    { path: '/book/mine', component: () => import('../views/Book/Mine.vue'), meta: { requiresAuth: true } },
    { path: '/book/new', component: () => import('../views/Book/Edit.vue'), meta: { requiresAuth: true } },
    { path: '/book/:id/edit', component: () => import('../views/Book/Edit.vue'), meta: { requiresAuth: true } },
    { path: '/book/:id', component: () => import('../views/Book/Detail.vue') },
    { path: '/login', component: () => import('../views/Login/index.vue'), meta: { guestOnly: true } },
    { path: '/register', component: () => import('../views/Register/index.vue'), meta: { guestOnly: true } },
    { path: '/profile', component: () => import('../views/Profile/index.vue'), meta: { requiresAuth: true } },
    { path: '/:pathMatch(.*)*', component: () => import('../views/NotFound.vue') },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  try {
    await auth.restore()
  } catch {
    if (to.meta.requiresAuth) return { path: '/login', query: { redirect: to.fullPath, reason: 'connection' } }
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) return safeRedirect(to.query.redirect)
})
