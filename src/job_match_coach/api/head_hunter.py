import json
from fastapi import APIRouter, File, HTTPException, UploadFile

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
