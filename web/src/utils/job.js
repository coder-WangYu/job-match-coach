// 猎头这块几个页面共用的小工具

export const API_BASE = "http://127.0.0.1:8000"

// 岗位按这几个字段渲染；后端字段名如果有出入，改这一个函数就够了
export function normalizeJob(item, index) {
    return {
        id: item.id ?? item.job_id ?? `job-${index + 1}`,
        title: item.title ?? item.job_title ?? item.name ?? "未命名岗位",
        company: item.company ?? "",
        location: item.location ?? item.city ?? "",
        salary: item.salary ?? item.salary_range ?? "",
        tags: Array.isArray(item.tags) ? item.tags : (Array.isArray(item.skills) ? item.skills : []),
        requirements: item.requirements ?? item.description ?? "",
        raw_text: item.raw_text ?? "",
    }
}

export function metaOf(job) {
    return [job?.company, job?.location, job?.salary].filter(Boolean).join(" · ")
}

// 标签用顿号或逗号分隔
export function parseTags(text) {
    return text.split(/[、,，;；]/).map((item) => item.trim()).filter(Boolean)
}

// 分数越高颜色越柔和
export function toneOf(score) {
    if (score >= 80) return "text-emerald-600"
    if (score >= 60) return "text-amber-600"
    return "text-rose-500"
}
