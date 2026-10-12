import { defineStore } from "pinia"
import { ref } from "vue"

export const useUserStore = defineStore('user', () => {
    const userId = ref(localStorage.getItem('userId') || '')
    const username = ref(localStorage.getItem('username') || "")

    function setUser(id, name) {
        userId.value = id
        username.value = name
        localStorage.setItem('userId', id)
        localStorage.setItem('username', name)
    }

    return { userId, username, setUser }
})