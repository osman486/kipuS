<template>
  <div class="cart">
    <h1>🛒 Корзина</h1>
    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="cart.items.length === 0" class="empty-cart">
      <p>Корзина пуста</p>
      <router-link to="/" class="continue-btn">Перейти в каталог</router-link>
    </div>
    <div v-else>
      <div v-for="item in cart.items" :key="item.product_id" class="cart-item">
        <img :src="`https://picsum.photos/id/${item.product_id + 10}/80/80`" class="item-image">
        <div class="item-info">
          <h3>{{ item.name }}</h3>
          <p>{{ item.price }} ₽ / шт</p>
        </div>
        <div class="item-quantity">
          <button @click="updateQuantity(item.product_id, item.quantity - 1)" :disabled="item.quantity <= 1">-</button>
          <span>{{ item.quantity }}</span>
          <button @click="updateQuantity(item.product_id, item.quantity + 1)">+</button>
        </div>
        <div class="item-total">
          <span>{{ item.total }} ₽</span>
          <button @click="removeItem(item.product_id)" class="remove-btn">🗑️</button>
        </div>
      </div>
      <div class="cart-summary">
        <div class="cart-total"><strong>Итого:</strong> <span>{{ cart.total }} ₽</span></div>
        <button @click="checkout" class="checkout-btn">Оформить заказ</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const cart = ref({ items: [], total: 0 })
const loading = ref(true)

const fetchCart = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    alert('Сначала войдите в систему')
    router.push('/login')
    return
  }
  try {
    const res = await axios.get('http://localhost:5000/api/cart', {
      headers: { Authorization: `Bearer ${token}` }
    })
    cart.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const updateQuantity = async (productId, newQuantity) => {
  if (newQuantity < 1) return
  const token = localStorage.getItem('token')
  await axios.put(`http://localhost:5000/api/cart/update/${productId}`, { quantity: newQuantity }, {
    headers: { Authorization: `Bearer ${token}` }
  })
  await fetchCart()
}

const removeItem = async (productId) => {
  if (!confirm('Удалить товар?')) return
  const token = localStorage.getItem('token')
  await axios.delete(`http://localhost:5000/api/cart/remove/${productId}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  await fetchCart()
}

const checkout = () => alert('Оформление заказа будет позже')

onMounted(fetchCart)
</script>

<style scoped>
.cart * { color: black !important; }
.cart { max-width: 1000px; margin: 20px auto; padding: 20px; background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
.cart-item { display: flex; align-items: center; justify-content: space-between; padding: 15px; border-bottom: 1px solid #eee; flex-wrap: wrap; gap: 15px; }
.item-image { width: 80px; height: 80px; object-fit: cover; border-radius: 10px; }
.item-info { flex: 2; min-width: 150px; }
.item-quantity { display: flex; align-items: center; gap: 10px; }
.item-quantity button { width: 30px; height: 30px; border: 1px solid #ddd; background: white; cursor: pointer; border-radius: 5px; }
.item-total { display: flex; align-items: center; gap: 15px; min-width: 120px; justify-content: flex-end; }
.remove-btn { background: none; border: none; font-size: 20px; cursor: pointer; }
.cart-summary { margin-top: 20px; padding-top: 20px; border-top: 2px solid #eee; text-align: right; }
.cart-total { font-size: 20px; margin-bottom: 15px; }
.checkout-btn { background-color: #4CAF50; color: white !important; border: none; padding: 12px 30px; border-radius: 30px; cursor: pointer; }
.empty-cart { text-align: center; padding: 50px; }
.continue-btn { display: inline-block; background-color: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 30px; }
.loading { text-align: center; padding: 50px; }
</style>