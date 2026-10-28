<template>
  <div class="app-container">
    <!-- Шапка со скошенным углом -->
    <nav class="navbar">
      <RouterLink to="/" class="nav-brand">
        <span class="brand-icon">S</span> SPORT<span class="accent">SHOP</span>
      </RouterLink>
      
      <div class="nav-links">
        <RouterLink to="/">Главная</RouterLink>
        <RouterLink to="/admin/clients">Клиенты</RouterLink>
        <RouterLink to="/admin/products">Каталог</RouterLink>
        <RouterLink to="/admin">Админка</RouterLink>
        <RouterLink to="/cart">Корзина</RouterLink>
        
        <template v-if="!isLoggedIn">
          <RouterLink to="/login" class="poly-btn">Вход</RouterLink>
        </template>
        <template v-else>
          <a href="#" @click.prevent="logout" class="poly-btn btn-red">Выйти</a>
        </template>
      </div>
    </nav>

    <!-- Контент -->
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoggedIn = ref(false)

onMounted(() => {
  isLoggedIn.value = !!localStorage.getItem('token')
})

function logout() {
  localStorage.removeItem('token')
  isLoggedIn.value = false
  router.push('/login')
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700;900&display=swap');

:root {
  --bg-dark: #0a0e17;
  --bg-panel: #121824;
  --cyan: #00f0ff;
  --red: #ff003c;
  --text-main: #ffffff;
  --text-muted: #8b9bb4;
}

/* ГЕОМЕТРИЧЕСКИЙ ФОН */
body {
  margin: 0;
  padding: 0;
  font-family: 'Montserrat', sans-serif;
  background-color: var(--bg-dark);
  background-image: 
    linear-gradient(135deg, rgba(0, 240, 255, 0.05) 25%, transparent 25%),
    linear-gradient(225deg, rgba(255, 0, 60, 0.05) 25%, transparent 25%),
    linear-gradient(45deg, rgba(0, 240, 255, 0.05) 25%, transparent 25%),
    linear-gradient(315deg, rgba(255, 0, 60, 0.05) 25%, transparent 25%);
  background-position: 10px 0, 10px 0, 0 0, 0 0;
  background-size: 20px 20px;
  background-repeat: repeat;
  color: var(--text-main);
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4 { 
  color: var(--text-main); 
  font-weight: 900; 
  text-transform: uppercase; 
  margin-top: 0; 
  letter-spacing: 1px;
}
p { color: var(--text-muted); line-height: 1.6; }

/* КНОПКИ СО СКОШЕННЫМИ УГЛАМИ (POLY) */
button, .poly-btn {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 14px;
  cursor: pointer;
  padding: 12px 24px;
  border: none;
  background-color: var(--cyan);
  color: var(--bg-dark);
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
button:hover, .poly-btn:hover {
  background-color: var(--text-main);
  transform: translateY(-2px);
}
button.btn-red, .poly-btn.btn-red {
  background-color: var(--red);
  color: var(--text-main);
}
button.btn-red:hover, .poly-btn.btn-red:hover {
  background-color: #ff3366;
}

/* ИНПУТЫ */
input, select, textarea {
  font-family: 'Montserrat', sans-serif;
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #2a3a55;
  border-radius: 0;
  outline: none;
  background-color: var(--bg-panel);
  color: var(--text-main);
  font-weight: 500;
  transition: border-color 0.2s;
}
input:focus, select:focus, textarea:focus {
  border-color: var(--cyan);
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
}

/* ШАПКА */
.app-container { min-height: 100vh; display: flex; flex-direction: column; }

.navbar {
  background-color: var(--bg-panel);
  padding: 0 40px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 2px solid var(--cyan);
  box-shadow: 0 4px 20px rgba(0, 240, 255, 0.1);
}

.nav-brand {
  color: var(--text-main);
  text-decoration: none;
  font-weight: 900;
  font-size: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  letter-spacing: 2px;
}
.nav-brand .accent { color: var(--cyan); }
.brand-icon {
  background: var(--cyan);
  color: var(--bg-dark);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%); /* Гексагон */
  font-size: 20px;
}

.nav-links { display: flex; align-items: center; gap: 24px; }
.nav-links a:not(.poly-btn) {
  color: var(--text-main);
  text-decoration: none;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 14px;
  transition: color 0.2s;
}
.nav-links a:not(.poly-btn):hover, 
.nav-links a.router-link-active:not(.poly-btn) { 
  color: var(--cyan); 
  text-shadow: 0 0 8px var(--cyan);
}

/* КОНТЕНТНАЯ ПАНЕЛЬ */
.main-content { 
  flex: 1; 
  padding: 40px; 
  max-width: 1200px; 
  margin: 40px auto; 
  width: 100%; 
  background: var(--bg-panel);
  border: 1px solid #1f2a3d;
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 30px), calc(100% - 30px) 100%, 0 100%);
}
</style>