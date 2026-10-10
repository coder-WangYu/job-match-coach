from job_match_coach.llm_matcher import match_with_llm
from job_match_coach.models import Resume, JobDescription

def main() -> None:
    resume_text = input("请输入简历：")
    jd_text = input("请输入JD：")

    result = match_with_llm(Resume(text=resume_text), JobDescription(text=jd_text))

    print(f"匹配分：{result.score}")
    print("改进建议：")
    for tip in result.suggestions:
        print(f"- {tip}")

if __name__ == "__main__":
    main()
