import { defineStore } from "pinia"
import { ref } from "vue"

export const useUserStore = defineStore('user', () => {
    const userId = ref(localStorage.getItem('userId') || '')
    const userEmail = ref(localStorage.getItem('userEmail') || '')
    const userRole = ref(localStorage.getItem('userRole') || '')

    // 持久化用户
    function setUser(id, email, role) {
        userId.value = id
        userEmail.value = email
        userRole.value = role

        localStorage.setItem('userId', id)
        localStorage.setItem('userEmail', email)
        localStorage.setItem('userRole', role)
    }

    // 退出登录
    function clearUser() {
        userId.value = ""
        userEmail.value = ""
        userRole.value = ""

        localStorage.removeItem('userId')
        localStorage.removeItem('userEmail')
        localStorage.removeItem('userRole')
    }

    return { 
        userId, 
        userEmail, 
        userRole, 
        setUser,
        clearUser
    }
})
