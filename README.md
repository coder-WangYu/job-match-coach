## 项目是什么
根据目前的求职场景，求职者上传简历和对应的JD，由大模型分析匹配程度并给出简历改进建议

## 技术栈
1. python
2. Vue
3. FastAPI
4. Streamlit（可选）
5. Tailwind

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