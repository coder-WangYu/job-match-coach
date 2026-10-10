import streamlit as st
from job_match_coach.models import Resume, JobDescription
from job_match_coach.llm_matcher import match_with_llm

st.title("求职匹配助手")
st.write("把简历和 JD 贴进来，我会给出匹配分和改进建议。")

resume_text = st.text_area("简历")
jd_text=st.text_area("JD")

if st.button("开始匹配"):
    if not resume_text.strip() or not jd_text.strip():
        st.warning("请先填写简历和JD")
        st.stop()
    
    with st.spinner("分析中"):
        result = match_with_llm(Resume(text=resume_text), JobDescription(text=jd_text))
    
    st.metric("匹配分", result.score)

    for tip in result.suggestions:
        st.write(f"- {tip}")
