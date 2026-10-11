<script setup>
import { computed, ref } from 'vue';

const API_BASE = "http://127.0.0.1:8000"

// 简历文件与后端返回的 resume_id
const resumeFile = ref(null)
const resumeId = ref("")
const uploading = ref(false)

// 岗位描述
const jd = ref("")

// 匹配结果
const score = ref(0)
const suggestions = ref([])
const hasResult = ref(false)
const loading = ref(false)
const error = ref("")

// 圆环进度：用半径算出周长，再按分数换算 dashoffset
const CIRCUMFERENCE = 2 * Math.PI * 34
const dashOffset = computed(() => {
  const percent = Math.min(Math.max(score.value, 0), 100) / 100
  return CIRCUMFERENCE * (1 - percent)
})

const scoreText = computed(() => Math.round(score.value))

// 分数越高颜色越柔和，避免红绿对撞的刺眼感
const tone = computed(() => {
  if (score.value >= 80) return { ring: "#34d399", text: "text-emerald-600" }
  if (score.value >= 60) return { ring: "#f59e0b", text: "text-amber-600" }
  return { ring: "#fb7185", text: "text-rose-500" }
})

const scoreSummary = computed(() => {
  if (score.value >= 80) return "匹配度很高，你的经历和这个岗位很接近，可以放心投递。"
  if (score.value >= 60) return "匹配度不错，补上下面这几处缺口，通过率会更高。"
  return "和岗位要求还有一些差距，先看看下面这些建议。"
})

// 上传简历，成功后拿到 resume_id
async function getResume(e) {
  const file = e.target.files?.[0]
  if (!file) return

  error.value = ""
  resumeFile.value = file
  resumeId.value = ""
  uploading.value = true

  try {
    const form = new FormData()
    form.append("file", file)

    const res = await fetch(`${API_BASE}/upload-resume`, {
      method: 'POST',
      body: form
    })

    if (!res.ok) throw new Error("服务器返回 " + res.status)

    const data = await res.json()
    resumeId.value = data.resume_id
  } catch (err) {
    error.value = "简历上传失败：" + err.message
  } finally {
    uploading.value = false
  }
}

// 提交简历与 JD，获取匹配结果
async function match() {
  error.value = ""

  if (!resumeId.value.trim() || !jd.value.trim()) {
    error.value = "请先上传简历，并填写岗位 JD"
    return
  }

  loading.value = true

  try {
    const res = await fetch(`${API_BASE}/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_id: resumeId.value, jd: jd.value })
    })

    if (!res.ok) throw new Error("请求失败：" + res.status)

    const data = await res.json()
    score.value = Number(data.score) || 0
    suggestions.value = data.suggestions ?? []
    hasResult.value = true
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#f7f6f3] text-stone-800 antialiased">
    <div class="mx-auto flex max-w-5xl flex-col gap-6 px-5 py-10 sm:px-8 sm:py-14">

      <!-- 顶部标题 -->
      <header class="flex items-start gap-3">
        <span class="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-amber-400 text-white shadow-sm">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
            <rect width="20" height="14" x="2" y="6" rx="2" />
          </svg>
        </span>
        <div class="min-w-0">
          <h1 class="text-xl font-semibold tracking-tight text-stone-900">求职匹配助手</h1>
          <p class="mt-0.5 text-sm leading-relaxed text-stone-500">
            上传简历、贴上岗位 JD，看看你们的匹配度，并拿到具体的修改建议。
          </p>
        </div>
      </header>

      <!-- 输入区：简历 + JD -->
      <div class="grid gap-5 md:grid-cols-2">

        <!-- 简历 -->
        <section class="flex flex-col rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
          <div class="mb-3 flex items-center gap-2">
            <span class="grid h-6 w-6 place-items-center rounded-md bg-amber-50 text-amber-600">
              <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
                <path d="M14 2v4a2 2 0 0 0 2 2h4" />
              </svg>
            </span>
            <h2 class="text-sm font-semibold text-stone-800">简历</h2>
            <span class="ml-auto text-xs text-stone-400">PDF</span>
          </div>

          <label class="group flex flex-1 cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-stone-300 bg-stone-50/60 px-4 py-8 text-center transition hover:border-amber-400 hover:bg-amber-50/60">
            <input type="file" accept=".pdf" class="hidden" @change="getResume">
            <svg class="h-6 w-6 text-stone-400 transition group-hover:text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" x2="12" y1="3" y2="15" />
            </svg>
            <span class="text-sm font-medium text-stone-600 transition group-hover:text-amber-700">点击选择简历文件</span>
            <span class="text-xs text-stone-400">支持 .pdf 格式</span>
          </label>

          <div v-if="uploading" class="mt-3 flex items-center gap-2 text-xs text-stone-500">
            <svg class="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M21 12a9 9 0 1 1-6.219-8.56" />
            </svg>
            正在解析简历…
          </div>

          <div v-else-if="resumeFile" class="mt-3 flex items-center gap-2 rounded-md border border-emerald-100 bg-emerald-50/70 px-3 py-2">
            <svg class="h-4 w-4 shrink-0 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
              <path d="M14 2v4a2 2 0 0 0 2 2h4" />
            </svg>
            <span class="truncate text-xs text-emerald-800">{{ resumeFile.name }}</span>
          </div>
        </section>

        <!-- 岗位描述 -->
        <section class="flex flex-col rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
          <div class="mb-3 flex items-center gap-2">
            <span class="grid h-6 w-6 place-items-center rounded-md bg-amber-50 text-amber-600">
              <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="20" height="14" x="2" y="6" rx="2" />
                <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
              </svg>
            </span>
            <h2 class="text-sm font-semibold text-stone-800">岗位描述</h2>
          </div>

          <textarea
            v-model="jd"
            rows="8"
            placeholder="把岗位职责、任职要求粘贴到这里…"
            class="min-h-44 w-full flex-1 resize-none rounded-lg border border-stone-200 bg-stone-50/60 p-3 text-sm leading-relaxed text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-100"
          ></textarea>

          <div class="mt-2 text-right text-xs text-stone-400">{{ jd.trim().length }} 字</div>
        </section>
      </div>

      <!-- 操作区 -->
      <div class="flex flex-col gap-3">
        <button
          class="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-amber-500 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-amber-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300 disabled:cursor-not-allowed disabled:bg-stone-300 sm:w-auto sm:self-start sm:px-8"
          :disabled="loading || uploading"
          @click="match"
        >
          <svg v-if="loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
          <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" />
            <path d="M20 3v4" />
            <path d="M22 5h-4" />
            <path d="M4 17v2" />
            <path d="M5 18H3" />
          </svg>
          {{ loading ? "分析中…" : "开始匹配" }}
        </button>

        <div v-if="error" class="flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-600">
          <svg class="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" x2="12" y1="8" y2="12" />
            <line x1="12" x2="12.01" y1="16" y2="16" />
          </svg>
          <span>{{ error }}</span>
        </div>
      </div>

      <!-- 结果 -->
      <section v-if="hasResult" class="rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm sm:p-6">
        <div class="flex flex-col items-center gap-5 sm:flex-row sm:gap-6">
          <div class="relative h-28 w-28 shrink-0">
            <svg class="h-28 w-28 -rotate-90" viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="34" fill="none" stroke="#ece9e4" stroke-width="7" />
              <circle
                cx="40" cy="40" r="34" fill="none"
                :stroke="tone.ring" stroke-width="7" stroke-linecap="round"
                :stroke-dasharray="CIRCUMFERENCE" :stroke-dashoffset="dashOffset"
                style="transition: stroke-dashoffset 700ms ease"
              />
            </svg>
            <div class="absolute inset-0 grid place-items-center">
              <div class="text-center">
                <div class="text-2xl font-semibold leading-none" :class="tone.text">{{ scoreText }}</div>
                <div class="mt-1 text-[11px] text-stone-400">匹配度</div>
              </div>
            </div>
          </div>

          <div class="min-w-0 flex-1 text-center sm:text-left">
            <h2 class="text-base font-semibold text-stone-900">匹配分析</h2>
            <p class="mt-1 text-sm leading-relaxed text-stone-500">{{ scoreSummary }}</p>
          </div>
        </div>

        <div class="mt-5 border-t border-stone-100 pt-5">
          <div class="mb-3 flex items-center gap-2">
            <svg class="h-4 w-4 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5" />
              <path d="M9 18h6" />
              <path d="M10 22h4" />
            </svg>
            <h3 class="text-sm font-semibold text-stone-800">改进建议</h3>
            <span v-if="suggestions.length" class="ml-auto text-xs text-stone-400">{{ suggestions.length }} 条</span>
          </div>

          <ul v-if="suggestions.length" class="space-y-2">
            <li
              v-for="(tip, i) in suggestions"
              :key="i"
              class="flex gap-3 rounded-md bg-stone-50 px-3 py-2.5"
            >
              <span class="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-amber-100 text-[11px] font-semibold text-amber-700">
                {{ i + 1 }}
              </span>
              <span class="text-sm leading-relaxed text-stone-600">{{ tip }}</span>
            </li>
          </ul>

          <div v-else class="flex items-center gap-2 rounded-md bg-emerald-50 px-3 py-3 text-sm text-emerald-700">
            <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21.801 10A10 10 0 1 1 17 3.335" />
              <path d="m9 11 3 3L22 4" />
            </svg>
            简历和岗位要求高度吻合，暂时没有需要补充的地方。
          </div>
        </div>
      </section>

      <footer class="pt-2 text-center text-xs text-stone-400 sm:text-left">
        分析结果由大模型生成，建议结合自己的实际情况判断。
      </footer>
    </div>
  </div>
</template>
