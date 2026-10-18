<script setup>
import { nextTick, ref } from 'vue';
import MarkdownText from '../components/markdown-text.vue';
import { API_BASE } from "../utils/job"


// 简历文件与后端返回的 resume_id
const resumeFile = ref(null)
const resumeId = ref("")
const uploading = ref(false)

// 输入框里的岗位描述
const jdText = ref("")

// 用户输入
const userInput = ref("")

// 简历JD匹配结果
const matchData = ref({})

// 对话内容，每条消息形如 { id, role, kind, ... }
const messages = ref([])
const loading = ref(false)
const error = ref("")

const listEl = ref(null)
const composerEl = ref(null)

let messageSeq = 0

const CIRCUMFERENCE = 2 * Math.PI * 34

// 分数越高颜色越柔和，避免红绿对撞的刺眼感
function toneOf(score) {
  if (score >= 80) return { ring: "#34d399", text: "text-emerald-600" }
  if (score >= 60) return { ring: "#f59e0b", text: "text-amber-600" }
  return { ring: "#fb7185", text: "text-rose-500" }
}

function dashOffsetOf(score) {
  const percent = Math.min(Math.max(score, 0), 100) / 100
  return CIRCUMFERENCE * (1 - percent)
}

function summaryOf(score) {
  if (score >= 80) return "匹配度很高，你的经历和这个岗位很接近，可以放心投递。"
  if (score >= 60) return "匹配度不错，补上下面这几处缺口，通过率会更高。"
  return "和岗位要求还有一些差距，先看看下面这些建议。"
}

// 追加一条消息，并把视野带到底部
function pushMessage(message) {
  messages.value.push({ id: ++messageSeq, ...message })
  scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  listEl.value?.lastElementChild?.scrollIntoView({ behavior: "smooth", block: "end" })
}

// 上传简历，成功后拿到 resume_id
async function getResume(e) {
  // 重置简历 & JD & 历史会话
  matchData.value = {}
  jdText.value = ""
  messages.value = []
  
  const file = e.target.files?.[0]
  if (!file) return

  error.value = ""
  resumeId.value = ""
  resumeFile.value = null
  uploading.value = true

  try {
    const form = new FormData()
    form.append("file", file)

    const res = await fetch(`${API_BASE}/upload_resume`, {
      method: 'POST',
      body: form
    })

    if (!res.ok) throw new Error("服务器返回 " + res.status)

    const data = await res.json()
    resumeId.value = data.resume_id
    resumeFile.value = file

    pushMessage({ role: "user", kind: "resume", fileName: file.name })
    pushMessage({
      role: "assistant",
      kind: "text",
      text: "简历收到了，把想投的岗位 JD 粘贴到下面发给我，我来算算匹配度。",
    })
  } catch (err) {
    error.value = "简历上传失败：" + err.message
  } finally {
    uploading.value = false
    // 清空 input 的值，否则再选同一份文件不会触发 change
    e.target.value = ""
  }
}

// 发送 JD，获取匹配结果
async function send() {
  if (loading.value || uploading.value) return

  error.value = ""

  const text = userInput.value.trim()
  if (!text) return

  if (!resumeId.value) {
    error.value = "先上传一份简历，我才能算匹配度"
    return
  }

  if (Object.keys(matchData.value).length === 0) { // 第一次发送JD，走/match
    pushMessage({ role: "user", kind: "text", text })
    userInput.value = ""
    composerEl.value?.focus()
    loading.value = true

    try {
      const res = await fetch(`${API_BASE}/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_id: resumeId.value, jd: text })
      })

      if (!res.ok) throw new Error("请求失败：" + res.status)

      const data = await res.json()

      // 记录matchData，后续send走/chat
      matchData.value = data
      jdText.value = text

      pushMessage({
        role: "assistant",
        kind: "result",
        score: Number(data.score) || 0,
        suggestions: data.suggestions ?? [],
      })
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  } else { // 后续发送内容，走/chat
    pushMessage({ role: "user", kind: "text", text })
    userInput.value = ""
    composerEl.value?.focus()
    loading.value = true

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          resume_id: resumeId.value, 
          user_text: text
        })
      })

      if (!res.ok) throw new Error("请求失败：" + res.status)

      const data = await res.json()

      pushMessage({ role: "assistant", kind: "text", text: data.reply })
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }
}

// 回车发送、Shift + Enter 换行；输入法选词那一下回车不算发送
function onComposerKeydown(event) {
  if (event.key !== "Enter" || event.shiftKey) return
  if (event.isComposing || event.keyCode === 229) return

  event.preventDefault()
  send()
}
</script>

<template>
  <div class="chat-shell flex flex-col bg-[#f7f6f3] text-stone-800 antialiased">

    <!-- 对话区：整块高度固定，只有这里自己滚 -->
    <main class="min-h-0 flex-1 overflow-y-auto">
      <div ref="listEl" class="mx-auto flex min-h-full w-full max-w-3xl flex-col gap-4 px-5 pb-6 pt-8 sm:px-8">

        <!-- 空状态 -->
        <div v-if="!messages.length && !loading" class="flex flex-1 flex-col items-center justify-center gap-3 py-16 text-center">
          <span class="grid h-11 w-11 place-items-center rounded-full bg-amber-100 text-amber-600">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z" />
            </svg>
          </span>
          <p class="text-sm font-medium text-stone-700">把简历和岗位对一对</p>
          <p class="max-w-xs text-sm leading-relaxed text-stone-500">
            先在下面传一份简历，再把岗位 JD 粘贴进来发给我。
          </p>
        </div>

        <!-- 消息列表 -->
        <template v-for="m in messages" :key="m.id">

          <!-- 我发的 -->
          <div v-if="m.role === 'user'" class="flex justify-end">
            <div v-if="m.kind === 'resume'" class="max-w-[85%] rounded-lg border border-amber-200/70 bg-amber-100/70 px-3.5 py-2.5">
              <div class="flex items-center gap-2">
                <svg class="h-4 w-4 shrink-0 text-amber-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
                  <path d="M14 2v4a2 2 0 0 0 2 2h4" />
                </svg>
                <span class="truncate text-sm text-stone-800">{{ m.fileName }}</span>
              </div>
              <p class="mt-1 pl-6 text-[11px] text-stone-500">简历 PDF</p>
            </div>

            <div v-else class="max-w-[85%] whitespace-pre-wrap rounded-lg border border-amber-200/70 bg-amber-100/70 px-3.5 py-2.5 text-sm leading-relaxed text-stone-800">{{ m.text }}</div>
          </div>

          <!-- 助手回的 -->
          <div v-else class="flex justify-start">

            <!-- 匹配结果 -->
            <div v-if="m.kind === 'result'" class="w-full max-w-[95%] rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
              <div class="flex flex-col items-center gap-4 sm:flex-row">
                <div class="relative h-20 w-20 shrink-0">
                  <svg class="h-20 w-20 -rotate-90" viewBox="0 0 80 80">
                    <circle cx="40" cy="40" r="34" fill="none" stroke="#ece9e4" stroke-width="7" />
                    <circle
                      cx="40" cy="40" r="34" fill="none"
                      :stroke="toneOf(m.score).ring" stroke-width="7" stroke-linecap="round"
                      :stroke-dasharray="CIRCUMFERENCE" :stroke-dashoffset="dashOffsetOf(m.score)"
                      style="transition: stroke-dashoffset 700ms ease"
                    />
                  </svg>
                  <div class="absolute inset-0 grid place-items-center">
                    <div class="text-center">
                      <div class="text-lg font-semibold leading-none" :class="toneOf(m.score).text">{{ Math.round(m.score) }}</div>
                      <div class="mt-1 text-[10px] text-stone-500">匹配度</div>
                    </div>
                  </div>
                </div>

                <p class="text-sm leading-relaxed text-stone-500">{{ summaryOf(m.score) }}</p>
              </div>

              <div class="mt-4 border-t border-stone-100 pt-4">
                <div class="mb-3 flex items-center gap-2">
                  <svg class="h-4 w-4 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5" />
                    <path d="M9 18h6" />
                    <path d="M10 22h4" />
                  </svg>
                  <h3 class="text-sm font-semibold text-stone-800">改进建议</h3>
                  <span v-if="m.suggestions.length" class="ml-auto text-xs text-stone-400">{{ m.suggestions.length }} 条</span>
                </div>

                <ul v-if="m.suggestions.length" class="space-y-2">
                  <li v-for="(tip, i) in m.suggestions" :key="i" class="flex gap-3 rounded-md bg-stone-50 px-3 py-2.5">
                    <span class="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-amber-100 text-[11px] font-semibold text-amber-700">
                      {{ i + 1 }}
                    </span>
                    <MarkdownText :source="tip" inline />
                  </li>
                </ul>

                <div v-else class="flex items-center gap-2 rounded-md bg-emerald-50 px-3 py-3 text-sm text-emerald-700">
                  <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21.801 10A10 10 0 1 1 17 3.335" />
                    <path d="m9 11 3 3L22 4" />
                  </svg>
                  简历和岗位要求高度吻合，暂时没有需要补充的地方。
                </div>

                <div class="flex items-center gap-2 rounded-md bg-emerald-50 px-3 py-3 text-sm text-emerald-700">
                  <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21.801 10A10 10 0 1 1 17 3.335" />
                    <path d="m9 11 3 3L22 4" />
                  </svg>
                  如果您有疑问，可以继续想我提问~
                </div>
              </div>
            </div>

            <!-- 普通文字：模型回的是 Markdown，交给组件渲染 -->
            <div v-else class="max-w-[85%] rounded-lg border border-stone-200 bg-white px-3.5 py-2.5 shadow-sm">
              <MarkdownText :source="m.text" />
            </div>
          </div>
        </template>

        <!-- 正在分析 -->
        <div v-if="loading" class="flex justify-start">
          <div class="flex items-center gap-1.5 rounded-lg border border-stone-200 bg-white px-4 py-3 shadow-sm">
            <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-300"></span>
            <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-300" style="animation-delay: 150ms"></span>
            <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-300" style="animation-delay: 300ms"></span>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部输入：常驻窗口底部，不参与滚动 -->
    <div class="border-t border-stone-200/70 bg-[#f7f6f3]">
      <div class="mx-auto w-full max-w-3xl px-5 py-4 sm:px-8">

        <div v-if="error" class="mb-2 flex items-start gap-2 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-600">
          <svg class="mt-0.5 h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" x2="12" y1="8" y2="12" />
            <line x1="12" x2="12.01" y1="16" y2="16" />
          </svg>
          <span>{{ error }}</span>
        </div>

        <!-- 当前简历状态 -->
        <div class="mb-2 flex items-center gap-2">
          <span v-if="uploading" class="inline-flex items-center gap-1.5 text-xs text-stone-500">
            <svg class="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M21 12a9 9 0 1 1-6.219-8.56" />
            </svg>
            正在解析简历…
          </span>
          <span v-else-if="resumeFile" class="inline-flex max-w-full items-center gap-1.5 rounded-md border border-emerald-100 bg-emerald-50/70 px-2 py-1 text-xs text-emerald-800">
            <svg class="h-3.5 w-3.5 shrink-0 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
              <path d="M14 2v4a2 2 0 0 0 2 2h4" />
            </svg>
            <span class="truncate">{{ resumeFile.name }}</span>
          </span>
          <span v-else class="text-xs text-stone-400">还没有简历</span>
        </div>

        <!-- 输入框 -->
        <div class="rounded-lg border border-stone-200 bg-white p-2 shadow-sm transition focus-within:border-amber-400 focus-within:ring-2 focus-within:ring-amber-100">
          <textarea
            ref="composerEl"
            v-model="userInput"
            rows="1"
            placeholder="把岗位 JD 粘贴到这里，Enter 发送，Shift + Enter 换行"
            class="field-sizing-content max-h-40 w-full resize-none bg-transparent px-2 py-1.5 text-sm leading-relaxed text-stone-800 placeholder:text-stone-400 focus:outline-none"
            @keydown="onComposerKeydown"
          ></textarea>

          <div class="flex items-center justify-between gap-2 px-0.5 pt-1">
            <label class="inline-flex cursor-pointer items-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium text-stone-500 transition hover:bg-stone-100 hover:text-stone-700 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-amber-300">
              <input type="file" accept=".pdf" class="sr-only" @change="getResume">
              <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48" />
              </svg>
              {{ resumeFile ? "换一份简历" : "上传简历" }}
            </label>

            <button
              type="button"
              class="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-amber-500 text-white transition hover:bg-amber-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300 disabled:cursor-not-allowed disabled:bg-stone-300"
              :disabled="loading || uploading || !userInput.trim()"
              aria-label="发送"
              @click="send"
            >
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 19V5" />
                <path d="m5 12 7-7 7 7" />
              </svg>
            </button>
          </div>
        </div>

        <p class="mt-2 text-center text-[11px] text-stone-400">分析结果由大模型生成，建议结合实际情况判断。</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 77px 是顶部粘性表头的高度：整页正好占一屏，多出来的内容由中间那块自己滚 */
.chat-shell {
  height: calc(100vh - 77px);
  height: calc(100dvh - 77px);
}
</style>
