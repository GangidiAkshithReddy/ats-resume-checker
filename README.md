# AI ATS Resume Checker

A free, no-login web app that compares your resume against a job description
and gives you a match score, missing keywords, AI section feedback, bullet
rewrite suggestions, a generated cover letter, and a downloadable PDF report.

## Files
- `app.py` — Streamlit app (UI)
- `parser_utils.py` — extracts text from PDF/DOCX, checks formatting issues
- `matcher.py` — keyword extraction and scoring logic
- `ai_engine.py` — Gemini AI integration (section feedback, rewrites, cover letter)
- `pdf_report.py` — generates downloadable PDF report
- `requirements.txt` — dependencies
- `.streamlit/secrets.toml.example` — template for your Gemini API key

## Setup

1. Get a free Gemini API key from https://aistudio.google.com/app/apikey
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
3. Paste your key into `secrets.toml`:
   ```
   GEMINI_API_KEY = "AIza..."
   ```
4. `secrets.toml` is gitignored — never commit it

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```
Then open http://localhost:8501

## Deploy for free (Streamlit Community Cloud)
1. Push this folder to a new GitHub repo (e.g. `ats-resume-checker`)
   — make sure `.streamlit/secrets.toml` is NOT pushed (it's gitignored)
2. Go to share.streamlit.io, sign in with GitHub
3. Click "New app", select the repo, set main file to `app.py`
4. In the app settings, go to "Secrets" and paste:
   ```
   GEMINI_API_KEY = "AIza..."
   ```
5. Deploy — you get a public URL like `yourapp.streamlit.app`

## Features
- Keyword match score with visual pills
- Formatting/parsing issue detection
- AI section-by-section feedback (Summary, Skills, Experience, Education)
- AI bullet point rewrite suggestions
- AI-generated cover letter (with tone selection)
- Downloadable PDF report

## Next improvements (when you have time)
- Separate project: PDF <-> Word converter and PDF compressor
- Resume vs JD side-by-side text highlighting
- Save/compare multiple job descriptions
- Simple anonymous analytics for usage tracking

