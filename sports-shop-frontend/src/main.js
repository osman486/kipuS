import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Если вы удалили файл main.css, удалите и эту строку:
// import './assets/main.css' 

const app = createApp(App)
app.use(router)
app.mount('#app')