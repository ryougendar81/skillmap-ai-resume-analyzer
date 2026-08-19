import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


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

    Resume:
    {resume_text}

    Job Description:
    {job_description}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    if "```" in content:
        content = content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(content)

    except:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "recommendations": content
        }


def chatbot_response(user_question, analysis_context):
    prompt = f"""
    You are an AI career coach.

    Resume analysis context:
    {analysis_context}

    User question:
    {user_question}

    Give a helpful career-focused answer.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content