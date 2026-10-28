<template>
  <div class="admin">
    <h2>Админ-панель</h2>
    <div class="form-card">
      <h3>{{ editing ? 'Редактировать товар' : 'Добавить товар' }}</h3>
      <form @submit.prevent="saveProduct">
        <input v-model="form.name" placeholder="Название" required />
        <input v-model="form.price" type="number" step="0.01" placeholder="Цена" required />
        <input v-model="form.stock" type="number" placeholder="Количество" />
        <input v-model="form.category" placeholder="Категория" />
        <textarea v-model="form.description" placeholder="Описание"></textarea>
        
        <div class="upload-area">
          <input type="file" @change="handleFileUpload" accept="image/*" />
          <button type="button" @click="uploadImage" :disabled="!selectedFile">Загрузить картинку</button>
          <div v-if="form.image_url" class="preview">
            <img :src="'http://localhost:5000/api/uploads/' + form.image_url" style="max-width:100px" />
          </div>
        </div>
        
        <div class="form-buttons">
          <button type="submit">{{ editing ? 'Сохранить' : 'Добавить' }}</button>
          <button type="button" @click="cancelEdit" v-if="editing">Отмена</button>
        </div>
      </form>
    </div>

    <div class="products-list">
      <h3>Список товаров</h3>
      <div v-for="p in products" :key="p.id" class="product-row">
        <img :src="`https://picsum.photos/id/${p.id + 10}/50/50`" class="product-thumb" />
        <div class="product-info"><strong>{{ p.name }}</strong> — {{ p.price }} ₽ ({{ p.stock }} шт)</div>
        <div class="product-actions">
          <button @click="editProduct(p)" class="edit-btn">✏️</button>
          <button @click="removeProduct(p.id)" class="delete-btn">🗑️</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const products = ref([])
const form = ref({ name: '', price: 0, stock: 0, category: '', description: '', image_url: '' })
const editing = ref(false)
const editingId = ref(null)
const selectedFile = ref(null)

const fetchProducts = async () => {
  const res = await axios.get('http://localhost:5000/api/products')
  products.value = res.data
}

const saveProduct = async () => {
  const token = localStorage.getItem('token')
  const url = editing.value ? `http://localhost:5000/api/admin/products/${editingId.value}` : 'http://localhost:5000/api/admin/products'
  const method = editing.value ? 'put' : 'post'
  await axios[method](url, form.value, { headers: { Authorization: `Bearer ${token}` } })
  alert(editing.value ? 'Обновлено' : 'Добавлено')
  fetchProducts()
  cancelEdit()
}

const editProduct = (p) => {
  editing.value = true
  editingId.value = p.id
  form.value = { ...p }
  if (form.value.image_url) form.value.image_url = form.value.image_url.replace('http://localhost:5000/api/uploads/', '')
}

const cancelEdit = () => {
  editing.value = false
  editingId.value = null
  form.value = { name: '', price: 0, stock: 0, category: '', description: '', image_url: '' }
  selectedFile.value = null
}

const removeProduct = async (id) => {
  if (!confirm('Удалить?')) return
  const token = localStorage.getItem('token')
  await axios.delete(`http://localhost:5000/api/admin/products/${id}`, { headers: { Authorization: `Bearer ${token}` } })
  fetchProducts()
}

const handleFileUpload = (e) => { selectedFile.value = e.target.files[0] }
const uploadImage = async () => {
  if (!selectedFile.value) return
  const token = localStorage.getItem('token')
  const fd = new FormData()
  fd.append('file', selectedFile.value)
  const res = await axios.post('http://localhost:5000/api/upload', fd, {
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' }
  })
  form.value.image_url = res.data.filename
  alert('Картинка загружена')
}

onMounted(fetchProducts)
</script>

<style scoped>
.admin * { color: black !important; }
.admin { max-width: 1000px; margin: 20px auto; padding: 20px; background: linear-gradient(135deg, #f5f7fa, #c3cfe2); border-radius: 20px; }
.form-card, .products-list { background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
input, textarea { width: 100%; margin: 8px 0; padding: 10px; border: 2px solid #ddd; border-radius: 8px; }
button { background: linear-gradient(135deg, #4CAF50, #45a049); color: white; border: none; padding: 8px 16px; margin: 5px; border-radius: 8px; cursor: pointer; }
.product-row { display: flex; align-items: center; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee; }
.product-thumb { width: 50px; height: 50px; border-radius: 10px; }
.product-info { flex: 1; margin-left: 15px; }
.edit-btn, .delete-btn { padding: 5px 12px; }
.delete-btn { background: linear-gradient(135deg, #f44336, #d32f2f); }
.upload-area { margin: 10px 0; padding: 15px; border: 2px dashed #4CAF50; border-radius: 10px; text-align: center; }
</style>