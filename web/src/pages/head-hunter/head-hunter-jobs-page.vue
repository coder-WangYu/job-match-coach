<script setup>
import { computed, onMounted, ref } from "vue"
import { API_BASE, metaOf, normalizeJob } from "../../utils/job"

const jobs = ref([])
const jobTotal = ref(0)
const jobPage = ref(1)
const jobPageSize = ref(10)
const jobsLoading = ref(false)
const jobsError = ref("")

const totalPages = computed(() => Math.max(1, Math.ceil(jobTotal.value / jobPageSize.value)))

// 分页拉岗位列表
async function loadJobs(page = jobPage.value) {
    jobsLoading.value = true
    jobsError.value = ""

    try {
        // 约定的接口：GET /head-hunter/jobs?page=&page_size= -> { jobs: [...], total }
        const res = await fetch(`${API_BASE}/head-hunter/jobs?page=${page}&page_size=${jobPageSize.value}`)

        if (!res.ok) throw new Error("岗位列表加载失败：" + res.status)

        const data = await res.json()
        jobs.value = (data.jobs ?? []).map(normalizeJob)
        jobTotal.value = Number(data.total) || jobs.value.length
        jobPage.value = page
    } catch (err) {
        jobsError.value = err.message
    } finally {
        jobsLoading.value = false
    }
}

onMounted(() => loadJobs(1))
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
                        已经入库的全部岗位，按页浏览。新岗位在「岗位上传」里解析入库。
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
                        <div class="flex items-start gap-3">
                            <div class="min-w-0 flex-1">
                                <p class="truncate text-sm font-medium text-stone-800">{{ job.title }}</p>
                                <p v-if="metaOf(job)" class="mt-0.5 text-xs text-stone-500">{{ metaOf(job) }}</p>
                            </div>
                            <span class="shrink-0 rounded-md border border-stone-200 bg-stone-50 px-1.5 py-0.5 text-[11px] text-stone-400">
                                {{ job.id }}
                            </span>
                        </div>

                        <div v-if="job.tags.length" class="mt-2 flex flex-wrap gap-1.5">
                            <span
                                v-for="tag in job.tags"
                                :key="tag"
                                class="rounded-md border border-stone-200 bg-stone-50 px-1.5 py-0.5 text-[11px] text-stone-600"
                            >
                                {{ tag }}
                            </span>
                        </div>

                        <p v-if="job.requirements" class="mt-2 line-clamp-2 text-xs leading-relaxed text-stone-500">
                            {{ job.requirements }}
                        </p>
                    </li>
                </ul>

                <p v-else class="px-5 py-16 text-center text-xs text-stone-400">
                    岗位列表还是空的，先去「岗位上传」传一份 JD 汇总文档
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
        </div>
    </div>
</template>

<style scoped>
/* 77px 是顶部粘性表头的高度：内容区占满剩下的一屏并自己滚 */
.page-shell {
    height: calc(100vh - 77px);
    height: calc(100dvh - 77px);
}
</style>
