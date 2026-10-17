<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue"
import MarkdownText from "../../components/markdown-text.vue"
import { API_BASE, metaOf, toneOf } from "../../utils/job"

const resumeFile = ref(null)
const matching = ref(false)
const matchStage = ref("")
const matches = ref([])
const matchError = ref("")

// 当前选中的卡片（选中后显示追问入口）
const selectedKey = ref("")

// 详情弹窗
const detailItem = ref(null)

// 追问抽屉
const askItem = ref(null)
const askThreads = ref({})
const askInput = ref("")
const askLoading = ref(false)
const askList = ref(null)
const askInputEl = ref(null)

// 按分数从高到低；岗位对象由后端随结果带回来，
// 因为岗位列表是分页的，前端拿不到全部岗位去回查
const matchedJobs = computed(() =>
    matches.value
        .map((item) => ({
            ...item,
            score: Number(item.score) || 0,
            job: item.job ?? null,
        }))
        .sort((a, b) => b.score - a.score)
)

function keyOf(item) {
    return item.job_id ?? item.job?.id ?? item.id ?? ""
}

function toggleSelect(item) {
    selectedKey.value = selectedKey.value === keyOf(item) ? "" : keyOf(item)
}

function openDetail(item) {
    detailItem.value = item
}

function closeDetail() {
    detailItem.value = null
}

const currentThread = computed(() =>
    askItem.value ? (askThreads.value[keyOf(askItem.value)] || []) : []
)

async function openAsk(item) {
    askItem.value = item
    askInput.value = ""

    const key = keyOf(item)
    if (!askThreads.value[key]) askThreads.value[key] = []

    await nextTick()
    askInputEl.value?.focus()
    askList.value?.scrollTo({ top: askList.value.scrollHeight })
}

function closeAsk() {
    askItem.value = null
}

async function scrollAskToBottom() {
    await nextTick()
    askList.value?.scrollTo({ top: askList.value.scrollHeight, behavior: "smooth" })
}

// 只做前端：先把用户这句话放进对话，接口接上后在这里发请求并追加回复
function sendAsk() {
    if (!askItem.value || askLoading.value) return

    const text = askInput.value.trim()
    if (!text) return

    const key = keyOf(askItem.value)
    if (!askThreads.value[key]) askThreads.value[key] = []

    askThreads.value[key].push({ role: "user", text })
    askInput.value = ""
    scrollAskToBottom()

    // TODO：后端接上后，在这里把 text 发出去，拿到回复再 push 一条 assistant 消息
    // askLoading 用来在等待期间显示“正在思考…”
}

// 回车发送、Shift + Enter 换行；输入法选词那一下回车不算发送
function onAskKeydown(event) {
    if (event.key !== "Enter" || event.shiftKey) return
    if (event.isComposing || event.keyCode === 229) return

    event.preventDefault()
    sendAsk()
}

// Esc 关详情弹窗和追问抽屉
function onEsc(event) {
    if (event.key !== "Escape") return
    closeDetail()
    closeAsk()
}

watch(askItem, (value) => {
    document.body.style.overflow = value ? "hidden" : ""
})

onMounted(() => document.addEventListener("keydown", onEsc))
onBeforeUnmount(() => {
    document.removeEventListener("keydown", onEsc)
    document.body.style.overflow = ""
})

// 上传简历（复用已有的 /upload_resume），再拿 resume_id 去岗位库比对
async function uploadResume(e) {
    const file = e.target.files?.[0]
    if (!file) return

    matchError.value = ""
    matching.value = true
    matchStage.value = "正在解析简历…"
    matches.value = []
    selectedKey.value = ""
    resumeFile.value = file

    try {
        const form = new FormData()
        form.append("file", file)

        const uploadRes = await fetch(`${API_BASE}/upload_resume`, {
            method: 'POST',
            body: form
        })

        if (!uploadRes.ok) throw new Error("简历上传失败：" + uploadRes.status)

        const uploadData = await uploadRes.json()

        matchStage.value = "正在比对岗位列表…"

        // 约定的接口：POST /head-hunter/match，{ resume_id } -> { matches: [{ job, score }] }
        const res = await fetch(`${API_BASE}/head-hunter/match`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume_id: uploadData.resume_id })
        })

        if (!res.ok) throw new Error("比对失败：" + res.status)

        const data = await res.json()
        matches.value = data.matches ?? []
    } catch (err) {
        matchError.value = err.message
    } finally {
        matching.value = false
        matchStage.value = ""
        e.target.value = ""
    }
}
</script>

<template>
    <div class="page-shell overflow-y-auto bg-[#f7f6f3] text-stone-800 antialiased">
        <div class="mx-auto w-full max-w-5xl px-5 py-8 sm:px-8">

            <router-link to="/head-hunter" class="inline-flex items-center gap-1.5 text-sm text-stone-500 transition hover:text-stone-800">
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m12 19-7-7 7-7" />
                    <path d="M19 12H5" />
                </svg>
                返回猎头工作台
            </router-link>

            <header class="mt-4 mb-6">
                <h1 class="text-xl font-semibold tracking-tight text-stone-900">候选人匹配</h1>
                <p class="mt-1 text-sm leading-relaxed text-stone-500">
                    上传一份候选人简历，系统会拿它去撞岗位列表，列出适合推的岗位和匹配分数。
                </p>
            </header>

            <section class="rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
                <div class="grid gap-5 lg:grid-cols-[minmax(0,300px)_minmax(0,1fr)]">

                    <!-- 左：上传简历 -->
                    <div>
                        <label class="group flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-stone-300 bg-stone-50/60 px-4 py-8 text-center transition hover:border-amber-400 hover:bg-amber-50/60 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-amber-300">
                            <input type="file" accept=".pdf" class="sr-only" @change="uploadResume">
                            <svg class="h-5 w-5 text-stone-400 transition group-hover:text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                                <circle cx="12" cy="7" r="4" />
                            </svg>
                            <span class="text-sm font-medium text-stone-600 transition group-hover:text-amber-700">
                                {{ resumeFile ? "换一份简历" : "上传候选人简历" }}
                            </span>
                            <span class="text-xs text-stone-400">PDF 格式，上传后自动比对</span>
                        </label>

                        <div v-if="resumeFile" class="mt-3 flex items-center gap-2 rounded-md border border-emerald-100 bg-emerald-50/70 px-2.5 py-1.5">
                            <svg class="h-3.5 w-3.5 shrink-0 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
                                <path d="M14 2v4a2 2 0 0 0 2 2h4" />
                            </svg>
                            <span class="truncate text-xs text-emerald-800">{{ resumeFile.name }}</span>
                        </div>

                        <div v-if="matching" class="mt-3 flex items-center gap-2 text-xs text-stone-500">
                            <svg class="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                            </svg>
                            {{ matchStage }}
                        </div>

                        <div v-else-if="matchError" class="mt-3 flex items-start gap-2 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-600">
                            <svg class="mt-0.5 h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="12" x2="12" y1="8" y2="12" />
                                <line x1="12" x2="12.01" y1="16" y2="16" />
                            </svg>
                            <span>{{ matchError }}</span>
                        </div>
                    </div>

                    <!-- 右：适合的岗位 -->
                    <div class="lg:border-l lg:border-stone-100 lg:pl-5">
                        <div v-if="matchedJobs.length" class="mb-3 flex items-center gap-2">
                            <h2 class="text-sm font-semibold text-stone-800">适合的岗位</h2>
                            <span class="text-xs text-stone-400">命中 {{ matchedJobs.length }} 个</span>
                        </div>

                        <div v-if="matchedJobs.length" class="grid gap-2.5 sm:grid-cols-2">
                            <article
                                v-for="item in matchedJobs"
                                :key="keyOf(item)"
                                tabindex="0"
                                class="cursor-pointer rounded-lg border bg-stone-50/60 px-3.5 py-3 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300"
                                :class="selectedKey === keyOf(item)
                                    ? 'border-amber-300 ring-1 ring-amber-200'
                                    : 'border-stone-200/80 hover:border-stone-300'"
                                :title="metaOf(item.job)"
                                @click="toggleSelect(item)"
                                @keydown.enter.prevent="toggleSelect(item)"
                                @keydown.space.prevent="toggleSelect(item)"
                            >
                                <div class="flex items-start justify-between gap-2">
                                    <p class="text-xs leading-none text-stone-500">
                                        匹配分数：<span class="text-sm font-semibold" :class="toneOf(item.score)">{{ Math.round(item.score) }}</span>
                                    </p>

                                    <button
                                        type="button"
                                        class="shrink-0 cursor-pointer rounded-md border border-stone-200 bg-white px-2 py-1 text-[11px] text-stone-500 transition hover:bg-stone-50 hover:text-stone-800"
                                        @click.stop="openDetail(item)"
                                    >
                                        显示详情
                                    </button>
                                </div>

                                <p class="mt-2 text-sm font-medium leading-relaxed text-stone-800">
                                    {{ item.job?.title ?? "岗位列表里没找到这个 id" }}
                                </p>

                                <p class="mt-1.5 text-[11px] leading-relaxed text-stone-500">
                                    <span class="text-stone-400">评分依据：</span>{{ item.reason || "未给出说明" }}
                                </p>

                                <!-- 选中后才出现的追问入口 -->
                                <div v-if="selectedKey === keyOf(item)" class="mt-2.5 border-t border-stone-200/70 pt-2.5">
                                    <button
                                        type="button"
                                        class="inline-flex cursor-pointer items-center gap-1.5 rounded-md bg-amber-500 px-2.5 py-1 text-[11px] font-medium text-white transition hover:bg-amber-600"
                                        @click.stop="openAsk(item)"
                                    >
                                        <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z" />
                                        </svg>
                                        追问这个岗位
                                    </button>
                                </div>
                            </article>
                        </div>

                        <p v-else class="flex h-full min-h-44 items-center justify-center rounded-lg border border-dashed border-stone-200 px-4 text-center text-xs leading-relaxed text-stone-400">
                            上传一份候选人简历<br />这里会列出他适合的岗位
                        </p>
                    </div>
                </div>
            </section>

            <!-- 详情弹窗：渲染这条岗位的 raw_text -->
            <Transition name="fade">
                <div v-if="detailItem" class="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/25 p-5" @click="closeDetail">
                    <div
                        class="flex max-h-[80vh] w-full max-w-2xl flex-col rounded-lg border border-stone-200 bg-white shadow-xl"
                        role="dialog"
                        aria-modal="true"
                        aria-label="岗位详情"
                        @click.stop
                    >
                        <header class="flex shrink-0 items-center gap-3 border-b border-stone-100 px-5 py-4">
                            <div class="min-w-0 flex-1">
                                <p class="text-xs text-stone-400">岗位详情</p>
                                <h2 class="truncate text-sm font-semibold text-stone-800">
                                    {{ detailItem.job?.title ?? "岗位" }}
                                </h2>
                            </div>

                            <button
                                type="button"
                                class="grid h-8 w-8 shrink-0 cursor-pointer place-items-center rounded-md text-stone-400 transition hover:bg-stone-100 hover:text-stone-700"
                                aria-label="关闭"
                                @click="closeDetail"
                            >
                                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M18 6 6 18" />
                                    <path d="m6 6 12 12" />
                                </svg>
                            </button>
                        </header>

                        <div class="min-h-0 flex-1 overflow-y-auto overscroll-contain px-5 py-4">
                            <MarkdownText v-if="detailItem.job?.raw_text" :source="detailItem.job.raw_text" />
                            <p v-else class="py-10 text-center text-xs text-stone-400">这个岗位没有保存原文</p>
                        </div>
                    </div>
                </div>
            </Transition>

            <!-- 追问抽屉：从右侧滑出 -->
            <Transition name="fade">
                <div v-if="askItem" class="fixed inset-0 z-40 bg-stone-900/20" @click="closeAsk"></div>
            </Transition>

            <Transition name="slide">
                <aside
                    v-if="askItem"
                    class="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col border-l border-stone-200 bg-[#f7f6f3] shadow-2xl"
                    role="dialog"
                    aria-modal="true"
                    aria-label="岗位追问"
                >
                    <!-- 顶部：岗位信息 -->
                    <header class="flex shrink-0 items-start gap-3 border-b border-stone-200/70 px-5 py-4">
                        <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-amber-50 text-sm font-semibold" :class="toneOf(askItem.score)">
                            {{ Math.round(askItem.score) }}
                        </span>

                        <div class="min-w-0 flex-1">
                            <p class="truncate text-sm font-medium text-stone-800">{{ askItem.job?.title ?? "岗位" }}</p>
                            <p v-if="metaOf(askItem.job)" class="mt-0.5 truncate text-[11px] text-stone-400">{{ metaOf(askItem.job) }}</p>
                        </div>

                        <button
                            type="button"
                            class="grid h-8 w-8 shrink-0 cursor-pointer place-items-center rounded-md text-stone-400 transition hover:bg-stone-200/60 hover:text-stone-700"
                            aria-label="关闭追问"
                            @click="closeAsk"
                        >
                            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M18 6 6 18" />
                                <path d="m6 6 12 12" />
                            </svg>
                        </button>
                    </header>

                    <!-- 中间：对话内容，自己滚 -->
                    <div ref="askList" class="min-h-0 flex-1 space-y-3 overflow-y-auto px-5 py-4">
                        <p v-if="!currentThread.length && !askLoading" class="pt-12 text-center text-xs leading-relaxed text-stone-400">
                            还没有追问记录<br />可以问这个候选人和岗位的匹配细节
                        </p>

                        <template v-for="(msg, i) in currentThread" :key="i">
                            <div v-if="msg.role === 'user'" class="flex justify-end">
                                <span class="max-w-[85%] rounded-lg border border-amber-200/70 bg-amber-100/70 px-3 py-2 text-sm leading-relaxed text-stone-800">{{ msg.text }}</span>
                            </div>
                            <div v-else class="flex justify-start">
                                <div class="max-w-[92%] rounded-lg border border-stone-200 bg-white px-3.5 py-2.5 shadow-sm">
                                    <MarkdownText :source="msg.text" />
                                </div>
                            </div>
                        </template>

                        <div v-if="askLoading" class="flex justify-start">
                            <div class="flex items-center gap-1.5 rounded-lg border border-stone-200 bg-white px-4 py-3 shadow-sm">
                                <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-300"></span>
                                <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-300" style="animation-delay: 150ms"></span>
                                <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-300" style="animation-delay: 300ms"></span>
                            </div>
                        </div>
                    </div>

                    <!-- 底部：输入框 -->
                    <footer class="shrink-0 border-t border-stone-200/70 px-5 py-4">
                        <div class="flex items-end gap-2 rounded-lg border border-stone-200 bg-white p-2 shadow-sm transition focus-within:border-amber-400 focus-within:ring-2 focus-within:ring-amber-100">
                            <textarea
                                ref="askInputEl"
                                v-model="askInput"
                                rows="1"
                                placeholder="追问一句…"
                                class="field-sizing-content max-h-32 min-w-0 flex-1 resize-none bg-transparent px-1.5 py-1.5 text-sm leading-relaxed text-stone-800 placeholder:text-stone-400 focus:outline-none"
                                @keydown="onAskKeydown"
                            ></textarea>
                            <button
                                type="button"
                                class="grid h-8 w-8 shrink-0 cursor-pointer place-items-center rounded-full bg-amber-500 text-white transition hover:bg-amber-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300 disabled:cursor-not-allowed disabled:bg-stone-300"
                                :disabled="askLoading || !askInput.trim()"
                                aria-label="发送"
                                @click="sendAsk"
                            >
                                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M12 19V5" />
                                    <path d="m5 12 7-7 7 7" />
                                </svg>
                            </button>
                        </div>
                    </footer>
                </aside>
            </Transition>
        </div>
    </div>
</template>

<style scoped>
/* 77px 是顶部粘性表头的高度：内容区占满剩下的一屏并自己滚 */
.page-shell {
    height: calc(100vh - 77px);
    height: calc(100dvh - 77px);
}

/* 弹窗淡入淡出 */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 160ms ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

/* 追问抽屉从右侧滑入 */
.slide-enter-active,
.slide-leave-active {
    transition: transform 240ms ease;
}

.slide-enter-from,
.slide-leave-to {
    transform: translateX(100%);
}
</style>
