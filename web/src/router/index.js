import { createRouter, createWebHistory } from "vue-router"
import LoginPage from "../pages/login-page.vue"
import JobSeekerPage from "../pages/job-seeker-page.vue"
import HrPage from "../pages/hr-page.vue"
import HeadHunterPage from "../pages/head-hunter-page.vue"
import HomePage from "../pages/home-page.vue"
import { useUserStore } from "../stores/user.js"
import { ROLES } from "../config/roles.js"

const router = createRouter({
    history: createWebHistory(),

    routes: [
        {
            path: '/',
            component: HomePage
        },
        { 
            path: '/login', 
            component: LoginPage,
            meta: {
                showHeader: true
            }
        },
        { 
            path: '/job-seeker', 
            component: JobSeekerPage,
            meta: {
                requireAuth: true,
                role: "job_seeker",
                showHeader: true
            }
        },
        { 
            path: '/hr', 
            component: HrPage,
            meta: {
                requireAuth: true,
                role: "hr",
                showHeader: true
            }
        },
        { 
            path: '/head-hunter', 
            component: HeadHunterPage,
            meta: {
                requireAuth: true,
                role: "head_hunter",
                showHeader: true
            }
        },
    ]
})

router.beforeEach(to => {
    const userStore = useUserStore()

    if (to.meta.requireAuth && !userStore.userId) {
        return "/login"
    }

    if (to.meta.role && userStore.userRole !== to.meta.role) {
        return ROLES[userStore.userRole].path
    }
})

export default router