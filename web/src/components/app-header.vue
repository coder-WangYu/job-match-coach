<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()

// 头像下拉的展开状态
const menuBox = ref(null)
const menuOpen = ref(false)

function toggleMenu() {
    menuOpen.value = !menuOpen.value
}

function closeMenu() {
    menuOpen.value = false
}

// 点到菜单外面就收起来
function onDocumentClick(event) {
    if (!menuOpen.value) return
    if (menuBox.value && !menuBox.value.contains(event.target)) closeMenu()
}

onMounted(() => document.addEventListener("click", onDocumentClick))
onBeforeUnmount(() => document.removeEventListener("click", onDocumentClick))

// 退出登录
function logout() {
    closeMenu()
    userStore.clearUser()

    router.push("/login")
}
</script>

<template>
    <!-- 顶部：品牌与返回 -->
    <header class="mx-auto flex w-full max-w-5xl items-center gap-3 px-5 py-5 sm:px-8">
        <router-link to="/" class="flex items-center gap-2.5">
            <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-amber-400 text-white shadow-sm">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                    stroke-linecap="round" stroke-linejoin="round">
                    <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
                    <rect width="20" height="14" x="2" y="6" rx="2" />
                </svg>
            </span>
            <span class="flex min-w-0 flex-col leading-tight">
                <span class="truncate text-sm font-semibold text-stone-900">同频</span>
                <span class="truncate text-[11px] text-stone-400">人岗智配Agent</span>
            </span>
        </router-link>

        <router-link to="/"
            class="ml-auto inline-flex items-center gap-1.5 text-sm text-stone-500 transition hover:text-stone-800">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="m12 19-7-7 7-7" />
                <path d="M19 12H5" />
            </svg>
            返回首页
        </router-link>

        <!-- 用户头像：登录后才显示，点一下向下弹出菜单 -->
        <div v-if="userStore.userId" ref="menuBox" class="relative">
            <button type="button" aria-haspopup="menu" :aria-expanded="menuOpen" aria-label="账号菜单"
                class="grid h-9 w-9 place-items-center rounded-full ring-1 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300"
                :class="menuOpen
                    ? 'bg-amber-100 text-amber-700 ring-amber-300'
                    : 'bg-amber-50 text-amber-600 ring-amber-200 hover:bg-amber-100 hover:text-amber-700'"
                @click="toggleMenu" @keydown.esc="closeMenu">
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                    stroke-linecap="round" stroke-linejoin="round">
                    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                </svg>
            </button>

            <Transition name="menu-pop">
                <div v-if="menuOpen" role="menu"
                    class="absolute right-0 z-20 mt-2 w-40 origin-top-right rounded-lg border border-stone-200 bg-white p-1 shadow-lg">
                    <!-- TODO：编辑信息的跳转逻辑 -->
                    <button type="button" role="menuitem" @click="closeMenu"
                        class="flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-sm text-stone-600 transition hover:bg-stone-50 hover:text-stone-900">
                        <svg class="h-4 w-4 shrink-0 text-stone-400" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                            <path
                                d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z" />
                        </svg>
                        编辑信息
                    </button>

                    <button type="button" role="menuitem" @click="logout"
                        class="flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-sm text-rose-600 transition hover:bg-rose-50">
                        <svg class="h-4 w-4 shrink-0 text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                            <polyline points="16 17 21 12 16 7" />
                            <line x1="21" x2="9" y1="12" y2="12" />
                        </svg>
                        退出登录
                    </button>
                </div>
            </Transition>
        </div>
    </header>
</template>

<style scoped>
/* 下拉菜单的进出场：轻微下落 + 淡入 */
.menu-pop-enter-active,
.menu-pop-leave-active {
    transition: opacity 120ms ease, transform 120ms ease;
}

.menu-pop-enter-from,
.menu-pop-leave-to {
    opacity: 0;
    transform: translateY(-4px) scale(0.98);
}
</style>
