<template>
  <div class="min-h-screen bg-[#f7f6f3] text-stone-800 antialiased">

    <!-- 顶部导航 -->
    <header class="sticky top-0 z-10 border-b border-stone-200/70 bg-[#f7f6f3]/95 backdrop-blur">
      <div class="mx-auto flex max-w-6xl items-center gap-3 px-5 py-3.5 sm:px-8">
        <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-amber-400 text-white shadow-sm">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
            <rect width="20" height="14" x="2" y="6" rx="2" />
          </svg>
        </span>
        <div class="flex min-w-0 flex-col leading-tight">
          <span class="truncate text-sm font-semibold text-stone-900">同频</span>
          <span class="truncate text-[11px] text-stone-400">人岗智配Agent</span>
        </div>

        <nav class="ml-auto flex items-center gap-1">
          <router-link to="/job-seeker" class="hidden rounded-md px-3 py-2 text-sm text-stone-600 transition hover:bg-white hover:text-stone-900 sm:block">
            求职者
          </router-link>
          <router-link to="/hr" class="hidden rounded-md px-3 py-2 text-sm text-stone-600 transition hover:bg-white hover:text-stone-900 sm:block">
            HR
          </router-link>
          <router-link to="/head-hunter" class="hidden rounded-md px-3 py-2 text-sm text-stone-600 transition hover:bg-white hover:text-stone-900 sm:block">
            猎头
          </router-link>
          <router-link to="/login" class="rounded-md border border-stone-300 bg-white px-3.5 py-2 text-sm font-medium text-stone-700 transition hover:border-stone-400 hover:text-stone-900">
            登录
          </router-link>
        </nav>
      </div>
    </header>

    <!-- 首屏 -->
    <section class="mx-auto max-w-6xl px-5 pb-12 pt-10 sm:px-8 sm:pb-16 sm:pt-16">
      <div class="grid items-center gap-10 lg:grid-cols-[1.05fr_minmax(0,360px)] lg:gap-14">
        <div>
          <span class="inline-flex items-center gap-1.5 rounded-md bg-amber-100/70 px-2.5 py-1 text-xs font-medium text-amber-700">
            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 3v18" />
              <path d="m5 8 7-5 7 5" />
              <path d="m5 16 7 5 7-5" />
            </svg>
            三种角色，三条入口
          </span>

          <h1 class="mt-4 text-2xl font-semibold tracking-tight text-stone-900 sm:text-3xl lg:text-4xl">
            同频——人岗智配Agent
          </h1>

          <p class="mt-4 max-w-xl text-base leading-relaxed text-stone-600">
            把简历和岗位要求一起交给大模型，让系统读懂内容本身，而不是去数关键词有没有出现过。求职者知道自己该补什么，HR 知道先看哪几份，猎头知道这个候选人适合哪些岗位。
          </p>

          <div class="mt-5 flex flex-wrap gap-2">
            <span class="rounded-md border border-stone-200 bg-white px-2.5 py-1 text-xs text-stone-500">大模型语义匹配</span>
            <span class="rounded-md border border-stone-200 bg-white px-2.5 py-1 text-xs text-stone-500">PDF 简历自动解析</span>
            <span class="rounded-md border border-stone-200 bg-white px-2.5 py-1 text-xs text-stone-500">LangGraph 编排流程</span>
          </div>

          <div class="mt-7 flex flex-col gap-3 sm:flex-row">
            <router-link to="/job-seeker" class="inline-flex items-center justify-center gap-2 rounded-lg bg-amber-500 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-amber-600">
              我是求职者，开始匹配
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
            </router-link>
            <router-link to="/hr" class="inline-flex items-center justify-center gap-2 rounded-lg border border-stone-300 bg-white px-6 py-3 text-sm font-medium text-stone-700 transition hover:border-stone-400 hover:text-stone-900">
              我是 HR，去筛简历
            </router-link>
          </div>
        </div>

        <!-- 产品实际输出的样子 -->
        <div class="rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center gap-2 text-xs text-stone-500">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
            求职者 · 匹配结果
          </div>

          <div class="flex items-center gap-4">
            <div class="relative h-24 w-24 shrink-0">
              <svg class="h-24 w-24 -rotate-90" viewBox="0 0 80 80">
                <circle cx="40" cy="40" r="34" fill="none" stroke="#ece9e4" stroke-width="7" />
                <circle
                  cx="40" cy="40" r="34" fill="none"
                  stroke="#f59e0b" stroke-width="7" stroke-linecap="round"
                  stroke-dasharray="213.628" stroke-dashoffset="47"
                />
              </svg>
              <div class="absolute inset-0 grid place-items-center">
                <div class="text-center">
                  <div class="text-xl font-semibold leading-none text-amber-600">78</div>
                  <div class="mt-1 text-[10px] text-stone-500">匹配度</div>
                </div>
              </div>
            </div>
            <p class="text-sm leading-relaxed text-stone-500">
              匹配度不错，补上下面这几处缺口，通过率会更高。
            </p>
          </div>

          <div class="mt-4 space-y-2 border-t border-stone-100 pt-4">
            <div class="flex gap-2.5 rounded-md bg-stone-50 px-3 py-2.5">
              <span class="mt-0.5 grid h-4 w-4 shrink-0 place-items-center rounded-full bg-amber-100 text-[10px] font-semibold text-amber-700">1</span>
              <span class="text-xs leading-relaxed text-stone-600">岗位要求 3 年以上前端经验，简历里没写年限，建议点明工作年限。</span>
            </div>
            <div class="flex gap-2.5 rounded-md bg-stone-50 px-3 py-2.5">
              <span class="mt-0.5 grid h-4 w-4 shrink-0 place-items-center rounded-full bg-amber-100 text-[10px] font-semibold text-amber-700">2</span>
              <span class="text-xs leading-relaxed text-stone-600">JD 强调 React 生态，建议补一个用 Hooks 重构的项目案例。</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 三种角色 -->
    <section class="border-t border-stone-200/70 bg-white/60">
      <div class="mx-auto max-w-6xl px-5 py-14 sm:px-8">
        <div class="max-w-2xl">
          <h2 class="text-xl font-semibold tracking-tight text-stone-900">你在什么位置，就从哪进去</h2>
          <p class="mt-2 text-sm leading-relaxed text-stone-500">
            同一套匹配能力，三种角色看到的结果不一样：求职者要建议，HR 要排序，猎头要岗位清单。
          </p>
        </div>

        <div class="mt-8 grid gap-5 md:grid-cols-3">
          <!-- 求职者 -->
          <article class="flex flex-col rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
            <div class="flex items-center gap-2.5">
              <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-amber-50 text-amber-600">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </span>
              <div class="min-w-0">
                <h3 class="text-sm font-semibold text-stone-900">求职者</h3>
                <p class="text-xs text-stone-500">这个岗位适不适合我</p>
              </div>
            </div>

            <ol class="mt-5 space-y-2.5">
              <li class="flex gap-2.5 text-sm leading-relaxed text-stone-600">
                <span class="text-xs font-semibold text-amber-500">01</span>
                上传自己的简历（PDF）
              </li>
              <li class="flex gap-2.5 text-sm leading-relaxed text-stone-600">
                <span class="text-xs font-semibold text-amber-500">02</span>
                粘贴想投的岗位 JD
              </li>
              <li class="flex gap-2.5 text-sm leading-relaxed text-stone-600">
                <span class="text-xs font-semibold text-amber-500">03</span>
                拿到匹配分数和逐条改进建议
              </li>
            </ol>

            <div class="mt-5 rounded-md bg-stone-50 px-3 py-3">
              <p class="text-xs font-medium text-stone-500">解决什么</p>
              <p class="mt-1 text-sm leading-relaxed text-stone-600">
                投之前就知道差在哪，把简历按岗位要求逐条补齐，不再盲目海投。
              </p>
            </div>

            <router-link to="/job-seeker" class="mt-5 inline-flex items-center gap-1.5 text-sm font-medium text-amber-600 transition hover:text-amber-700 md:mt-auto md:pt-5">
              进入求职者页面
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
            </router-link>
          </article>

          <!-- HR -->
          <article class="flex flex-col rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
            <div class="flex items-center gap-2.5">
              <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-emerald-50 text-emerald-600">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
              </span>
              <div class="min-w-0">
                <h3 class="text-sm font-semibold text-stone-900">HR</h3>
                <p class="text-xs text-stone-500">这批简历里先看谁</p>
              </div>
            </div>

            <ol class="mt-5 space-y-2.5">
              <li class="flex gap-2.5 text-sm leading-relaxed text-stone-600">
                <span class="text-xs font-semibold text-emerald-500">01</span>
                写清这个岗位的要求
              </li>
              <li class="flex gap-2.5 text-sm leading-relaxed text-stone-600">
                <span class="text-xs font-semibold text-emerald-500">02</span>
                批量上传收到的多份简历
              </li>
              <li class="flex gap-2.5 text-sm leading-relaxed text-stone-600">
                <span class="text-xs font-semibold text-emerald-500">03</span>
                按匹配度排好序，直接挑人
              </li>
            </ol>

            <div class="mt-5 rounded-md bg-stone-50 px-3 py-3">
              <p class="text-xs font-medium text-stone-500">解决什么</p>
              <p class="mt-1 text-sm leading-relaxed text-stone-600">
                几十份简历不用一份份硬读，把时间花在最匹配的那几位候选人身上。
              </p>
            </div>

            <router-link to="/hr" class="mt-5 inline-flex items-center gap-1.5 text-sm font-medium text-emerald-600 transition hover:text-emerald-700 md:mt-auto md:pt-5">
              进入 HR 页面
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
            </router-link>
          </article>

          <!-- 猎头 -->
          <article class="flex flex-col rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
            <div class="flex items-center gap-2.5">
              <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-sky-50 text-sky-600">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <circle cx="12" cy="12" r="6" />
                  <circle cx="12" cy="12" r="2" />
                </svg>
              </span>
              <div class="min-w-0">
                <h3 class="text-sm font-semibold text-stone-900">猎头</h3>
                <p class="text-xs text-stone-500">这个人能推哪些岗位</p>
              </div>
            </div>

            <ol class="mt-5 space-y-2.5">
              <li class="flex gap-2.5 text-sm leading-relaxed text-stone-600">
                <span class="text-xs font-semibold text-sky-500">01</span>
                建立岗位知识库，把手里岗位收进来
              </li>
              <li class="flex gap-2.5 text-sm leading-relaxed text-stone-600">
                <span class="text-xs font-semibold text-sky-500">02</span>
                上传候选人的简历
              </li>
              <li class="flex gap-2.5 text-sm leading-relaxed text-stone-600">
                <span class="text-xs font-semibold text-sky-500">03</span>
                得到一份「适合哪些岗位」的清单
              </li>
            </ol>

            <div class="mt-5 rounded-md bg-stone-50 px-3 py-3">
              <p class="text-xs font-medium text-stone-500">解决什么</p>
              <p class="mt-1 text-sm leading-relaxed text-stone-600">
                让一份简历去撞一遍全部岗位，手里攒下的岗位资源也能反复用起来。
              </p>
            </div>

            <router-link to="/head-hunter" class="mt-5 inline-flex items-center gap-1.5 text-sm font-medium text-sky-600 transition hover:text-sky-700 md:mt-auto md:pt-5">
              进入猎头页面
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
            </router-link>
          </article>
        </div>
      </div>
    </section>

    <!-- 解决什么问题 -->
    <section class="border-t border-stone-200/70">
      <div class="mx-auto max-w-6xl px-5 py-14 sm:px-8">
        <div class="max-w-2xl">
          <h2 class="text-xl font-semibold tracking-tight text-stone-900">它解决什么问题</h2>
          <p class="mt-2 text-sm leading-relaxed text-stone-500">
            这三件事，原来都得靠人一条条读、一份份比。
          </p>
        </div>

        <div class="mt-8 grid gap-5 md:grid-cols-3">
          <div class="rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
            <span class="grid h-8 w-8 place-items-center rounded-md bg-amber-50 text-amber-600">
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </span>
            <h3 class="mt-4 text-sm font-semibold text-stone-900">简历投出去没回音</h3>
            <p class="mt-2 text-sm leading-relaxed text-stone-600">
              先看清和岗位的差距在哪，再决定要不要投、该补哪几处，而不是投完等消息。
            </p>
          </div>

          <div class="rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
            <span class="grid h-8 w-8 place-items-center rounded-md bg-emerald-50 text-emerald-600">
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z" />
                <path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65" />
                <path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65" />
              </svg>
            </span>
            <h3 class="mt-4 text-sm font-semibold text-stone-900">简历太多看不过来</h3>
            <p class="mt-2 text-sm leading-relaxed text-stone-600">
              先按匹配度排一次序，值得细看的排在前面，阅读时间花在更可能合适的人身上。
            </p>
          </div>

          <div class="rounded-lg border border-stone-200/80 bg-white p-5 shadow-sm">
            <span class="grid h-8 w-8 place-items-center rounded-md bg-sky-50 text-sky-600">
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <circle cx="12" cy="12" r="6" />
                <circle cx="12" cy="12" r="2" />
              </svg>
            </span>
            <h3 class="mt-4 text-sm font-semibold text-stone-900">候选人只敢推一个岗位</h3>
            <p class="mt-2 text-sm leading-relaxed text-stone-600">
              把岗位攒成知识库，让简历去撞一遍，一次找出真正对得上的那几个岗位。
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- 匹配流程 -->
    <section class="border-t border-stone-200/70 bg-white/60">
      <div class="mx-auto max-w-6xl px-5 py-14 sm:px-8">
        <div class="grid gap-8 lg:grid-cols-[minmax(0,260px)_1fr] lg:items-center lg:gap-14">
          <div>
            <h2 class="text-xl font-semibold tracking-tight text-stone-900">匹配是怎么跑出来的</h2>
            <p class="mt-2 text-sm leading-relaxed text-stone-500">
              简历和岗位文本进去，先抽技能，再打分给建议，中间结果在节点之间传递。
            </p>
          </div>

          <ol class="grid gap-4 sm:grid-cols-3">
            <li class="rounded-lg border border-stone-200/80 bg-white p-4">
              <span class="text-xs font-semibold text-amber-500">01</span>
              <h3 class="mt-2 text-sm font-semibold text-stone-900">读简历与岗位</h3>
              <p class="mt-1 text-xs leading-relaxed text-stone-500">PDF 解析成文本，和粘贴的 JD 一起带进流程。</p>
            </li>
            <li class="rounded-lg border border-stone-200/80 bg-white p-4">
              <span class="text-xs font-semibold text-amber-500">02</span>
              <h3 class="mt-2 text-sm font-semibold text-stone-900">抽取关键技能</h3>
              <p class="mt-1 text-xs leading-relaxed text-stone-500">从两边内容里提出技能项，作为打分的依据。</p>
            </li>
            <li class="rounded-lg border border-stone-200/80 bg-white p-4">
              <span class="text-xs font-semibold text-amber-500">03</span>
              <h3 class="mt-2 text-sm font-semibold text-stone-900">打分并给建议</h3>
              <p class="mt-1 text-xs leading-relaxed text-stone-500">给出匹配分数，以及可以逐条改进的具体建议。</p>
            </li>
          </ol>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="border-t border-stone-200/70">
      <div class="mx-auto flex max-w-6xl flex-col gap-2 px-5 py-8 text-xs text-stone-500 sm:flex-row sm:items-center sm:px-8">
        <span>同频——人岗智配Agent</span>
        <span class="sm:ml-auto">分析结果由大模型生成，建议结合实际情况判断。</span>
      </div>
    </footer>
  </div>
</template>
