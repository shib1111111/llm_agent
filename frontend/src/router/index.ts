import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import store from '../store';

// Layouts & Pages
import Home from '../views/Home.vue';
import Login from '../views/auth/Login.vue';
import Signup from '../views/auth/Signup.vue';
import DbQuery from '../views/DbQuery.vue';
import DocQuery from '../views/DocQuery.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guestOnly: true }
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup,
    meta: { guestOnly: true }
  },
  {
    path: '/db-query',
    name: 'DbQuery',
    component: DbQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/doc-query',
    name: 'DocQuery',
    component: DocQuery,
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    // Always scroll to top
    return { top: 0 };
  },
});

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  
  // Check if the route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
  } 
  // Check if the route is for guests only (like login/signup) and user is already authenticated
  else if (to.meta.guestOnly && isAuthenticated) {
    next({ name: 'Home' });
  } 
  else {
    next();
  }
});

export default router;