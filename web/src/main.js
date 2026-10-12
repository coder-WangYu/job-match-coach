import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router/index.js'
import { createPinia } from "pinia"

// createPinia() 要在 app.use(router) 之前注册
// 否则守卫里取 store 可能报错
createApp(App)
    .use(createPinia())
    .use(router)
    .mount('#app')
