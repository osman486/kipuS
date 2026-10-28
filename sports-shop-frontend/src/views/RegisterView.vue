<template>
  <div class="register">
    <h2>Регистрация</h2>
    <input v-model="email" type="email" placeholder="Email" />
    <input v-model="password" type="password" placeholder="Пароль" />
    <input v-model="fullName" placeholder="Ваше имя" />
    <button @click="register">Зарегистрироваться</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const email = ref('')
const password = ref('')
const fullName = ref('')

const register = async () => {
  try {
    await axios.post('http://localhost:5000/api/register', {
      email: email.value,
      password: password.value,
      full_name: fullName.value
    })
    alert('Регистрация успешна! Теперь войдите')
    router.push('/login')
  } catch (error) {
    alert('Ошибка: ' + (error.response?.data?.message || 'Неизвестная ошибка'))
  }
}
</script>

<style scoped>
.register {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}
input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}
button {
  width: 100%;
  background-color: #4CAF50;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>