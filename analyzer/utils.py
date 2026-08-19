import os
import json

from groq import Groq
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_resume_with_ai(resume_text, job_description):

    prompt = f"""
You are an expert ATS resume analyzer.

Analyze the given resume against the job description.

Return ONLY valid JSON.

Exact format:

{{
    "match_score": 85,
    "matched_skills": ["Python", "Django", "React"],
    "missing_skills": ["Docker", "AWS", "Redis"],
    "recommendations": "Learn Docker, AWS deployment, Redis caching, and improve system design knowledge."
}}

Rules:

1. match_score must be a number between 0 and 100.
2. matched_skills must be a JSON list of skills found in both the resume and job description.
3. missing_skills must be a JSON list of important skills required by the job but missing from the resume.
4. recommendations must be a clear career-focused explanation.
5. Return ONLY JSON.
6. Do not use Markdown.
7. Do not put the JSON inside ```json blocks.

Resume:
{resume_text}

Job Description:
{job_description}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    # Remove Markdown code fences if the model accidentally adds them
    if "```" in content:
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:
        result = json.loads(content)

        # Make sure required fields exist
        return {
            "match_score": result.get("match_score", 0),
            "matched_skills": result.get("matched_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "recommendations": result.get("recommendations", "")
        }

    except (json.JSONDecodeError, TypeError, ValueError):

        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "recommendations": content
        }


def chatbot_response(user_question, analysis_context):

    prompt = f"""
You are an AI career coach inside an application called SkillMap.

Use the resume analysis context below to answer the user's question.

Resume Analysis Context:
{analysis_context}

User Question:
{user_question}

Give a helpful, practical and career-focused answer.

Focus on:
- Resume improvement
- Missing skills
- Learning roadmap
- Projects
- Interview preparation
- Job preparation
- Career guidance

Keep the answer clear and useful.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content