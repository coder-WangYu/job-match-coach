<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ROLE_OPTIONS, ROLES } from '../config/roles'

const API_BASE = "http://127.0.0.1:8000"

const router = useRouter()
const userStore = useUserStore()

// 当前是登录还是注册
const mode = ref('login')

const email = ref("")
const password = ref("")
const confirmPassword = ref("")
const role = ref("")
const showPassword = ref(false)

// 角色下拉：展开状态与键盘高亮到哪一项
const roleBox = ref(null)
const roleOpen = ref(false)
const roleActiveIndex = ref(-1)

const loading = ref(false)
const error = ref("")
const notice = ref("")

// 字段被碰过之后才显示错误，避免刚进页面就满屏飘红
const touched = reactive({ email: false, password: false, confirmPassword: false, role: false })

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

const roleError = computed(() => {
  if (mode.value !== "register") return ""
  if (!role.value) return "请选择你的角色"
  return ""
})

const canSubmit = computed(
  () => !emailError.value && !passwordError.value && !confirmError.value && !roleError.value
)

const roleLabel = computed(
  () => ROLE_OPTIONS.find((option) => option.value === role.value)?.label ?? "请选择你的角色"
)

// 错误、展开、常态三种边框样式，互斥地挑一个
const roleFieldClass = computed(() => {
  if (touched.role && roleError.value) return "border-rose-300 focus:border-rose-400 focus:ring-rose-100"
  if (roleOpen.value) return "border-amber-400 ring-2 ring-amber-100"
  return "border-stone-200 hover:border-stone-300 focus:border-amber-400 focus:ring-amber-100"
})

function toggleRole() {
  roleOpen.value = !roleOpen.value

  if (roleOpen.value) {
    const index = ROLE_OPTIONS.findIndex((option) => option.value === role.value)
    roleActiveIndex.value = index >= 0 ? index : 0
  }
}

// 收起时如果还没选，就当用户碰过这个字段了，这时才提示
function closeRole() {
  if (roleOpen.value) touched.role = true
  roleOpen.value = false
  roleActiveIndex.value = -1
}

function pickRole(option) {
  role.value = option.value
  touched.role = true
  closeRole()
}

function moveRoleActive(step) {
  if (!roleOpen.value) {
    toggleRole()
    return
  }

  const total = ROLE_OPTIONS.length
  roleActiveIndex.value = (roleActiveIndex.value + step + total) % total
}

// 上下键移动、回车选中、Esc 收起
function onRoleKeydown(event) {
  if (event.key === "ArrowDown") {
    event.preventDefault()
    moveRoleActive(1)
  } else if (event.key === "ArrowUp") {
    event.preventDefault()
    moveRoleActive(-1)
  } else if (event.key === "Enter" || event.key === " ") {
    event.preventDefault()
    if (roleOpen.value && roleActiveIndex.value >= 0) {
      pickRole(ROLE_OPTIONS[roleActiveIndex.value])
    } else {
      toggleRole()
    }
  } else if (event.key === "Escape" || event.key === "Tab") {
    closeRole()
  }
}

// 点到面板外面就收起来
function onDocumentClick(event) {
  if (!roleOpen.value) return
  if (roleBox.value && !roleBox.value.contains(event.target)) closeRole()
}

onMounted(() => document.addEventListener("click", onDocumentClick))
onBeforeUnmount(() => document.removeEventListener("click", onDocumentClick))

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
  closeRole()
  // closeRole 会把 role 标记成已碰过，这里再清掉
  touched.role = false
}

async function submit() {
  touched.email = true
  touched.password = true
  touched.confirmPassword = true
  touched.role = true
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

// 把后端返回的错误翻成一句人话，Supabase 原本给的是英文
async function readError(res) {
  const data = await res.json().catch(() => null)
  const detail = typeof data?.detail === "string" ? data.detail : ""

  if (/already registered|already been registered/i.test(detail)) return "这个邮箱已经注册过了，直接登录吧"
  if (/invalid login credentials/i.test(detail)) return "邮箱或密码不正确"
  if (/email not confirmed/i.test(detail)) return "邮箱还没验证，先去邮箱里点一下确认链接"
  if (/rate limit|too many/i.test(detail)) return "操作太频繁了，稍等一下再试"

  if (detail) return detail
  if (res.status === 422) return "请求格式不对，检查一下邮箱和密码"
  return `请求失败（${res.status}）`
}

// 注册：成功后切回登录态，邮箱留在输入框里
async function register() {
  const res = await fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.value.trim(), password: password.value, role: role.value })
  })

  if (!res.ok) {
    throw new Error(await readError(res))
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
    body: JSON.stringify({ email: email.value.trim(), password: password.value })
  })

  if (!res.ok) {
    throw new Error(await readError(res))
  }

  const data = await res.json()
  userStore.setUser(data.user_id, data.email, data.role)
  
  // 跳转到角色对应页面
  router.push(ROLES[data.role].path)
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f7f6f3] text-stone-800 antialiased">
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

            <!-- 角色：只有注册时需要 -->
            <div v-if="mode === 'register'">
              <label id="role-label" for="role" class="mb-1.5 block text-sm font-medium text-stone-700">角色</label>
              <div ref="roleBox" class="relative">
                <span
                  class="pointer-events-none absolute inset-y-0 left-3 grid place-items-center transition"
                  :class="role ? 'text-amber-500' : 'text-stone-400'"
                >
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                </span>

                <button
                  id="role"
                  type="button"
                  role="combobox"
                  aria-haspopup="listbox"
                  aria-controls="role-listbox"
                  :aria-expanded="roleOpen"
                  :aria-activedescendant="roleOpen && roleActiveIndex >= 0 ? `role-option-${ROLE_OPTIONS[roleActiveIndex].value}` : undefined"
                  :aria-invalid="Boolean(touched.role && roleError)"
                  class="flex w-full items-center justify-between gap-2 rounded-lg border bg-white py-2.5 pl-9 pr-3 text-left text-sm transition focus:outline-none focus:ring-2"
                  :class="roleFieldClass"
                  @click="toggleRole"
                  @keydown="onRoleKeydown"
                >
                  <span :class="role ? 'text-stone-800' : 'text-stone-400'">{{ roleLabel }}</span>
                  <svg
                    class="h-4 w-4 shrink-0 text-stone-400 transition-transform duration-150"
                    :class="roleOpen ? 'rotate-180' : ''"
                    viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                  >
                    <path d="m6 9 6 6 6-6" />
                  </svg>
                </button>

                <Transition name="role-pop">
                  <ul
                    v-if="roleOpen"
                    id="role-listbox"
                    role="listbox"
                    aria-labelledby="role-label"
                    class="absolute z-20 mt-2 w-full origin-top rounded-lg border border-stone-200 bg-white p-1 shadow-lg"
                  >
                    <li
                      v-for="(option, i) in ROLE_OPTIONS"
                      :id="`role-option-${option.value}`"
                      :key="option.value"
                      role="option"
                      :aria-selected="option.value === role"
                      class="flex cursor-pointer items-center justify-between gap-2 rounded-md px-3 py-2.5 text-sm transition"
                      :class="[
                        i === roleActiveIndex ? 'bg-amber-50 text-amber-900' : 'text-stone-600',
                        option.value === role ? 'font-medium' : '',
                      ]"
                      @click="pickRole(option)"
                      @mouseenter="roleActiveIndex = i"
                    >
                      {{ option.label }}
                      <svg
                        v-if="option.value === role"
                        class="h-4 w-4 shrink-0 text-amber-500"
                        viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
                      >
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                    </li>
                  </ul>
                </Transition>
              </div>
              <p v-if="touched.role && roleError" class="mt-1.5 text-xs text-rose-500">{{ roleError }}</p>
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

<style scoped>
/* 下拉面板的进出场：轻微下落 + 淡入 */
.role-pop-enter-active,
.role-pop-leave-active {
  transition: opacity 120ms ease, transform 120ms ease;
}

.role-pop-enter-from,
.role-pop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
