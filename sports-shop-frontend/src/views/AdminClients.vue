<template>
  <div class="admin-clients">
    <h1 class="page-title">Клиенты</h1>

    <div class="controls">
      <select v-model="sort" @change="fetchClients">
        <option value="name">По алфавиту</option>
        <option value="total">По сумме</option>
        <option value="count">По количеству</option>
      </select>
      <button class="dir-btn" @click="toggleOrder">{{ order === 'asc' ? '↑' : '↓' }}</button>
    </div>

    <div v-if="loading" class="state">ЗАГРУЗКА...</div>

    <table v-else class="poly-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Имя</th>
          <th>Email</th>
          <th>Заказы</th>
          <th>Сумма</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(c, idx) in clients" :key="c.id">
          <td>{{ idx + 1 }}</td>
          <td class="strong">{{ c.full_name }}</td>
          <td>{{ c.email }}</td>
          <td>{{ c.orders_count }}</td>
          <td class="price">{{ formatMoney(c.total_spent) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://localhost:5000'
const clients = ref([])
const loading = ref(false)
const sort = ref('name')
const order = ref('asc')

async function fetchClients() {
  loading.value = true
  try {
    const { data } = await axios.get(`${API}/api/clients`, { params: { sort: sort.value, order: order.value } })
    clients.value = data
  } catch (e) { console.error(e) } finally { loading.value = false }
}
function toggleOrder() { order.value = order.value === 'asc' ? 'desc' : 'asc'; fetchClients() }
function formatMoney(n) { return Number(n).toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }) }
onMounted(fetchClients)
</script>

<style scoped>
.page-title { font-size: 36px; margin-bottom: 40px; padding-bottom: 15px; border-bottom: 2px solid var(--cyan); color: var(--cyan); }

.controls { display: flex; gap: 15px; margin-bottom: 30px; }
.dir-btn { padding: 12px 24px; }

.poly-table {
  width: 100%;
  border-collapse: collapse;
}

.poly-table th, .poly-table td {
  padding: 16px;
  border-bottom: 1px solid #1f2a3d;
  text-align: left;
  font-size: 15px;
}

.poly-table th {
  background: #121824;
  color: var(--cyan);
  text-transform: uppercase;
  font-weight: 900;
  border-top: 1px solid #1f2a3d;
}

.poly-table tr:hover td {
  background: rgba(0, 240, 255, 0.05);
}

.strong { font-weight: 900; color: var(--text-main); }
.price { font-weight: 900; color: var(--red); }
.state { font-weight: 900; font-size: 18px; color: var(--cyan); }
</style>