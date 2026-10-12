<script setup>
import { ref } from 'vue';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';

const API_BASE = "http://127.0.0.1:8000"
const userStore = useUserStore()
const router = useRouter()
const username = ref("")

// 用户登录
async function login() {
    try {
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username.value })
        })

        if(!res.ok) return

        const data = await res.json()
        userStore.setUser(data.user_id, data.username)

        router.push('/job-seeker')
    } catch(e) {
        throw new Error(e)
    }
}

// 用户注册
async function register() {
    try {
        const res = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username.value })
        })

        if(!res.ok) return
    } catch(e) {
        throw new Error(e)
    }
}
</script>

<template>
    <p>用户名：<input class="border-2" v-model="username" type="text"></p>
    <button class="border-2" @click="login">登录</button>
    <button class="border-2" @click="register">注册</button>
</template>