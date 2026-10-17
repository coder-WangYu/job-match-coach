import hashlib
import json
from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from job_match_coach.auth.supabase_client import get_supabase
from job_match_coach.core.store import RESUME_STORE
from job_match_coach.llm.embed import embed
from job_match_coach.llm.llm import ask

router = APIRouter()


@router.post("/jobs")
async def jobs(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8")

    raw = ask(
        f"""
            你是岗位信息抽取助手。下面是一份 Markdown 招聘文档，可能包含一个或多个岗位。
            请抽取为 JSON 数组，每个元素只能包含这些字段：
                title：岗位名称；
                edu：学历；
                location：城市；
                salary：薪资范围；
                tags：职位描述；
                requirements：任职要求；
                raw_text：该岗位原文（原封不动的写进来）
            其中 tags 必须是字符串数组，requirements 用一段文字概括任职要求。

            要求：
                1. 只输出合法 JSON 数组；
                2. 不要 markdown 代码块，不要其它说明。
                3. 文档里没有的信息填空字符串或空数组，不要编造。

            文档内容：{content}
        """
    )

    jobs = json.loads(raw)

    return {"jobs": jobs}


class ImportRequest(BaseModel):
    jobs: list[dict]


@router.post("/jobs-import")
def jobs_import(body: ImportRequest):
    sb = get_supabase()
    imported = 0
    skipped = []

    for job in body.jobs:
        hash_info = (
            job.get("title").strip()
            + job.get("location").strip()
            + job.get("edu").strip()
            + job.get("salary").strip()
        )
        content_hash = hashlib.sha256(hash_info.encode("utf-8")).hexdigest()

        # 已有相同原文则跳过
        exists = (
            sb.table("jobs")
            .select("id")
            .eq("content_hash", content_hash)
            .limit(1)
            .execute()
        )

        if exists.data:
            skipped.append(job)
            continue

        row = job | {
            "content_hash": content_hash,
            "embedding": embed(job.get("raw_text").strip()),
        }

        sb.table("jobs").insert(row).execute()
        imported += 1

    return {"imported": imported, "skipped": skipped}


@router.get("/get-jobs")
def get_jobs(page: int = 1, page_size: int = 10):
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10

    sb = get_supabase()
    start = (page - 1) * page_size
    end = start + page_size - 1

    response = (
        sb.table("jobs")
        .select(
            "id, title, edu, location, salary, tags, requirements, raw_text, created_at",
            count="exact",
        )
        .order("created_at", desc=True)
        .range(start, end)
        .execute()
    )

    return {"jobs": response.data or [], "total": response.count or 0}


@router.post("/match")
def match(body: dict):
    resume_id = body.get("resume_id")
    resume = RESUME_STORE.get(resume_id)
    resume_embed = embed(resume)

    sb = get_supabase()
    result_top5 = (
        sb.rpc("match_jobs", {"query_embedding": resume_embed, "match_count": 5})
        .execute()
        .data
    )

    jobs_text = "\n\n".join(
        f"岗位id: {j['id']}\n"
        f"标题: {j.get('title') or ''}\n"
        f"学历: {j.get('edu') or ''}\n"
        f"地点: {j.get('location') or ''}\n"
        f"薪资: {j.get('salary') or ''}\n"
        f"要求: {j.get('requirements') or ''}\n"
        f"原文: {j.get('raw_text') or ''}"
        for j in result_top5
    )
    print(jobs_text)

    response = ask(
        f"""
        你是猎头人岗匹配助手。根据候选人简历，给下面每个候选岗位打 0–100 分。
        
        要求：
            1. 只输出合法 JSON 数组
            2. 不要 markdown
            3. 不要其它说明
            4. 每个元素字段：
                id: 岗位 id（必须与下面完全一致）
                score: 整数 0–100
                reason: 一句话理由
        
        分档参考：
            >=80 非常推荐；
            60–79 可约面；
            45–59 可优化；
            <50 不适合。
        
        候选人简历：{resume}
        候选岗位：{jobs_text}
    """
    )

    result = json.loads(response)
    by_id = {str(j["id"]): j for j in result_top5}
    matches = []
    for item in result:
        job = by_id.get(str(item.get("id")))
        if not job:
            continue
        
        score = int(item.get("score") or 0)
        if score < 50:
            continue

        matches.append(
            {
                "job": {
                    "id": job["id"],
                    "title": job.get("title"),
                    "edu": job.get("edu"),
                    "location": job.get("location"),
                    "salary": job.get("salary"),
                    "tags": job.get("tags"),
                    "requirements": job.get("requirements"),
                    "raw_text": job.get("raw_text"),
                },
                "score": score,
                "reason": item.get("reason") or "",
            }
        )
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    return {"matches": matches}
