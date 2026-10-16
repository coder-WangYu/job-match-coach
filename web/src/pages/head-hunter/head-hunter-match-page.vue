<script setup>
import { computed, ref } from "vue"
import { API_BASE, metaOf, toneOf } from "../../utils/job"

const resumeFile = ref(null)
const matching = ref(false)
const matchStage = ref("")
const matches = ref([])
const matchError = ref("")

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

// 上传简历（复用已有的 /upload_resume），再拿 resume_id 去岗位库比对
async function uploadResume(e) {
    const file = e.target.files?.[0]
    if (!file) return

    matchError.value = ""
    matching.value = true
    matchStage.value = "正在解析简历…"
    matches.value = []
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

                        <div v-if="matchedJobs.length" class="grid gap-2.5 sm:grid-cols-2 xl:grid-cols-3">
                            <article
                                v-for="item in matchedJobs"
                                :key="item.job_id ?? item.id"
                                class="rounded-lg border border-stone-200/80 bg-stone-50/60 px-3 py-2.5"
                                :title="metaOf(item.job)"
                            >
                                <p class="text-xs leading-none text-stone-500">
                                    匹配分数：<span class="text-sm font-semibold" :class="toneOf(item.score)">{{ Math.round(item.score) }}</span>
                                </p>
                                <p class="mt-1.5 line-clamp-2 text-xs leading-relaxed text-stone-700">
                                    {{ item.job?.title ?? "岗位列表里没找到这个 id" }}
                                </p>
                            </article>
                        </div>

                        <p v-else class="flex h-full min-h-44 items-center justify-center rounded-lg border border-dashed border-stone-200 px-4 text-center text-xs leading-relaxed text-stone-400">
                            上传一份候选人简历<br />这里会列出他适合的岗位
                        </p>
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
