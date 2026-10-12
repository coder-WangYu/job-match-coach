<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const API_BASE = "http://127.0.0.1:8000"

const router = useRouter()
const userStore = useUserStore()

// 当前是登录还是注册
const mode = ref('login')

const email = ref("")
const password = ref("")
const confirmPassword = ref("")
const showPassword = ref(false)

const loading = ref(false)
const error = ref("")
const notice = ref("")

// 字段被碰过之后才显示错误，避免刚进页面就满屏飘红
const touched = reactive({ email: false, password: false, confirmPassword: false })

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

// 注册密码规则：8-16 位英文或数字，大小写字母和数字都要有
const passwordRules = computed(() => [
  { label: "8-16 位，只能用英文和数字", ok: /^[A-Za-z0-9]{8,16}$/.test(password.value) },
  { label: "包含大写字母", ok: /[A-Z]/.test(password.value) },
  { label: "包含小写字母", ok: /[a-z]/.test(password.value) },
  { label: "包含数字", ok: /\d/.test(password.value) },
])

const passwordStrongEnough = computed(() => passwordRules.value.every((rule) => rule.ok))

const emailError = computed(() => {
  if (!email.value.trim()) return "请输入邮箱"
  if (!EMAIL_RE.test(email.value.trim())) return "邮箱格式不正确，例如 name@example.com"
  return ""
})

const passwordError = computed(() => {
  if (!password.value) return "请输入密码"
  // 登录只要求非空：早先注册的账号未必符合现在的密码规则
  if (mode.value === "register" && !passwordStrongEnough.value) return "密码不符合下面这几条要求"
  return ""
})

const confirmError = computed(() => {
  if (mode.value !== "register") return ""
  if (!confirmPassword.value) return "请再输入一次密码"
  if (confirmPassword.value !== password.value) return "两次输入的密码不一致"
  return ""
})

const canSubmit = computed(() => !emailError.value && !passwordError.value && !confirmError.value)

// 登录 / 注册之间切换，顺手清掉上一次的输入和提示
function switchMode(next) {
  if (mode.value === next) return

  mode.value = next
  password.value = ""
  confirmPassword.value = ""
  error.value = ""
  notice.value = ""
  touched.password = false
  touched.confirmPassword = false
}

async function submit() {
  touched.email = true
  touched.password = true
  touched.confirmPassword = true
  error.value = ""
  notice.value = ""

  if (!canSubmit.value) return

  loading.value = true

  try {
    if (mode.value === "register") {
      await register()
    } else {
      await login()
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 注册：成功后切回登录态，邮箱留在输入框里
async function register() {
  const res = await fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: email.value.trim(), password: password.value })
  })

  if (!res.ok) {
    throw new Error(res.status === 500 ? "这个邮箱可能已经被注册过了" : `注册失败（${res.status}）`)
  }

  mode.value = 'login'
  password.value = ""
  confirmPassword.value = ""
  touched.password = false
  touched.confirmPassword = false
  notice.value = "注册成功，用刚才的邮箱登录吧"
}

// 登录：拿到用户信息写进 pinia，再进求职者页
async function login() {
  const res = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: email.value.trim(), password: password.value })
  })

  if (!res.ok) {
    if (res.status === 404) throw new Error("这个邮箱还没有注册，先去注册一个")

    const data = await res.json().catch(() => null)
    throw new Error(data?.detail || `登录失败（${res.status}）`)
  }

  const data = await res.json()
  userStore.setUser(data.user_id, data.username)

  router.push('/job-seeker')
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f7f6f3] text-stone-800 antialiased">

    <!-- 顶部：品牌与返回 -->
    <header class="mx-auto flex w-full max-w-5xl items-center gap-3 px-5 py-5 sm:px-8">
      <router-link to="/" class="flex items-center gap-2.5">
        <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-amber-400 text-white shadow-sm">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
            <rect width="20" height="14" x="2" y="6" rx="2" />
          </svg>
        </span>
        <span class="flex min-w-0 flex-col leading-tight">
          <span class="truncate text-sm font-semibold text-stone-900">同频</span>
          <span class="truncate text-[11px] text-stone-400">人岗智配Agent</span>
        </span>
      </router-link>

      <router-link to="/" class="ml-auto inline-flex items-center gap-1.5 text-sm text-stone-500 transition hover:text-stone-800">
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m12 19-7-7 7-7" />
          <path d="M19 12H5" />
        </svg>
        返回首页
      </router-link>
    </header>

    <main class="flex flex-1 items-start justify-center px-5 pb-16 pt-2 sm:items-center sm:px-8">
      <div class="w-full max-w-md">
        <div class="rounded-lg border border-stone-200/80 bg-white p-6 shadow-sm sm:p-7">

          <!-- 登录 / 注册 切换 -->
          <div class="grid grid-cols-2 gap-1 rounded-lg bg-stone-100 p-1">
            <button
              type="button"
              class="rounded-md px-3 py-2 text-sm font-medium transition"
              :class="mode === 'login' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-700'"
              :aria-pressed="mode === 'login'"
              @click="switchMode('login')"
            >
              登录
            </button>
            <button
              type="button"
              class="rounded-md px-3 py-2 text-sm font-medium transition"
              :class="mode === 'register' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-700'"
              :aria-pressed="mode === 'register'"
              @click="switchMode('register')"
            >
              注册
            </button>
          </div>

          <h1 class="mt-5 text-lg font-semibold text-stone-900">
            {{ mode === 'login' ? '欢迎回来' : '创建账号' }}
          </h1>
          <p class="mt-1 text-sm leading-relaxed text-stone-500">
            {{ mode === 'login' ? '用注册时的邮箱登录，继续你的匹配分析。' : '注册后就能保存简历、查看匹配结果。' }}
          </p>

          <form class="mt-5 flex flex-col gap-4" novalidate @submit.prevent="submit">

            <!-- 邮箱 -->
            <div>
              <label for="email" class="mb-1.5 block text-sm font-medium text-stone-700">邮箱</label>
              <div class="relative">
                <span class="pointer-events-none absolute inset-y-0 left-3 grid place-items-center text-stone-400">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="20" height="16" x="2" y="4" rx="2" />
                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                </span>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  autocomplete="email"
                  placeholder="name@example.com"
                  class="w-full rounded-lg border bg-white py-2.5 pl-9 pr-3 text-sm text-stone-800 placeholder:text-stone-400 transition focus:outline-none focus:ring-2"
                  :class="touched.email && emailError
                    ? 'border-rose-300 focus:border-rose-400 focus:ring-rose-100'
                    : 'border-stone-200 focus:border-amber-400 focus:ring-amber-100'"
                  :aria-invalid="Boolean(touched.email && emailError)"
                  @blur="touched.email = true"
                >
              </div>
              <p v-if="touched.email && emailError" class="mt-1.5 text-xs text-rose-500">{{ emailError }}</p>
            </div>

            <!-- 密码 -->
            <div>
              <label for="password" class="mb-1.5 block text-sm font-medium text-stone-700">密码</label>
              <div class="relative">
                <span class="pointer-events-none absolute inset-y-0 left-3 grid place-items-center text-stone-400">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="18" height="11" x="3" y="11" rx="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                </span>
                <input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  :autocomplete="mode === 'register' ? 'new-password' : 'current-password'"
                  :placeholder="mode === 'register' ? '8-16 位英文和数字' : '请输入密码'"
                  class="w-full rounded-lg border bg-white py-2.5 pl-9 pr-11 text-sm text-stone-800 placeholder:text-stone-400 transition focus:outline-none focus:ring-2"
                  :class="touched.password && passwordError
                    ? 'border-rose-300 focus:border-rose-400 focus:ring-rose-100'
                    : 'border-stone-200 focus:border-amber-400 focus:ring-amber-100'"
                  :aria-invalid="Boolean(touched.password && passwordError)"
                  @blur="touched.password = true"
                >
                <button
                  type="button"
                  class="absolute inset-y-0 right-0 grid w-11 place-items-center text-stone-400 transition hover:text-stone-600"
                  :aria-label="showPassword ? '隐藏密码' : '显示密码'"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="showPassword" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.8 10.8 0 0 1-1.444 2.49" />
                    <path d="M14.084 14.158a3 3 0 0 1-4.242-4.242" />
                    <path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143" />
                    <path d="m2 2 20 20" />
                  </svg>
                  <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </button>
              </div>
              <p v-if="touched.password && passwordError" class="mt-1.5 text-xs text-rose-500">{{ passwordError }}</p>

              <!-- 注册时才需要看的密码规则 -->
              <ul v-if="mode === 'register'" class="mt-3 space-y-1.5">
                <li
                  v-for="rule in passwordRules"
                  :key="rule.label"
                  class="flex items-center gap-2 text-xs transition"
                  :class="rule.ok ? 'text-emerald-600' : 'text-stone-400'"
                >
                  <span class="grid h-3.5 w-3.5 shrink-0 place-items-center">
                    <svg v-if="rule.ok" class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20 6 9 17l-5-5" />
                    </svg>
                    <span v-else class="h-1.5 w-1.5 rounded-full bg-stone-300"></span>
                  </span>
                  {{ rule.label }}
                </li>
              </ul>
            </div>

            <!-- 确认密码：只有注册时需要 -->
            <div v-if="mode === 'register'">
              <label for="confirm" class="mb-1.5 block text-sm font-medium text-stone-700">确认密码</label>
              <div class="relative">
                <span class="pointer-events-none absolute inset-y-0 left-3 grid place-items-center text-stone-400">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="18" height="11" x="3" y="11" rx="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                </span>
                <input
                  id="confirm"
                  v-model="confirmPassword"
                  :type="showPassword ? 'text' : 'password'"
                  autocomplete="new-password"
                  placeholder="再输入一次密码"
                  class="w-full rounded-lg border bg-white py-2.5 pl-9 pr-3 text-sm text-stone-800 placeholder:text-stone-400 transition focus:outline-none focus:ring-2"
                  :class="touched.confirmPassword && confirmError
                    ? 'border-rose-300 focus:border-rose-400 focus:ring-rose-100'
                    : 'border-stone-200 focus:border-amber-400 focus:ring-amber-100'"
                  :aria-invalid="Boolean(touched.confirmPassword && confirmError)"
                  @blur="touched.confirmPassword = true"
                >
              </div>
              <p v-if="touched.confirmPassword && confirmError" class="mt-1.5 text-xs text-rose-500">{{ confirmError }}</p>
            </div>

            <!-- 服务端返回的提示 -->
            <div v-if="notice" class="flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3.5 py-3 text-sm text-emerald-700">
              <svg class="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21.801 10A10 10 0 1 1 17 3.335" />
                <path d="m9 11 3 3L22 4" />
              </svg>
              <span>{{ notice }}</span>
            </div>

            <div v-if="error" class="flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-600">
              <svg class="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" x2="12" y1="8" y2="12" />
                <line x1="12" x2="12.01" y1="16" y2="16" />
              </svg>
              <span>{{ error }}</span>
            </div>

            <button
              type="submit"
              class="mt-1 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-amber-500 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-amber-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300 disabled:cursor-not-allowed disabled:bg-stone-300"
              :disabled="loading"
            >
              <svg v-if="loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
              {{ loading ? "处理中…" : (mode === 'login' ? '登录' : '注册') }}
            </button>
          </form>
        </div>

        <p class="mt-4 text-center text-xs text-stone-500">
          分析结果由大模型生成，建议结合实际情况判断。
        </p>
      </div>
    </main>
  </div>
</template>
