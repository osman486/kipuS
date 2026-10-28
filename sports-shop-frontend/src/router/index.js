import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import CartView from '../views/CartView.vue'
import AdminView from '../views/AdminView.vue'
import AdminClients from '../views/AdminClients.vue'
import AdminProducts from '../views/AdminProducts.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  { path: '/cart', component: CartView },
  { path: '/admin', component: AdminView },
  { path: '/admin/clients', component: AdminClients },
  { path: '/admin/products', component: AdminProducts }
]

const router = createRouter({ history: createWebHistory(), routes })
export default router