<template>
  <div class="admin-products">
    <h1 class="page-title">Каталог товаров</h1>

    <!-- Панель фильтров в новом стиле -->
    <div class="filters-panel">
      <!-- Быстрые фильтры -->
      <div class="quick-filters">
        <button 
          v-for="f in quickFilters" 
          :key="f.label"
          class="filter-btn"
          :class="{ active: activeQuick === f.label }"
          @click="applyQuick(f)"
        >{{ f.label }}</button>
      </div>

      <!-- Ручной ввод цены и сортировка -->
      <div class="custom-controls">
        <div class="price-inputs">
          <span class="label">Своя цена:</span>
          <input v-model.number="priceFrom" type="number" placeholder="от" min="0" />
          <span class="dash">—</span>
          <input v-model.number="priceTo" type="number" placeholder="до" min="0" />
          <button class="apply-btn" @click="applyCustom">ОК</button>
          <button class="reset-btn" @click="resetFilters">Сброс</button>
        </div>

        <div class="sort-controls">
          <select v-model="sort" @change="fetchProducts" class="sort-select">
            <option value="price">По цене (дешевле)</option>
            <option value="price_desc">По цене (дороже)</option>
            <option value="name">По названию (А-Я)</option>
          </select>
          <button class="dir-btn" @click="toggleOrder" v-if="sort === 'price' || sort === 'price_desc'">
            {{ order === 'asc' ? '↑' : '↓' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="state">ЗАГРУЗКА...</div>
    <div v-else-if="products.length === 0" class="state">НЕТ ТОВАРОВ ПОД ФИЛЬТР</div>

    <!-- Полигональная сетка -->
    <div v-else class="grid">
      <div v-for="p in products" :key="p.id" class="card">
        <div class="card-top">
          <span class="cat">{{ p.category || 'ТОВАР' }}</span>
          <span class="price">{{ formatMoney(p.price) }}</span>
        </div>
        <div class="card-content">
          <h3>{{ p.name }}</h3>
          <p>{{ p.description }}</p>
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
const activeQuick = ref('Все')

// Состояние для сортировки и кастомных цен
const sort = ref('price')
const order = ref('asc')
const priceFrom = ref(null)
const priceTo = ref(null)

let currentParams = {}

const quickFilters = [
  { label: 'Все', params: {} },
  { label: 'До 100 ₽', params: { price_max: 100 } },
  { label: '100–500 ₽', params: { price_min: 100, price_max: 500 } },
  { label: '500–1000 ₽', params: { price_min: 500, price_max: 1000 } },
  { label: 'От 1000 ₽', params: { price_min: 1000 } },
]

async function fetchProducts() {
  loading.value = true
  
  // Настраиваем параметры сортировки
  let sortParam = 'price'
  let orderParam = order.value
  
  if (sort.value === 'name') { sortParam = 'name'; orderParam = 'asc' }
  if (sort.value === 'price_desc') { sortParam = 'price'; orderParam = 'desc' }
  if (sort.value === 'price') { sortParam = 'price'; orderParam = order.value }

  try {
    const { data } = await axios.get(`${API}/api/products`, { 
      params: { sort: sortParam, order: orderParam, ...currentParams } 
    })
    products.value = data
  } catch (e) { 
    console.error(e) 
  } finally { 
    loading.value = false 
  }
}

function applyQuick(f) {
  activeQuick.value = f.label
  priceFrom.value = f.params.price_min ?? null
  priceTo.value = f.params.price_max ?? null
  currentParams = { ...f.params }
  fetchProducts()
}

function applyCustom() {
  activeQuick.value = ''
  const params = {}
  if (priceFrom.value !== null && priceFrom.value !== '') params.price_min = priceFrom.value
  if (priceTo.value !== null && priceTo.value !== '') params.price_max = priceTo.value
  currentParams = params
  fetchProducts()
}

function resetFilters() {
  priceFrom.value = null
  priceTo.value = null
  activeQuick.value = 'Все'
  currentParams = {}
  fetchProducts()
}

function toggleOrder() {
  order.value = order.value === 'asc' ? 'desc' : 'asc'
  fetchProducts()
}

function formatMoney(n) { 
  return Number(n).toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }) 
}

onMounted(fetchProducts)
</script>

<style scoped>
.page-title { font-size: 36px; margin-bottom: 40px; padding-bottom: 15px; border-bottom: 2px solid var(--cyan); color: var(--cyan); }

/* Панель фильтров */
.filters-panel {
  background: #121824;
  border: 1px solid #1f2a3d;
  padding: 20px;
  margin-bottom: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%);
}

.quick-filters { display: flex; gap: 10px; flex-wrap: wrap; }
.filter-btn { 
  background: transparent; 
  color: var(--cyan); 
  border: 1px solid var(--cyan); 
  padding: 8px 16px;
  font-size: 13px;
}
.filter-btn:hover, .filter-btn.active { 
  background: var(--cyan); 
  color: var(--bg-dark); 
}

/* Кастомные контролы */
.custom-controls { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; }
.price-inputs { display: flex; align-items: center; gap: 10px; }
.price-inputs .label { font-weight: 700; text-transform: uppercase; font-size: 13px; color: var(--text-muted); }
.price-inputs input { width: 90px; padding: 8px 12px; }
.price-inputs .dash { color: var(--text-muted); }
.apply-btn { padding: 8px 16px; background: var(--cyan); color: var(--bg-dark); }
.reset-btn { padding: 8px 16px; background: transparent; color: var(--red); border: 1px solid var(--red); }
.reset-btn:hover { background: var(--red); color: white; }

.sort-controls { display: flex; align-items: center; gap: 10px; }
.sort-select { padding: 8px 12px; width: 200px; border: 1px solid var(--cyan); }
.dir-btn { padding: 8px 16px; background: var(--cyan); color: var(--bg-dark); font-weight: 900; }

/* Сетка карточек */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }

.card { 
  background: #0a0e17;
  border: 1px solid #1f2a3d; 
  display: flex; 
  flex-direction: column;
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%);
  transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 240, 255, 0.15);
  border-color: var(--cyan);
}

.card-top {
  display: flex; justify-content: space-between; align-items: center;
  padding: 15px; background: #121824; border-bottom: 1px solid #1f2a3d;
}
.cat { font-weight: 900; text-transform: uppercase; font-size: 12px; color: var(--cyan); }
.card-top .price { font-weight: 900; color: var(--red); font-size: 16px; }

.card-content { padding: 20px; }
.card-content h3 { font-size: 18px; margin-bottom: 10px; color: var(--text-main); }
.card-content p { font-size: 14px; color: var(--text-muted); }

.state { font-weight: 900; font-size: 18px; padding: 20px 0; color: var(--cyan); text-align: center; }
</style>