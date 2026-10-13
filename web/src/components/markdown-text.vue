<script>
import DOMPurify from 'dompurify'

// 模块级只跑一次：正文里的链接一律新开标签页，免得把正在进行的对话顶掉
DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node.tagName === 'A' && node.hasAttribute('href')) {
    node.setAttribute('target', '_blank')
    node.setAttribute('rel', 'noopener noreferrer')
  }
})
</script>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  // Markdown 原文
  source: { type: String, default: "" },
  // 只渲染行内语法（加粗、行内代码、链接），不生成段落、列表这些块级元素
  inline: { type: Boolean, default: false },
})

// 聊天场景下单个换行也要留住，表格等用 GFM 语法
const MARKED_OPTIONS = { gfm: true, breaks: true }

const html = computed(() => {
  const raw = props.inline
    ? marked.parseInline(props.source, MARKED_OPTIONS)
    : marked.parse(props.source, MARKED_OPTIONS)

  // 模型输出属于不可信内容，插进 DOM 之前先过滤一遍
  return DOMPurify.sanitize(raw)
})
</script>

<template>
  <div class="markdown-body" v-html="html"></div>
</template>

<style scoped>
/* v-html 生成的内容不带 scoped 属性，所以这里统一用 :deep() 才命中得了 */
.markdown-body {
  font-size: 0.875rem;
  line-height: 1.75;
  color: #57534e;
  word-break: break-word;
}

/* 首尾元素不要多出外边距，免得气泡里上下留一大块空白 */
.markdown-body :deep(> *:first-child) {
  margin-top: 0;
}

.markdown-body :deep(> *:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(p) {
  margin: 0.5rem 0;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin: 1rem 0 0.5rem;
  font-weight: 600;
  line-height: 1.45;
  color: #1c1917;
}

.markdown-body :deep(h1) {
  font-size: 1.05rem;
}

.markdown-body :deep(h2) {
  font-size: 0.975rem;
}

.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  font-size: 0.875rem;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}

.markdown-body :deep(ul) {
  list-style: disc;
}

.markdown-body :deep(ol) {
  list-style: decimal;
}

.markdown-body :deep(li) {
  margin: 0.25rem 0;
}

.markdown-body :deep(li::marker) {
  color: #a8a29e;
}

.markdown-body :deep(strong) {
  font-weight: 600;
  color: #1c1917;
}

.markdown-body :deep(a) {
  color: #b45309;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.markdown-body :deep(a:hover) {
  color: #92400e;
}

.markdown-body :deep(code) {
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  background: #f5f5f4;
  font-size: 0.85em;
  color: #b45309;
}

.markdown-body :deep(pre) {
  margin: 0.6rem 0;
  padding: 0.75rem 0.9rem;
  border-radius: 8px;
  background: #f5f5f4;
  overflow-x: auto;
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: transparent;
  font-size: 0.8rem;
  line-height: 1.6;
  color: #44403c;
}

.markdown-body :deep(blockquote) {
  margin: 0.6rem 0;
  padding: 0.25rem 0 0.25rem 0.75rem;
  border-left: 3px solid #fcd34d;
  color: #57534e;
}

.markdown-body :deep(hr) {
  margin: 0.9rem 0;
  border: 0;
  border-top: 1px solid #e7e5e4;
}

.markdown-body :deep(table) {
  width: 100%;
  margin: 0.6rem 0;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 0.4rem 0.6rem;
  border: 1px solid #e7e5e4;
  text-align: left;
  vertical-align: top;
}

.markdown-body :deep(th) {
  background: #fafaf9;
  font-weight: 600;
  color: #1c1917;
}

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 8px;
}
</style>
