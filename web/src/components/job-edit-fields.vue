<script setup>
// 草稿和入库失败列表共用的一套编辑字段
const model = defineModel({ type: Object, required: true })
</script>

<template>
    <div class="grid gap-2">
        <input
            v-model="model.title"
            placeholder="岗位名称"
            class="w-full rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100"
        >

        <div class="grid gap-2 sm:grid-cols-3">
            <input
                v-model="model.edu"
                placeholder="学历"
                class="w-full rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100"
            >
            <input
                v-model="model.location"
                placeholder="城市"
                class="w-full rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100"
            >
            <input
                v-model="model.salary"
                placeholder="薪资"
                class="w-full rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100"
            >
        </div>

        <input
            v-model="model.tagsText"
            placeholder="标签，用、分隔"
            class="w-full rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100"
        >

        <textarea
            v-model="model.requirements"
            rows="2"
            placeholder="任职要求"
            class="w-full resize-none rounded-md border border-stone-200 bg-white px-2.5 py-1.5 text-xs leading-relaxed text-stone-700 placeholder:text-stone-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100"
        ></textarea>
    </div>
</template>
