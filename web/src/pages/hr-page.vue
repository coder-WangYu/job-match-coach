<script setup>
import { computed, ref } from "vue"
import MarkdownText from '../components/markdown-text.vue'

const API_BASE = "http://127.0.0.1:8000"

// 岗位描述
const jd = ref("")

// 已上传的简历：{ id, filename }
const resumes = ref([])
const uploading = ref(false)

// 筛选结果，在接口返回的基础上补上追问需要的那几个字段
const candidates = ref([])
const screening = ref(false)
const error = ref("")

// 当前展开了追问的候选人
const openId = ref("")

// 三档归类，顺序就是页面上从左到右的顺序
const CATEGORIES = [
    {
        key: "重点关注",
        hint: "分数靠前，建议优先联系",
        dot: "bg-amber-500",
        chip: "border-amber-200 bg-amber-50 text-amber-700",
        ring: "#f59e0b",
        text: "text-amber-600",
    },
    {
        key: "可约面",
        hint: "基本达标，可以约一面",
        dot: "bg-emerald-500",
        chip: "border-emerald-200 bg-emerald-50 text-emerald-700",
        ring: "#34d399",
        text: "text-emerald-600",
    },
    {
        key: "淘汰",
        hint: "差距明显，先放一放",
        dot: "bg-stone-300",
        chip: "border-stone-200 bg-stone-100 text-stone-500",
        ring: "#a8a29e",
        text: "text-stone-500",
    },
]

const CIRCUMFERENCE = 2 * Math.PI * 34

function dashOffsetOf(score) {
    const percent = Math.min(Math.max(score, 0), 100) / 100
    return CIRCUMFERENCE * (1 - percent)
}

// 按三档归类，每档内部按分数从高到低
const groups = computed(() =>
    CATEGORIES.map((category) => ({
        ...category,
        items: candidates.value
            .filter((item) => item.category === category.key)
            .sort((a, b) => b.score - a.score),
    }))
)

// 后端万一返回了没约定的分类，单独兜底一栏，免得简历凭空消失
const unclassified = computed(() =>
    candidates.value.filter((item) => !CATEGORIES.some((category) => category.key === item.category))
)

// 上传时接口会带回文件名，这里按 resume_id 反查
function nameOf(resumeId) {
    return resumes.value.find((item) => item.id === resumeId)?.filename || resumeId.slice(0, 8)
}

function shortId(resumeId) {
    return resumeId.slice(0, 8)
}

// 上传简历：支持一次选多份，也支持分几次陆续加进来
async function uploadResumes(e) {
    const files = [...(e.target.files || [])]
    if (!files.length) return

    error.value = ""
    uploading.value = true

    try {
        for (const file of files) {
            const form = new FormData()
            form.append("file", file)

            const res = await fetch(`${API_BASE}/upload_resume`, {
                method: "POST",
                body: form
            })

            if (!res.ok) throw new Error(`${file.name} 上传失败（${res.status}）`)

            const data = await res.json()
            resumes.value.push({ id: data.resume_id, filename: data.filename || file.name })
        }
    } catch (err) {
        error.value = err.message
    } finally {
        uploading.value = false
        // 清空 input 的值，否则再选同一批文件不会触发 change
        e.target.value = ""
    }
}

// 用当前 JD 过一遍已上传的简历
async function startScreen() {
    error.value = ""

    if (!jd.value.trim()) {
        error.value = "先把岗位 JD 填上"
        return
    }

    if (!resumes.value.length) {
        error.value = "先上传至少一份简历"
        return
    }

    screening.value = true
    openId.value = ""

    try {
        const res = await fetch(`${API_BASE}/hr/screen`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jd: jd.value.trim(),
                resume_ids: resumes.value.map((item) => item.id),
            })
        })

        if (!res.ok) throw new Error("筛选失败：" + res.status)

        const data = await res.json()
        candidates.value = (data.results ?? []).map((item) => ({
            ...item,
            score: Number(item.score) || 0,
            chat: [],
            chatInput: "",
            chatLoading: false,
        }))
    } catch (err) {
        error.value = err.message
    } finally {
        screening.value = false
    }
}

function toggleAsk(item) {
    openId.value = openId.value === item.resume_id ? "" : item.resume_id
}

// 就这位候选人追问一句，后端按 resume_id 分线程记住上下文
async function ask(item) {
    if (item.chatLoading) return

    const text = item.chatInput.trim()
    if (!text) return

    error.value = ""
    item.chat.push({ role: "user", text })
    item.chatInput = ""
    item.chatLoading = true

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume_id: item.resume_id, user_text: text })
        })

        if (!res.ok) throw new Error("追问失败：" + res.status)

        const data = await res.json()
        item.chat.push({ role: "assistant", text: data.reply })
    } catch (err) {
        error.value = err.message
    } finally {
        item.chatLoading = false
    }
}

// 回车发送、Shift + Enter 换行；输入法选词那一下回车不算发送
function onAskKeydown(event, item) {
    if (event.key !== "Enter" || event.shiftKey) return
    if (event.isComposing || event.keyCode === 229) return

    event.preventDefault()
    ask(item)
}

// 换一批简历重新筛
function clearAll() {
    resumes.value = []
    candidates.value = []
    openId.value = ""
    error.value = ""
}
</script>

<template>
    <div class="min-h-screen bg-[#f7f6f3] text-stone-800 antialiased">
        <div class="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8">

            <header class="mb-6">
                <h1 class="text-xl font-semibold tracking-tight text-stone-900">批量筛选简历</h1>
                <p class="mt-1 text-sm leading-relaxed text-stone-500">
                    填好岗位要求，把收到的简历一次或分几次传上来，跑完按分数分成三档。
                </p>
            </header>

            <!-- 输入区：JD + 简历 -->
            <div class="grid gap-5 lg:grid-cols-2">

                <!-- 岗位 JD -->
                <section class="flex flex-col rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
                    <div class="mb-3 flex items-center gap-2">
                        <span class="grid h-6 w-6 place-items-center rounded-md bg-amber-50 text-amber-600">
                            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect width="20" height="14" x="2" y="6" rx="2" />
                                <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
                            </svg>
                        </span>
                        <h2 class="text-sm font-semibold text-stone-800">岗位要求</h2>
                        <span class="ml-auto text-xs text-stone-400">{{ jd.trim().length }} 字</span>
                    </div>

                    <textarea
                        v-model="jd"
                        rows="7"
                        placeholder="把岗位职责、任职要求粘贴到这里…"
                        class="min-h-40 w-full flex-1 resize-none rounded-lg border border-stone-200 bg-stone-50/60 p-3 text-sm leading-relaxed text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-100"
                    ></textarea>
                </section>

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
                        <span class="ml-auto text-xs text-stone-400">已上传 {{ resumes.length }} 份</span>
                    </div>

                    <label class="group flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-stone-300 bg-stone-50/60 px-4 py-6 text-center transition hover:border-amber-400 hover:bg-amber-50/60 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-amber-300">
                        <input type="file" accept=".pdf" multiple class="sr-only" @change="uploadResumes">
                        <svg class="h-5 w-5 text-stone-400 transition group-hover:text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                            <polyline points="17 8 12 3 7 8" />
                            <line x1="12" x2="12" y1="3" y2="15" />
                        </svg>
                        <span class="text-sm font-medium text-stone-600 transition group-hover:text-amber-700">
                            {{ resumes.length ? "继续添加简历" : "点击选择简历文件" }}
                        </span>
                        <span class="text-xs text-stone-400">支持一次多选，也可以分几批传</span>
                    </label>

                    <div v-if="uploading" class="mt-3 flex items-center gap-2 text-xs text-stone-500">
                        <svg class="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                        </svg>
                        正在解析…
                    </div>

                    <ul v-else-if="resumes.length" class="mt-3 flex max-h-32 flex-wrap gap-1.5 overflow-y-auto">
                        <li
                            v-for="item in resumes"
                            :key="item.id"
                            class="inline-flex max-w-full items-center gap-1.5 rounded-md border border-stone-200 bg-stone-50 px-2 py-1 text-xs text-stone-600"
                        >
                            <svg class="h-3 w-3 shrink-0 text-stone-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
                                <path d="M14 2v4a2 2 0 0 0 2 2h4" />
                            </svg>
                            <span class="truncate">{{ item.filename }}</span>
                        </li>
                    </ul>
                </section>
            </div>

            <!-- 操作区 -->
            <div class="mt-5 flex flex-col gap-3">
                <div class="flex flex-wrap items-center gap-3">
                    <button
                        class="inline-flex items-center justify-center gap-2 rounded-lg bg-amber-500 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-amber-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300 disabled:cursor-not-allowed disabled:bg-stone-300"
                        :disabled="screening || uploading"
                        @click="startScreen"
                    >
                        <svg v-if="screening" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                        </svg>
                        <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="11" cy="11" r="8" />
                            <path d="m21 21-4.3-4.3" />
                        </svg>
                        {{ screening ? "筛选中…" : "开始筛选" }}
                    </button>

                    <button
                        v-if="resumes.length || candidates.length"
                        type="button"
                        class="rounded-lg px-3 py-2 text-sm text-stone-500 transition hover:bg-white hover:text-stone-800"
                        @click="clearAll"
                    >
                        清空重来
                    </button>
                </div>

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
            <section v-if="candidates.length" class="mt-10">
                <div class="mb-5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-stone-500">
                    <span class="font-medium text-stone-700">共 {{ candidates.length }} 份简历</span>
                    <span v-for="group in groups" :key="group.key" class="inline-flex items-center gap-1.5">
                        <span class="h-1.5 w-1.5 rounded-full" :class="group.dot"></span>
                        {{ group.key }} {{ group.items.length }}
                    </span>
                </div>

                <div class="grid gap-6 lg:grid-cols-3">
                    <div v-for="group in groups" :key="group.key">
                        <div class="mb-1 flex items-center gap-2">
                            <span class="h-2 w-2 rounded-full" :class="group.dot"></span>
                            <h2 class="text-sm font-semibold text-stone-800">{{ group.key }}</h2>
                            <span class="ml-auto rounded-md border px-1.5 py-0.5 text-[11px] font-medium" :class="group.chip">
                                {{ group.items.length }}
                            </span>
                        </div>
                        <p class="mb-3 text-xs text-stone-400">{{ group.hint }}</p>

                        <div class="flex flex-col gap-3">
                            <article
                                v-for="item in group.items"
                                :key="item.resume_id"
                                class="rounded-lg border border-stone-200/80 bg-white p-3.5 shadow-sm"
                            >
                                <div class="flex items-start gap-3">
                                    <div class="relative h-11 w-11 shrink-0">
                                        <svg class="h-11 w-11 -rotate-90" viewBox="0 0 80 80">
                                            <circle cx="40" cy="40" r="34" fill="none" stroke="#ece9e4" stroke-width="7" />
                                            <circle
                                                cx="40" cy="40" r="34" fill="none"
                                                :stroke="group.ring" stroke-width="7" stroke-linecap="round"
                                                :stroke-dasharray="CIRCUMFERENCE" :stroke-dashoffset="dashOffsetOf(item.score)"
                                            />
                                        </svg>
                                        <div class="absolute inset-0 grid place-items-center">
                                            <span class="text-[11px] font-semibold leading-none" :class="group.text">
                                                {{ Math.round(item.score) }}
                                            </span>
                                        </div>
                                    </div>

                                    <div class="min-w-0 flex-1">
                                        <p class="truncate text-sm font-medium text-stone-800">{{ nameOf(item.resume_id) }}</p>
                                        <p class="mt-0.5 text-[11px] text-stone-400">ID {{ shortId(item.resume_id) }}</p>
                                    </div>
                                </div>

                                <button
                                    type="button"
                                    class="mt-3 inline-flex w-full items-center justify-center gap-1.5 rounded-md border border-stone-200 px-2 py-1.5 text-xs font-medium text-stone-600 transition hover:border-stone-300 hover:bg-stone-50 hover:text-stone-800"
                                    :aria-expanded="openId === item.resume_id"
                                    @click="toggleAsk(item)"
                                >
                                    <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z" />
                                    </svg>
                                    {{ openId === item.resume_id ? "收起" : "追问这位候选人" }}
                                </button>

                                <!-- 展开的追问线程 -->
                                <div v-if="openId === item.resume_id" class="mt-3 rounded-md border border-stone-200 bg-stone-50/70 p-2.5">
                                    <div v-if="item.chat.length" class="mb-2 space-y-2">
                                        <template v-for="(msg, i) in item.chat" :key="i">
                                            <div v-if="msg.role === 'user'" class="text-right">
                                                <span class="inline-block max-w-[90%] rounded-md bg-amber-100/80 px-2.5 py-1.5 text-left text-xs leading-relaxed text-stone-700">{{ msg.text }}</span>
                                            </div>
                                            <div v-else class="rounded-md border border-stone-200 bg-white px-2.5 py-2">
                                                <MarkdownText :source="msg.text" />
                                            </div>
                                        </template>
                                    </div>

                                    <div v-if="item.chatLoading" class="mb-2 flex items-center gap-1.5 rounded-md border border-stone-200 bg-white px-2.5 py-2">
                                        <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-300"></span>
                                        <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-300" style="animation-delay: 150ms"></span>
                                        <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-300" style="animation-delay: 300ms"></span>
                                    </div>

                                    <div class="flex items-end gap-2">
                                        <textarea
                                            v-model="item.chatInput"
                                            rows="1"
                                            placeholder="追问一句，比如「他做过哪些性能优化？」"
                                            class="field-sizing-content max-h-24 min-w-0 flex-1 resize-none rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs leading-relaxed text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100"
                                            @keydown="onAskKeydown($event, item)"
                                        ></textarea>
                                        <button
                                            type="button"
                                            class="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-amber-500 text-white transition hover:bg-amber-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300 disabled:cursor-not-allowed disabled:bg-stone-300"
                                            :disabled="item.chatLoading || !item.chatInput.trim()"
                                            aria-label="发送"
                                            @click="ask(item)"
                                        >
                                            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                                <path d="M12 19V5" />
                                                <path d="m5 12 7-7 7 7" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </article>

                            <p v-if="!group.items.length" class="rounded-lg border border-dashed border-stone-200 px-3 py-6 text-center text-xs text-stone-400">
                                这一档暂时没人
                            </p>
                        </div>
                    </div>
                </div>

                <!-- 没归进三档的兜底 -->
                <div v-if="unclassified.length" class="mt-6">
                    <h2 class="mb-3 text-sm font-semibold text-stone-800">未分类</h2>
                    <ul class="flex flex-wrap gap-2 text-xs text-stone-500">
                        <li v-for="item in unclassified" :key="item.resume_id" class="rounded-md border border-stone-200 bg-white px-2 py-1">
                            {{ nameOf(item.resume_id) }} · {{ item.score }} 分
                        </li>
                    </ul>
                </div>
            </section>

            <footer class="pt-10 text-center text-xs text-stone-400">
                筛选结果由大模型生成，建议结合实际情况判断。
            </footer>
        </div>
    </div>
</template>
