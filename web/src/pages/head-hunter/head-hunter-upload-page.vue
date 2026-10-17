<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import MarkdownText from "../../components/markdown-text.vue"
import { API_BASE, metaOf, normalizeJob, parseTags } from "../../utils/job"

// 解析出来的草稿，确认之后才批量入库
const drafts = ref([])
const parsing = ref(false)
const jobError = ref("")
const importedCount = ref(null)
const skippedContent = ref([])
const importing = ref(false)

// 正在编辑第几条，-1 表示没有在编辑
const editingIndex = ref(-1)
const editBuffer = ref(null)

// 正在看原文的那条，null 表示弹窗关着
const rawTextJob = ref(null)

function openRawText(job) {
    rawTextJob.value = job
}

function closeRawText() {
    rawTextJob.value = null
}

// Esc 关弹窗
function onEsc(event) {
    if (event.key === "Escape") closeRawText()
}

onMounted(() => document.addEventListener("keydown", onEsc))
onBeforeUnmount(() => document.removeEventListener("keydown", onEsc))

// 上传 JD 汇总文档，先解析成草稿，不直接入库
async function uploadJobs(e) {
    const file = e.target.files?.[0]
    if (!file) return

    jobError.value = ""
    importedCount.value = null
    editingIndex.value = -1
    parsing.value = true

    try {
        const form = new FormData()
        form.append("file", file)

        // 约定的接口：POST /head-hunter/jobs，FormData(file) -> { jobs: [...] }，只解析不入库
        const res = await fetch(`${API_BASE}/head-hunter/jobs`, {
            method: 'POST',
            body: form
        })

        if (!res.ok) throw new Error("解析失败：" + res.status)

        const data = await res.json()
        drafts.value = (data.jobs ?? []).map(normalizeJob)
    } catch (err) {
        jobError.value = err.message
    } finally {
        parsing.value = false
        // 清空 input 的值，否则再选同一个文件不会触发 change
        e.target.value = ""
    }
}

// 单条编辑：改的是副本，取消就丢掉
function startEdit(index) {
    const job = drafts.value[index]
    editingIndex.value = index
    editBuffer.value = {
        title: job.title,
        edu: job.edu,
        location: job.location,
        salary: job.salary,
        tagsText: job.tags.join("、"),
        requirements: job.requirements,
    }
}

function cancelEdit() {
    editingIndex.value = -1
    editBuffer.value = null
}

function saveEdit() {
    const index = editingIndex.value
    if (index < 0 || !editBuffer.value) return

    drafts.value[index] = {
        ...drafts.value[index],
        title: editBuffer.value.title.trim() || "未命名岗位",
        edu: editBuffer.value.edu.trim(),
        location: editBuffer.value.location.trim(),
        salary: editBuffer.value.salary.trim(),
        tags: parseTags(editBuffer.value.tagsText),
        requirements: editBuffer.value.requirements.trim(),
    }

    cancelEdit()
}

// 批量入库，成功后清空草稿
async function importDrafts() {
    if (!drafts.value.length || importing.value) return

    importing.value = true
    jobError.value = ""

    try {
        // 约定的接口：POST /head-hunter/jobs-import，{ jobs: [...] } -> { imported: n }
        const res = await fetch(`${API_BASE}/head-hunter/jobs-import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jobs: drafts.value.map(({ id, ...job }) => job),
            })
        })

        if (!res.ok) throw new Error("入库失败：" + res.status)

        const data = await res.json()
        drafts.value = []

        importedCount.value = Number(data.imported) || drafts.value.length
        skippedContent.value = data.skipped
        cancelEdit()
    } catch (err) {
        jobError.value = err.message
    } finally {
        importing.value = false
    }
}
</script>

<template>
    <div class="page-shell overflow-y-auto bg-[#f7f6f3] text-stone-800 antialiased">
        <div class="mx-auto w-full max-w-5xl px-5 py-8 sm:px-8">

            <router-link to="/head-hunter"
                class="inline-flex items-center gap-1.5 text-sm text-stone-500 transition hover:text-stone-800">
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                    stroke-linecap="round" stroke-linejoin="round">
                    <path d="m12 19-7-7 7-7" />
                    <path d="M19 12H5" />
                </svg>
                返回猎头工作台
            </router-link>

            <header class="mt-4 mb-6">
                <h1 class="text-xl font-semibold tracking-tight text-stone-900">岗位上传</h1>
                <p class="mt-1 text-sm leading-relaxed text-stone-500">
                    上传 JD 汇总文档，大模型会解析成结构化岗位。逐条确认或修改之后，再批量入库。
                </p>
            </header>

            <section class="rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
                <div v-if="parsing" class="flex items-center gap-2 text-xs text-stone-500">
                    <svg class="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2" stroke-linecap="round">
                        <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                    </svg>
                    正在解析文档…
                </div>

                <div v-else-if="jobError"
                    class="mb-3 flex items-start gap-2 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-600">
                    <svg class="mt-0.5 h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" x2="12" y1="8" y2="12" />
                        <line x1="12" x2="12.01" y1="16" y2="16" />
                    </svg>
                    <span>{{ jobError }}</span>
                </div>

                <div v-else-if="importedCount !== null"
                    class="mb-3 flex items-center gap-2 rounded-md border border-emerald-100 bg-emerald-50/70 px-3 py-2 text-xs text-emerald-800">
                    <svg class="h-3.5 w-3.5 shrink-0 text-emerald-600" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21.801 10A10 10 0 1 1 17 3.335" />
                        <path d="m9 11 3 3L22 4" />
                    </svg>
                    <span>已入库 {{ importedCount }} 个岗位，可以去「岗位列表」看看</span>
                </div>

                <!-- 还没解析出结果时：上传入口 -->
                <label v-if="!drafts.length && !parsing"
                    class="group flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-stone-300 bg-stone-50/60 px-4 py-14 text-center transition hover:border-amber-400 hover:bg-amber-50/60 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-amber-300">
                    <input type="file" accept=".md" class="sr-only" @change="uploadJobs">
                    <svg class="h-6 w-6 text-stone-400 transition group-hover:text-amber-500" viewBox="0 0 24 24"
                        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" x2="12" y1="3" y2="15" />
                    </svg>
                    <span class="text-sm font-medium text-stone-600 transition group-hover:text-amber-700">上传 JD
                        汇总文档</span>
                    <span class="text-xs text-stone-400">支持 .md，一份文档里可以放多个岗位</span>
                </label>

                <!-- 解析结果：逐条确认或修改，最后批量入库 -->
                <div v-if="drafts.length">
                    <div class="mb-3 flex flex-wrap items-center gap-2">
                        <h2 class="text-sm font-semibold text-stone-800">解析结果</h2>
                        <span class="text-xs text-stone-400">共 {{ drafts.length }} 个岗位，可以逐条修改</span>
                    </div>

                    <ul class="divide-y divide-stone-100 rounded-lg border border-stone-200/80">
                        <li v-for="(job, index) in drafts" :key="job.id" class="px-3.5 py-3">
                            <!-- 只读 -->
                            <div v-if="editingIndex !== index" class="flex items-start gap-3">
                                <span class="mt-0.5 shrink-0 text-[11px] text-stone-400">{{ index + 1 }}</span>

                                <div class="min-w-0 flex-1">
                                    <p class="text-sm font-medium text-stone-800">{{ job.title }}</p>
                                    <p v-if="metaOf(job)" class="mt-0.5 text-xs text-stone-500">{{ metaOf(job) }}</p>

                                    <div v-if="job.tags.length" class="mt-1.5 flex flex-wrap gap-1.5">
                                        <span v-for="tag in job.tags" :key="tag"
                                            class="rounded-md border border-stone-200 bg-stone-50 px-1.5 py-0.5 text-[11px] text-stone-600">
                                            {{ tag }}
                                        </span>
                                    </div>

                                    <p v-if="job.requirements"
                                        class="mt-1.5 line-clamp-2 text-xs leading-relaxed text-stone-500">
                                        {{ job.requirements }}
                                    </p>
                                </div>

                                <div class="flex shrink-0 items-center gap-1.5">
                                    <button type="button"
                                        class="cursor-pointer rounded-md border border-stone-200 px-2 py-1 text-xs text-stone-500 transition hover:bg-stone-50 hover:text-stone-800"
                                        @click="openRawText(job)">
                                        显示原文
                                    </button>

                                    <button type="button"
                                        class="cursor-pointer rounded-md border border-stone-200 px-2 py-1 text-xs text-stone-500 transition hover:bg-stone-50 hover:text-stone-800"
                                        @click="startEdit(index)">
                                        编辑
                                    </button>
                                </div>
                            </div>

                            <!-- 编辑中 -->
                            <div v-else class="grid gap-2">
                                <input v-model="editBuffer.title" placeholder="岗位名称"
                                    class="w-full rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100">

                                <div class="grid gap-2 sm:grid-cols-3">
                                    <input v-model="editBuffer.edu" placeholder="学历"
                                        class="w-full rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100">
                                    <input v-model="editBuffer.location" placeholder="城市"
                                        class="w-full rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100">
                                    <input v-model="editBuffer.salary" placeholder="薪资"
                                        class="w-full rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100">
                                </div>

                                <input v-model="editBuffer.tagsText" placeholder="标签，用、分隔"
                                    class="w-full rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100">

                                <textarea v-model="editBuffer.requirements" rows="2" placeholder="任职要求"
                                    class="w-full resize-none rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs leading-relaxed text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100"></textarea>

                                <div class="flex justify-end gap-2">
                                    <button type="button"
                                        class="cursor-pointer rounded-md px-2.5 py-1.5 text-xs text-stone-500 transition hover:bg-stone-100 hover:text-stone-800"
                                        @click="cancelEdit">
                                        取消
                                    </button>
                                    <button type="button"
                                        class="cursor-pointer rounded-md bg-amber-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-amber-600"
                                        @click="saveEdit">
                                        保存
                                    </button>
                                </div>
                            </div>
                        </li>
                    </ul>

                    <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
                        <label
                            class="inline-flex cursor-pointer items-center gap-1.5 rounded-md px-2 py-1.5 text-xs text-stone-500 transition hover:bg-stone-100 hover:text-stone-800 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-amber-300">
                            <input type="file" accept=".md" class="sr-only" @change="uploadJobs">
                            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                                <polyline points="17 8 12 3 7 8" />
                                <line x1="12" x2="12" y1="3" y2="15" />
                            </svg>
                            换一份文档
                        </label>

                        <button type="button"
                            class="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-amber-500 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-amber-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300 disabled:cursor-not-allowed disabled:bg-stone-300"
                            :disabled="importing" @click="importDrafts">
                            <svg v-if="importing" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2" stroke-linecap="round">
                                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                            </svg>
                            <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21.801 10A10 10 0 1 1 17 3.335" />
                                <path d="m9 11 3 3L22 4" />
                            </svg>
                            {{ importing ? "入库中…" : `批量入库（${drafts.length}）` }}
                        </button>
                    </div>
                </div>
            </section>

            <!-- 原文弹窗：按 Markdown 渲染 raw_text -->
            <Transition name="fade">
                <div v-if="rawTextJob" class="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/25 p-5"
                    @click="closeRawText">
                    <div class="flex max-h-[80vh] w-full max-w-2xl flex-col rounded-lg border border-stone-200 bg-white shadow-xl"
                        role="dialog" aria-modal="true" aria-label="岗位原文" @click.stop>
                        <header class="flex shrink-0 items-center gap-3 border-b border-stone-100 px-5 py-4">
                            <div class="min-w-0 flex-1">
                                <h2 class="truncate text-sm font-semibold text-stone-800">{{ rawTextJob.title }}</h2>
                            </div>

                            <button type="button"
                                class="grid h-8 w-8 shrink-0 cursor-pointer place-items-center rounded-md text-stone-400 transition hover:bg-stone-100 hover:text-stone-700"
                                aria-label="关闭" @click="closeRawText">
                                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M18 6 6 18" />
                                    <path d="m6 6 12 12" />
                                </svg>
                            </button>
                        </header>

                        <div class="min-h-0 flex-1 overflow-y-auto overscroll-contain px-5 py-4">
                            <MarkdownText v-if="rawTextJob.raw_text" :source="rawTextJob.raw_text" />
                            <p v-else class="py-10 text-center text-xs text-stone-400">这条解析结果没有附带原文</p>
                        </div>
                    </div>
                </div>
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
</style>
