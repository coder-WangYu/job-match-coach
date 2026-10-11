## 项目是什么
根据目前的求职场景，求职者上传简历和对应的JD，由大模型分析匹配程度并给出简历改进建议

## 技术栈
1. python
2. Vue
3. FastAPI
5. Tailwind
6. LangGraph

## 如何配置 .env
在.env文件中添加 DEEPSEEK_API_KEY

## 如何启动后端
在项目根目录使用以下命令：
uv run uvicorn job_match_coach.api:app --reload --port 8000

http://127.0.0.1:8000/health - 用于测试接口是否健康
http://127.0.0.1:8000/docs - 查看接口文档

## 如何启动前端
进入web文件夹使用一下命令：
npm run dev

## 如何使用
1. 上传简历（/upload-resume）获取resume_id，简历内容保存在后端
2. 填写JD内容：手动粘贴岗位要求、任职要求等
3. 匹配（/match）时通过给后端传resume_id、jd以获取结果
    - 这里走LangGraph(START -> extract_skills -> score_and_suggest -> END)
    - 主要是通过 graph_state.py 创建图状态
               graph_nodes.py 创建图节点
               graph.py 构建完整的图
    - 最后在 /match 接口中通过 graph.invoke调用LLM获取匹配结果