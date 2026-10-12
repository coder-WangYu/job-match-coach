import { createRouter, createWebHistory } from "vue-router"
import LoginPage from "../pages/login-page.vue"
import JobSeekerPage from "../pages/job-seeker-page.vue"
import HrPage from "../pages/hr-page.vue"
import HeadHunterPage from "../pages/head-hunter-page.vue"
import HomePage from "../pages/home-page.vue"
import { useUserStore } from "../stores/user.js"

const router = createRouter({
    history: createWebHistory(),

    routes: [
        {
            path: '/',
            component: HomePage
        },
        { 
            path: '/login', 
            component: LoginPage 
        },
        { 
            path: '/job-seeker', 
            component: JobSeekerPage,
            meta: {
                requireAuth: true
            }
        },
        { 
            path: '/hr', 
            component: HrPage,
            meta: {
                requireAuth: true
            }
        },
        { 
            path: '/head-hunter', 
            component: HeadHunterPage,
            meta: {
                requireAuth: true
            }
        },
    ]
})

router.beforeEach(to => {
    const userStore = useUserStore()

    if (to.meta.requireAuth && !userStore.userId) {
        return "/login"
    }
})

export default router