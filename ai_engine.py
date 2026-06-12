import json
import os
from google import genai
from google.genai import types


def get_client():
    """Create a Gemini client using the API key from secrets or env var."""
    # Try Streamlit secrets first (for deployed app)
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

    # Fall back to environment variable (for local dev)
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Add it to .streamlit/secrets.toml "
            "(local) or your Streamlit Cloud app secrets (deployed)."
        )

    return genai.Client(api_key=api_key)


MODEL_NAME = "gemini-2.5-flash"


def _generate_json(prompt, system_instruction=None):
    """Call Gemini and parse a JSON response, with fallback cleanup."""
    client = get_client()

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
    )
    if system_instruction:
        config.system_instruction = system_instruction

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )

    text = response.text.strip()
    # Strip markdown fences if the model adds them anyway
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


def _generate_text(prompt, system_instruction=None):
    """Call Gemini and return plain text."""
    client = get_client()

    config = types.GenerateContentConfig()
    if system_instruction:
        config.system_instruction = system_instruction

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )
    return response.text.strip()


def analyze_resume_sections(resume_text, jd_text):
    """Get section-by-section feedback on the resume against the JD."""
    system_instruction = (
        "You are an expert technical recruiter and resume reviewer. "
        "You give honest, specific, actionable feedback. "
        "You never use em dashes. You write in plain, direct language. "
        "Always respond with valid JSON only, no markdown formatting."
    )

    prompt = f"""Analyze this resume against the job description below.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Return a JSON object with this exact structure:
{{
  "overall_summary": "2-3 sentence overall assessment of fit",
  "sections": [
    {{
      "section_name": "Summary/Objective",
      "rating": "strong" | "needs_work" | "missing",
      "feedback": "specific feedback for this section, 2-3 sentences"
    }},
    {{
      "section_name": "Skills",
      "rating": "strong" | "needs_work" | "missing",
      "feedback": "specific feedback"
    }},
    {{
      "section_name": "Experience/Projects",
      "rating": "strong" | "needs_work" | "missing",
      "feedback": "specific feedback"
    }},
    {{
      "section_name": "Education",
      "rating": "strong" | "needs_work" | "missing",
      "feedback": "specific feedback"
    }}
  ],
  "top_priorities": ["priority 1 action item", "priority 2 action item", "priority 3 action item"]
}}"""

    return _generate_json(prompt, system_instruction)


def suggest_bullet_rewrites(resume_text, jd_text, max_bullets=8):
    """Suggest rewrites for weak bullet points in the resume."""
    system_instruction = (
        "You are an expert resume writer. You rewrite weak bullet points into "
        "strong, quantified, action-oriented bullets tailored to a target job. "
        "You never invent metrics or experience the person doesn't have. "
        "You never use em dashes. Always respond with valid JSON only."
    )

    prompt = f"""Here is a resume and a target job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Find up to {max_bullets} bullet points or sentences in the resume's experience/projects
sections that are weak, vague, or could be better aligned with the job description.
For each one, suggest an improved version. Only suggest improvements based on what's
already stated, do not invent new skills, tools, or numbers that aren't implied by
the original text.

Return a JSON object with this exact structure:
{{
  "rewrites": [
    {{
      "original": "the original bullet text",
      "improved": "the improved bullet text",
      "why": "one sentence explaining why this is better"
    }}
  ]
}}

If the resume is already strong and you find fewer than 3 things to improve, that's fine,
just return what you genuinely found."""

    return _generate_json(prompt, system_instruction)


def generate_cover_letter(resume_text, jd_text, company_name=None, tone="professional"):
    """Generate a tailored cover letter based on resume and job description."""
    system_instruction = (
        "You are an expert cover letter writer. You write concise, specific, "
        "genuine-sounding cover letters that connect a candidate's real experience "
        "to a job description. You never use em dashes. You avoid generic "
        "phrases like 'I am writing to express my interest'. "
        "You write only the letter body, no subject line, no JSON, plain text only."
    )

    company_line = f"The company is {company_name}." if company_name else "No company name was given, write it generically without inventing one."

    prompt = f"""Write a {tone} cover letter for this candidate applying to this job.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

{company_line}

Keep it to 3-4 short paragraphs. Be specific about how the candidate's actual
experience (from the resume) matches what the job needs. Do not invent
experience that isn't in the resume. Do not use em dashes."""

    return _generate_text(prompt, system_instruction)


def extract_jd_keywords_ai(jd_text, top_n=20):
    """Use AI to extract the most important keywords/skills from a job description."""
    system_instruction = (
        "You extract the most important skills, tools, and qualifications from "
        "job descriptions. Always respond with valid JSON only."
    )

    prompt = f"""Extract the {top_n} most important keywords from this job description
that an ATS system or recruiter would search for. Focus on specific skills,
tools, technologies, certifications, and qualifications. Avoid generic words
like "team", "communication", "experience".

JOB DESCRIPTION:
{jd_text}

Return a JSON object:
{{
  "keywords": ["keyword1", "keyword2", ...]
}}"""

    return _generate_json(prompt, system_instruction)
