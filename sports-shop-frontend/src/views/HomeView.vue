<template>
  <div class="home-page">
    <h1 class="page-title">Спортивное питание</h1>

    <div v-if="loading" class="state">ЗАГРУЗКА...</div>

    <div class="products-grid">
      <div v-for="p in products" :key="p.id" class="product-card">
        <div class="card-top">
          <span class="category">{{ p.category || 'СПОРТ' }}</span>
          <span class="stock">В наличии: {{ p.stock }}</span>
        </div>
        
        <div class="card-body">
          <h3>{{ p.name }}</h3>
          <p class="desc">{{ p.description }}</p>
        </div>
        
        <div class="card-footer">
          <span class="price">{{ formatMoney(p.price) }}</span>
          <button class="buy-btn" @click="addToCart(p.id)">В корзину</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://localhost:5000'
const products = ref([])
const loading = ref(false)

async function fetchProducts() {
  loading.value = true
  try {
    const { data } = await axios.get(`${API}/api/products`)
    products.value = data
  } catch (e) { console.error(e) } finally { loading.value = false }
}

async function addToCart(id) {
  const token = localStorage.getItem('token')
  if (!token) { alert('Войдите в аккаунт!'); return }
  try {
    await axios.post(`${API}/api/cart/add`, { product_id: id, quantity: 1 }, { headers: { Authorization: `Bearer ${token}` } })
    alert('Добавлено!')
  } catch (e) { alert('Ошибка') }
}
function formatMoney(n) { return Number(n).toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }) }
onMounted(fetchProducts)
</script>

<style scoped>
.page-title { 
  font-size: 36px; 
  margin-bottom: 40px; 
  padding-bottom: 15px;
  border-bottom: 2px solid var(--cyan);
  color: var(--cyan);
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
}

.products-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
  gap: 30px; 
}

.product-card {
  background: #0a0e17;
  border: 1px solid #1f2a3d;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%);
}
.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 240, 255, 0.15);
  border-color: var(--cyan);
}

.card-top {
  display: flex;
  justify-content: space-between;
  padding: 15px 20px;
  border-bottom: 1px solid #1f2a3d;
  background: #121824;
}
.category { font-weight: 900; text-transform: uppercase; font-size: 12px; color: var(--red); }
.stock { font-weight: 600; font-size: 12px; color: var(--text-muted); }

.card-body { padding: 20px; flex: 1; }
.card-body h3 { font-size: 22px; margin-bottom: 10px; }
.desc { font-size: 14px; font-weight: 500; }

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-top: 1px solid #1f2a3d;
}

.price { font-size: 24px; font-weight: 900; color: var(--text-main); }
.buy-btn { padding: 10px 20px; font-size: 12px; }
</style>