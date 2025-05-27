import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/components/Home.vue';
import DirectQueryDB from '@/components/DirectQueryDB.vue';
import DirectQueryDoc from '@/components/DirectQueryDoc.vue';
import Login from '@/components/Login.vue';
import Signup from '@/components/Signup.vue';
import store from '@/store';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
  { path: '/home', component: Home, meta: { requiresAuth: true } },
  { path: '/db-query', component: DirectQueryDB, meta: { requiresAuth: true } },
  { path: '/doc-query', component: DirectQueryDoc, meta: { requiresAuth: true } },
  { path: '/login', component: Login },
  { path: '/signup', component: Signup },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!store.state.access_token;
  console.log('Navigating to:', to.path, 'Authenticated:', isAuthenticated);
  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log('Redirecting to login: User not authenticated');
    next('/login');
  } else {
    next();
  }
});

export default router;