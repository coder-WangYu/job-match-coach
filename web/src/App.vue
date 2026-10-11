<script setup>
import { ref } from 'vue';

// 获取匹配结果
const score = ref(0)
const suggestions = ref([])
const loading = ref(false)
const error = ref("")

async function match() {
  error.value = ""

  if (!resumeId.value.trim() || !jdId.value.trim()) throw new Error("请填写简历和JD")

  loading.value = true

  try {
    const res = await fetch("http://127.0.0.1:8000/match", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json'},
      body: JSON.stringify({ resume_id: resumeId.value, jd_id: jdId.value})
    })

    if (!res.ok) throw new Error("请求失败：" + res.status)

    const data = await res.json()
    score.value = data.score
    suggestions.value = data.suggestions
  } catch(err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 获取用户简历
const resumeFile = ref(null)
const resumeId = ref("")

async function getResume(e) {
  const file = e.target.files?.[0]
  if (!file) return
  console.log(file.name);

  resumeFile.value = file

  try {
    const form = new FormData()
    form.append("file", resumeFile.value)

    const res = await fetch("http://127.0.0.1:8000/upload-resume", {
      method: 'POST',
      body: form
    })

    const data = await res.json()
    resumeId.value = data.resume_id
  } catch(e) {
    throw new Error("上传失败：" + e.value)
  }
}

// 获取JD
const jdUrl = ref("")
const jdId = ref("")

async function getJD() {
  try {
    const res = await fetch("http://127.0.0.1:8000/fetch-jd", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: jdUrl.value }),
    })

    const data = await res.json()
    jdId.value = data.jd_id
    console.log(data)
  } catch(e) {
    throw new Error("解析失败：" + e.value)
  }
}
</script>

<template>
  <div class="p-2">
    <h1 class="text-2xl font-bold mb-4">
      求职匹配助手
    </h1>

    <h3 class="mb-2">简历：</h3>
    <!-- <textarea class="w-200 h-50 border-2" id="resume" v-model="resume"></textarea> -->
     <input type="file" accept=".pdf,.doc,.docx,.wps" @change="getResume">
     <p v-if="resumeFile">已选择：{{ resumeFile.name }}</p>

    <h3 class="my-2">JD：</h3>
    <!-- <textarea class="w-200 h-50 border-2" id="jd" v-model="jd"></textarea> -->
     <input class="border-2" type="input" v-model="jdUrl" @change="getJD">

    <button class="block my-4 px-4 py-2 rounded-lg cursor-pointer bg-amber-200 hover:bg-amber-500" :disabled="loading" @click="match">
      {{ loading == true ? "分析中..." : "开始匹配" }}
    </button>

    <div class="px-4" v-if="score !== null && suggestions.length > 0">
      <div class="mb-2">匹配分数：<span>{{ score }}</span></div>
      <div>改进建议：</div>
      <ul>
        <li class="pl-4" v-for="(tip, i) in suggestions" :key="i">- {{ tip }}</li>
      </ul>
    </div>
    <div v-if="error">
      <span class="text-red-500">{{ error }}</span>
    </div>
  </div>
</template>
