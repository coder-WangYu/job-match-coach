<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import MarkdownText from "../../components/markdown-text.vue"
import JobEditFields from "../../components/job-edit-fields.vue"
import { API_BASE, metaOf, normalizeJob, parseTags } from "../../utils/job"

const jobs = ref([])
const jobTotal = ref(0)
const jobPage = ref(1)
const jobPageSize = ref(10)
const jobsLoading = ref(false)
const jobsError = ref("")
const actionError = ref("")

// 查询条件：关键词匹配岗位名称 / 任职要求 / 原文，城市单独模糊匹配
const keyword = ref("")
const location = ref("")

// 详情弹窗
const detailJob = ref(null)

// 行内编辑
const editingId = ref("")
const editBuffer = ref(null)
const savingId = ref("")

// 删除确认
const deletingJob = ref(null)
const deleteLoading = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(jobTotal.value / jobPageSize.value)))
const hasFilter = computed(() => Boolean(keyword.value.trim() || location.value.trim()))

function queryString(page) {
    const params = new URLSearchParams({
        page: String(page),
        page_size: String(jobPageSize.value),
    })

    if (keyword.value.trim()) params.set("keyword", keyword.value.trim())
    if (location.value.trim()) params.set("location", location.value.trim())

    return params.toString()
}

// 分页拉岗位列表
async function loadJobs(page = jobPage.value) {
    jobsLoading.value = true
    jobsError.value = ""
    actionError.value = ""

    try {
        const res = await fetch(`${API_BASE}/head-hunter/get-jobs?${queryString(page)}`)

        if (!res.ok) throw new Error("岗位列表加载失败：" + res.status)

        const data = await res.json()
        jobs.value = (data.jobs ?? []).map(normalizeJob)
        jobTotal.value = Number(data.total) || jobs.value.length
        jobPage.value = page
        cancelEdit()
    } catch (err) {
        jobsError.value = err.message
    } finally {
        jobsLoading.value = false
    }
}

function search() {
    loadJobs(1)
}

function resetSearch() {
    keyword.value = ""
    location.value = ""
    loadJobs(1)
}

// 详情：直接渲染这条岗位的原文
function openDetail(job) {
    detailJob.value = job
}

function closeDetail() {
    detailJob.value = null
}

// 行内编辑
function startEdit(job) {
    editingId.value = job.id
    editBuffer.value = {
        title: job.title || "",
        edu: job.edu || "",
        location: job.location || "",
        salary: job.salary || "",
        tagsText: Array.isArray(job.tags) ? job.tags.join("、") : "",
        requirements: job.requirements || "",
    }
}

function cancelEdit() {
    editingId.value = ""
    editBuffer.value = null
}

async function saveEdit(job) {
    if (!editBuffer.value || savingId.value) return

    savingId.value = job.id
    actionError.value = ""

    try {
        const res = await fetch(`${API_BASE}/head-hunter/jobs/${job.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...job,
                title: editBuffer.value.title.trim() || "未命名岗位",
                edu: editBuffer.value.edu.trim(),
                location: editBuffer.value.location.trim(),
                salary: editBuffer.value.salary.trim(),
                tags: parseTags(editBuffer.value.tagsText),
                requirements: editBuffer.value.requirements.trim(),
            })
        })

        if (!res.ok) throw new Error("保存失败：" + res.status)

        await loadJobs(jobPage.value)
    } catch (err) {
        actionError.value = err.message
    } finally {
        savingId.value = ""
    }
}

// 删除
function askDelete(job) {
    deletingJob.value = job
}

function cancelDelete() {
    deletingJob.value = null
}

async function confirmDelete() {
    if (!deletingJob.value || deleteLoading.value) return

    const job = deletingJob.value
    deleteLoading.value = true
    actionError.value = ""

    try {
        const res = await fetch(`${API_BASE}/head-hunter/jobs/${job.id}`, { method: 'DELETE' })

        if (!res.ok) throw new Error("删除失败：" + res.status)

        deletingJob.value = null

        // 删完当前页空了就往前退一页
        const nextPage = jobs.value.length === 1 && jobPage.value > 1 ? jobPage.value - 1 : jobPage.value
        await loadJobs(nextPage)
    } catch (err) {
        actionError.value = err.message
    } finally {
        deleteLoading.value = false
    }
}

// Esc 关弹窗
function onEsc(event) {
    if (event.key !== "Escape") return
    closeDetail()
    cancelDelete()
}

onMounted(() => {
    document.addEventListener("keydown", onEsc)
    loadJobs(1)
})

onBeforeUnmount(() => document.removeEventListener("keydown", onEsc))
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

            <header class="mt-4 mb-6 flex flex-wrap items-end gap-3">
                <div>
                    <h1 class="text-xl font-semibold tracking-tight text-stone-900">岗位列表</h1>
                    <p class="mt-1 text-sm leading-relaxed text-stone-500">
                        已经入库的全部岗位，可以按岗位名称、技能关键词或城市查询。
                    </p>
                </div>
                <span class="ml-auto text-xs text-stone-400">共 {{ jobTotal }} 个岗位</span>
                <button
                    type="button"
                    class="cursor-pointer rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-600 transition hover:bg-stone-50"
                    @click="loadJobs(jobPage)"
                >
                    刷新
                </button>
            </header>

            <!-- 查询 -->
            <form class="mb-4 flex flex-wrap gap-2" @submit.prevent="search">
                <div class="relative min-w-0 flex-1">
                    <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="11" cy="11" r="8" />
                        <path d="m21 21-4.3-4.3" />
                    </svg>
                    <input
                        v-model="keyword"
                        type="search"
                        placeholder="岗位名称 / 技能关键词"
                        class="w-full rounded-lg border border-stone-200 bg-white py-2 pl-9 pr-3 text-sm text-stone-800 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100"
                    >
                </div>

                <div class="relative w-32 shrink-0">
                    <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0" />
                        <circle cx="12" cy="10" r="3" />
                    </svg>
                    <input
                        v-model="location"
                        type="text"
                        placeholder="城市"
                        class="w-full rounded-lg border border-stone-200 bg-white py-2 pl-9 pr-3 text-sm text-stone-800 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100"
                    >
                </div>

                <button
                    type="submit"
                    class="inline-flex cursor-pointer items-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-amber-600"
                >
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="11" cy="11" r="8" />
                        <path d="m21 21-4.3-4.3" />
                    </svg>
                    查询
                </button>

                <button
                    v-if="hasFilter"
                    type="button"
                    class="cursor-pointer rounded-lg px-3 py-2 text-sm text-stone-500 transition hover:bg-white hover:text-stone-800"
                    @click="resetSearch"
                >
                    清除
                </button>
            </form>

            <div v-if="actionError" class="mb-3 flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-600">
                <svg class="mt-0.5 h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" x2="12" y1="8" y2="12" />
                    <line x1="12" x2="12.01" y1="16" y2="16" />
                </svg>
                <span>{{ actionError }}</span>
            </div>

            <section class="rounded-lg border border-stone-200/80 bg-white shadow-sm">
                <div v-if="jobsLoading" class="flex items-center justify-center gap-2 px-5 py-16 text-xs text-stone-400">
                    <svg class="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                        <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                    </svg>
                    正在加载…
                </div>

                <div v-else-if="jobsError" class="px-5 py-6">
                    <div class="flex items-start gap-2 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-600">
                        <svg class="mt-0.5 h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="12" x2="12" y1="8" y2="12" />
                            <line x1="12" x2="12.01" y1="16" y2="16" />
                        </svg>
                        <span>{{ jobsError }}</span>
                    </div>
                    <button
                        type="button"
                        class="mt-3 cursor-pointer rounded-md border border-stone-200 px-2.5 py-1.5 text-xs text-stone-600 transition hover:bg-stone-50"
                        @click="loadJobs(jobPage)"
                    >
                        重试
                    </button>
                </div>

                <ul v-else-if="jobs.length" class="divide-y divide-stone-100">
                    <li v-for="job in jobs" :key="job.id" class="px-5 py-3.5 transition hover:bg-stone-50">
                        <!-- 只读 -->
                        <div v-if="editingId !== job.id" class="flex flex-col gap-2 sm:flex-row sm:items-start">
                            <div class="min-w-0 flex-1">
                                <p class="text-sm font-medium text-stone-800">{{ job.title }}</p>
                                <p v-if="metaOf(job)" class="mt-0.5 text-xs text-stone-500">{{ metaOf(job) }}</p>

                                <div v-if="job.tags.length" class="mt-1.5 flex flex-wrap gap-1.5">
                                    <span
                                        v-for="tag in job.tags"
                                        :key="tag"
                                        class="rounded-md border border-stone-200 bg-stone-50 px-1.5 py-0.5 text-[11px] text-stone-600"
                                    >
                                        {{ tag }}
                                    </span>
                                </div>

                                <p v-if="job.requirements" class="mt-1.5 line-clamp-2 text-xs leading-relaxed text-stone-500">
                                    {{ job.requirements }}
                                </p>
                            </div>

                            <div class="flex shrink-0 flex-wrap items-center gap-1.5">
                                <button
                                    type="button"
                                    class="cursor-pointer rounded-md border border-stone-200 bg-white px-2 py-1 text-xs text-stone-500 transition hover:bg-stone-50 hover:text-stone-800"
                                    @click="openDetail(job)"
                                >
                                    显示详情
                                </button>
                                <button
                                    type="button"
                                    class="cursor-pointer rounded-md border border-stone-200 bg-white px-2 py-1 text-xs text-stone-500 transition hover:bg-stone-50 hover:text-stone-800"
                                    @click="startEdit(job)"
                                >
                                    编辑
                                </button>
                                <button
                                    type="button"
                                    class="cursor-pointer rounded-md px-2 py-1 text-xs text-rose-500 transition hover:bg-rose-50 hover:text-rose-600"
                                    @click="askDelete(job)"
                                >
                                    删除
                                </button>
                            </div>
                        </div>

                        <!-- 编辑中 -->
                        <div v-else class="grid gap-2">
                            <JobEditFields v-model="editBuffer" />

                            <div class="flex justify-end gap-2">
                                <button
                                    type="button"
                                    class="cursor-pointer rounded-md px-2.5 py-1.5 text-xs text-stone-500 transition hover:bg-stone-100 hover:text-stone-800 disabled:cursor-not-allowed disabled:opacity-40"
                                    :disabled="savingId === job.id"
                                    @click="cancelEdit"
                                >
                                    取消
                                </button>
                                <button
                                    type="button"
                                    class="cursor-pointer rounded-md bg-amber-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-60"
                                    :disabled="savingId === job.id"
                                    @click="saveEdit(job)"
                                >
                                    {{ savingId === job.id ? "保存中…" : "保存" }}
                                </button>
                            </div>
                        </div>
                    </li>
                </ul>

                <p v-else class="px-5 py-16 text-center text-xs text-stone-400">
                    {{ hasFilter ? "没有找到匹配的岗位，换个关键词试试" : "岗位列表还是空的，先去「岗位上传」传一份 JD 汇总文档" }}
                </p>

                <div v-if="jobs.length && !jobsError" class="flex flex-wrap items-center justify-between gap-3 border-t border-stone-100 px-5 py-3">
                    <span class="text-xs text-stone-500">
                        第 {{ (jobPage - 1) * jobPageSize + 1 }}–{{ (jobPage - 1) * jobPageSize + jobs.length }} 条，共 {{ jobTotal }} 条
                    </span>

                    <div class="flex items-center gap-2">
                        <button
                            type="button"
                            class="cursor-pointer rounded-md border border-stone-200 px-2.5 py-1.5 text-xs text-stone-600 transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-40"
                            :disabled="jobPage <= 1"
                            @click="loadJobs(jobPage - 1)"
                        >
                            上一页
                        </button>
                        <span class="text-xs text-stone-500">第 {{ jobPage }} / {{ totalPages }} 页</span>
                        <button
                            type="button"
                            class="cursor-pointer rounded-md border border-stone-200 px-2.5 py-1.5 text-xs text-stone-600 transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-40"
                            :disabled="jobPage >= totalPages"
                            @click="loadJobs(jobPage + 1)"
                        >
                            下一页
                        </button>
                    </div>
                </div>
            </section>

            <!-- 详情弹窗：渲染 raw_text -->
            <Transition name="fade">
                <div v-if="detailJob" class="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/25 p-5" @click="closeDetail">
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
                                <h2 class="truncate text-sm font-semibold text-stone-800">{{ detailJob.title }}</h2>
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
                            <MarkdownText v-if="detailJob.raw_text" :source="detailJob.raw_text" />
                            <p v-else class="py-10 text-center text-xs text-stone-400">这个岗位没有保存原文</p>
                        </div>
                    </div>
                </div>
            </Transition>

            <!-- 删除确认 -->
            <Transition name="fade">
                <div v-if="deletingJob" class="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/25 p-5" @click="cancelDelete">
                    <div
                        class="w-full max-w-sm rounded-lg border border-stone-200 bg-white p-5 shadow-xl"
                        role="dialog"
                        aria-modal="true"
                        aria-label="删除岗位"
                        @click.stop
                    >
                        <h2 class="text-base font-semibold text-stone-900">删除这个岗位？</h2>
                        <p class="mt-2 text-sm leading-relaxed text-stone-500">
                            「{{ deletingJob.title }}」会从岗位列表里移除，这个操作不能撤销。
                        </p>

                        <div class="mt-5 flex justify-end gap-2">
                            <button
                                type="button"
                                class="cursor-pointer rounded-md px-3 py-2 text-sm text-stone-500 transition hover:bg-stone-100 hover:text-stone-800"
                                @click="cancelDelete"
                            >
                                取消
                            </button>
                            <button
                                type="button"
                                class="cursor-pointer rounded-md bg-rose-500 px-3 py-2 text-sm font-medium text-white transition hover:bg-rose-600 disabled:cursor-not-allowed disabled:opacity-60"
                                :disabled="deleteLoading"
                                @click="confirmDelete"
                            >
                                {{ deleteLoading ? "删除中…" : "删除" }}
                            </button>
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
