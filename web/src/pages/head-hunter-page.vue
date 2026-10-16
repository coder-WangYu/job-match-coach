<template>
    <div class="page-shell overflow-y-auto bg-[#f7f6f3] text-stone-800 antialiased">
        <div class="mx-auto w-full max-w-5xl px-5 py-10 sm:px-8">

            <header class="mb-8">
                <h1 class="text-xl font-semibold tracking-tight text-stone-900">猎头工作台</h1>
                <p class="mt-1 text-sm leading-relaxed text-stone-500">
                    岗位、候选人、岗位库分三件事做：先把岗位整理进库，再拿候选人去撞。
                </p>
            </header>

            <div class="grid gap-5 lg:grid-cols-3">

                <!-- 岗位上传 -->
                <article class="flex flex-col rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
                    <span class="grid h-10 w-10 place-items-center rounded-lg bg-amber-50 text-amber-600">
                        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                            <path d="m17 8-5-5-5 5" />
                            <path d="M12 3v12" />
                        </svg>
                    </span>

                    <h2 class="mt-4 text-base font-semibold text-stone-900">岗位上传</h2>
                    <p class="mt-2 flex-1 text-sm leading-relaxed text-stone-500">
                        上传 JD 汇总文档，大模型解析成结构化岗位。逐条确认或修改之后，再批量入库。
                    </p>

                    <router-link
                        to="/head-hunter/upload"
                        class="mt-5 inline-flex items-center justify-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-amber-600"
                    >
                        进入
                        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M5 12h14" />
                            <path d="m12 5 7 7-7 7" />
                        </svg>
                    </router-link>
                </article>

                <!-- 候选人匹配 -->
                <article class="flex flex-col rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
                    <span class="grid h-10 w-10 place-items-center rounded-lg bg-emerald-50 text-emerald-600">
                        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10" />
                            <circle cx="12" cy="12" r="6" />
                            <circle cx="12" cy="12" r="2" />
                        </svg>
                    </span>

                    <h2 class="mt-4 text-base font-semibold text-stone-900">候选人匹配</h2>
                    <p class="mt-2 flex-1 text-sm leading-relaxed text-stone-500">
                        上传一份候选人简历，拿它去撞岗位列表，列出适合推的岗位和匹配分数。
                    </p>

                    <router-link
                        to="/head-hunter/match"
                        class="mt-5 inline-flex items-center justify-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-amber-600"
                    >
                        进入
                        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M5 12h14" />
                            <path d="m12 5 7 7-7 7" />
                        </svg>
                    </router-link>
                </article>

                <!-- 岗位列表 -->
                <article class="flex flex-col rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
                    <span class="grid h-10 w-10 place-items-center rounded-lg bg-sky-50 text-sky-600">
                        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
                            <rect width="20" height="14" x="2" y="6" rx="2" />
                        </svg>
                    </span>

                    <h2 class="mt-4 text-base font-semibold text-stone-900">岗位列表</h2>
                    <p class="mt-2 flex-1 text-sm leading-relaxed text-stone-500">
                        已经入库的全部岗位，按页浏览，以后会越攒越多，随时可以回来翻。
                    </p>

                    <router-link
                        to="/head-hunter/jobs"
                        class="mt-5 inline-flex items-center justify-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-amber-600"
                    >
                        进入
                        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M5 12h14" />
                            <path d="m12 5 7 7-7 7" />
                        </svg>
                    </router-link>
                </article>
            </div>
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
