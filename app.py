import streamlit as st
from parser_utils import extract_text, clean_text, check_formatting_issues
from matcher import calculate_match
from pdf_report import build_pdf_report
import ai_engine

st.set_page_config(page_title="ATS Resume Checker", page_icon="📄", layout="wide")

# ----------------------------------------------------------------------------
# Custom CSS
# ----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Force light theme regardless of system/browser dark mode */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%) !important;
        color: #1f2937 !important;
    }

    /* Ensure all text defaults to dark, readable color */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
        color: #1f2937;
    }

    /* Text inputs, text areas, file uploader, selectbox */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
    }

    /* File uploader drop area */
    [data-testid="stFileUploaderDropzone"] {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: #1f2937 !important;
    }

    /* Uploaded file name chip */
    [data-testid="stFileUploaderFile"] {
        background-color: #f3f4f6 !important;
        color: #1f2937 !important;
    }

    /* Placeholder text */
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #9ca3af !important;
    }

    /* Tabs text */
    .stTabs [data-baseweb="tab"] {
        color: #1f2937 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #4f46e5 !important;
    }

    /* Mobile responsiveness */
    @media (max-width: 640px) {
        .app-header h1 {
            font-size: 1.7rem;
        }
        .app-header p {
            font-size: 0.9rem;
        }
        .score-circle {
            width: 110px;
            height: 110px;
            font-size: 1.8rem;
        }
        .card {
            padding: 1rem;
        }
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 1100px;
    }

    /* Global fade-in for the whole app */
    .main .block-container {
        animation: fadeInUp 0.5s ease-out;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes popIn {
        0% { opacity: 0; transform: scale(0.85); }
        60% { opacity: 1; transform: scale(1.04); }
        100% { opacity: 1; transform: scale(1); }
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 8px 24px rgba(79, 70, 229, 0.18); }
        50% { box-shadow: 0 8px 36px rgba(124, 58, 237, 0.32); }
    }

    .app-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        animation: fadeInUp 0.6s ease-out;
    }
    .app-header h1 {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4f46e5, #7c3aed, #4f46e5);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        animation: gradientShift 6s ease infinite;
    }
    .app-header p {
        color: #6b7280;
        font-size: 1.05rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 24px rgba(79, 70, 229, 0.06);
        border: 1px solid #eef0f6;
        margin-bottom: 1.2rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        animation: fadeInUp 0.5s ease-out;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 32px rgba(79, 70, 229, 0.12);
    }

    .score-wrap {
        text-align: center;
        padding: 1.5rem 0;
    }
    .score-circle {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.8rem auto;
        font-size: 2.6rem;
        font-weight: 800;
        color: white;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        animation: popIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1), pulseGlow 3s ease-in-out infinite;
    }
    .verdict {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 0.4rem;
        animation: fadeIn 0.8s ease-out 0.2s both;
    }

    .pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.82rem;
        margin: 3px;
        font-weight: 500;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        animation: fadeIn 0.5s ease-out both;
    }
    .pill:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .pill-found {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    .pill-missing {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }

    .section-card {
        border-left: 4px solid #d1d5db;
        background: #f9fafb;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.7rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: fadeInUp 0.4s ease-out both;
    }
    .section-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }
    .section-card.strong { border-left-color: #16a34a; }
    .section-card.needs_work { border-left-color: #d97706; }
    .section-card.missing { border-left-color: #dc2626; }

    .section-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.2rem;
    }
    .badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 9px;
        border-radius: 999px;
        margin-left: 8px;
        vertical-align: middle;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        animation: popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) both;
    }
    .badge.strong { background: #dcfce7; color: #166534; }
    .badge.needs_work { background: #fef3c7; color: #92400e; }
    .badge.missing { background: #fee2e2; color: #991b1b; }

    .rewrite-card {
        background: #f9fafb;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border: 1px solid #eef0f6;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        animation: fadeInUp 0.4s ease-out both;
    }
    .rewrite-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.08);
        border-color: #c7d2fe;
    }
    .rewrite-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 2px;
    }
    .rewrite-original { color: #b91c1c; }
    .rewrite-improved { color: #15803d; }
    .rewrite-why {
        color: #6b7280;
        font-size: 0.85rem;
        font-style: italic;
        margin-top: 4px;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.18);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        background-size: 150% auto;
        border: none;
        transition: background-position 0.4s ease, transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background-position: 100% 0;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3);
    }

    /* Download buttons */
    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.15);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(79, 70, 229, 0.06);
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #4f46e5 !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        animation: fadeIn 0.4s ease-out;
    }

    /* Input focus glow */
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.18) !important;
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown("""
<div class="app-header">
    <h1>📄 AI ATS Resume Checker</h1>
    <p>Upload your resume, paste a job description, and get an AI-powered breakdown
    of your match score, missing keywords, section feedback, and rewrite suggestions.</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("1. Upload your resume")
    resume_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("2. Paste the job description")
    jd_text = st.text_area("Job description", height=200, placeholder="Paste the full job description here...")
    company_name = st.text_input("Company name (optional, for cover letter)", placeholder="e.g. Acme Corp")
    st.markdown('</div>', unsafe_allow_html=True)

run_ai = st.checkbox("Include AI-powered analysis (section feedback, rewrites, cover letter)", value=True)

analyze = st.button("Analyze", type="primary")

# ----------------------------------------------------------------------------
# Analysis
# ----------------------------------------------------------------------------
if analyze:
    if not resume_file:
        st.error("Please upload your resume.")
    elif not jd_text.strip():
        st.error("Please paste a job description.")
    else:
        try:
            resume_file.seek(0)
            raw_text = extract_text(resume_file, resume_file.name)

            if not raw_text.strip():
                st.error("Couldn't extract any text from this file. It may be an image-based/scanned document.")
            else:
                resume_clean = clean_text(raw_text)
                jd_clean = clean_text(jd_text)

                with st.spinner("Calculating keyword match..."):
                    result = calculate_match(resume_clean, jd_clean)

                resume_file.seek(0)
                formatting_issues = check_formatting_issues(resume_file, resume_file.name, raw_text)

                ai_sections = None
                ai_rewrites = None
                ai_error = None

                if run_ai:
                    try:
                        with st.spinner("Running AI section analysis..."):
                            ai_sections = ai_engine.analyze_resume_sections(raw_text, jd_text)
                        with st.spinner("Generating rewrite suggestions..."):
                            ai_rewrites = ai_engine.suggest_bullet_rewrites(raw_text, jd_text)
                    except Exception as e:
                        ai_error = str(e)

                st.session_state["raw_text"] = raw_text
                st.session_state["jd_text"] = jd_text
                st.session_state["company_name"] = company_name
                st.session_state["result"] = result
                st.session_state["formatting_issues"] = formatting_issues
                st.session_state["ai_sections"] = ai_sections
                st.session_state["ai_rewrites"] = ai_rewrites
                st.session_state["ai_error"] = ai_error
                st.session_state["analyzed"] = True
                st.session_state["cover_letter"] = None
                st.session_state["pdf_bytes"] = None

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Something went wrong while processing your file: {e}")

# ----------------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------------
if st.session_state.get("analyzed"):
    result = st.session_state["result"]
    formatting_issues = st.session_state["formatting_issues"]
    ai_sections = st.session_state.get("ai_sections")
    ai_rewrites = st.session_state.get("ai_rewrites")
    ai_error = st.session_state.get("ai_error")
    raw_text = st.session_state["raw_text"]
    jd_text_saved = st.session_state["jd_text"]
    company_name_saved = st.session_state.get("company_name")

    st.divider()

    score = result["score"]
    if score >= 75:
        circle_color = "#16a34a"
        verdict = "Strong match"
        verdict_color = "#16a34a"
    elif score >= 50:
        circle_color = "#d97706"
        verdict = "Moderate match — some improvements needed"
        verdict_color = "#d97706"
    else:
        circle_color = "#dc2626"
        verdict = "Weak match — significant gaps"
        verdict_color = "#dc2626"

    st.markdown(f"""
    <div class="card score-wrap">
        <div class="score-circle" style="background: {circle_color};">{score}%</div>
        <div class="verdict" style="color: {verdict_color};">{verdict}</div>
    </div>
    """, unsafe_allow_html=True)

    if ai_error:
        st.warning(f"AI analysis unavailable: {ai_error}")

    tab_names = ["Keywords", "Formatting"]
    if ai_sections:
        tab_names.append("AI Section Feedback")
    if ai_rewrites:
        tab_names.append("Rewrite Suggestions")
    tab_names.append("Cover Letter")
    tab_names.append("Download Report")

    tabs = st.tabs(tab_names)
    tab_map = dict(zip(tab_names, tabs))

    with tab_map["Keywords"]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ✅ Found in your resume")
            if result["matched"]:
                pills = "".join(
                    f'<span class="pill pill-found" style="animation-delay:{i*0.04}s">{kw}</span>'
                    for i, kw in enumerate(result["matched"])
                )
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.write("None found.")
        with c2:
            st.markdown("#### ❌ Missing from your resume")
            if result["missing"]:
                pills = "".join(
                    f'<span class="pill pill-missing" style="animation-delay:{i*0.04}s">{kw}</span>'
                    for i, kw in enumerate(result["missing"])
                )
                st.markdown(pills, unsafe_allow_html=True)
                st.caption("Consider naturally incorporating these terms if they reflect your real skills/experience.")
            else:
                st.write("Great — no major gaps found!")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_map["Formatting"]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if formatting_issues:
            for issue in formatting_issues:
                st.warning(issue)
        else:
            st.success("No major formatting issues detected.")
        st.markdown('</div>', unsafe_allow_html=True)

    if ai_sections:
        with tab_map["AI Section Feedback"]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"**Overall summary:** {ai_sections.get('overall_summary', '')}")
            st.markdown("---")
            for i, sec in enumerate(ai_sections.get("sections", [])):
                rating = sec.get("rating", "needs_work")
                badge_label = {"strong": "Strong", "needs_work": "Needs Work", "missing": "Missing"}.get(rating, rating)
                st.markdown(f"""
                <div class="section-card {rating}" style="animation-delay:{i*0.08}s">
                    <span class="section-title">{sec.get('section_name', '')}</span>
                    <span class="badge {rating}">{badge_label}</span>
                    <div style="margin-top: 6px; color: #4b5563; font-size: 0.9rem;">{sec.get('feedback', '')}</div>
                </div>
                """, unsafe_allow_html=True)

            if ai_sections.get("top_priorities"):
                st.markdown("#### 🎯 Top priorities")
                for i, item in enumerate(ai_sections["top_priorities"], 1):
                    st.markdown(f"{i}. {item}")
            st.markdown('</div>', unsafe_allow_html=True)

    if ai_rewrites:
        with tab_map["Rewrite Suggestions"]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            rewrites = ai_rewrites.get("rewrites", [])
            if rewrites:
                for i, r in enumerate(rewrites):
                    st.markdown(f"""
                    <div class="rewrite-card" style="animation-delay:{i*0.08}s">
                        <div class="rewrite-label rewrite-original">Original</div>
                        <div>{r.get('original', '')}</div>
                        <div class="rewrite-label rewrite-improved" style="margin-top:8px;">Improved</div>
                        <div>{r.get('improved', '')}</div>
                        <div class="rewrite-why">{r.get('why', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No major rewrite suggestions — your bullets already look solid!")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_map["Cover Letter"]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        tone = st.selectbox("Tone", ["professional", "enthusiastic", "concise"], key="cl_tone")
        if st.button("Generate cover letter", key="gen_cl"):
            try:
                with st.spinner("Writing cover letter..."):
                    letter = ai_engine.generate_cover_letter(
                        raw_text, jd_text_saved, company_name_saved, tone
                    )
                st.session_state["cover_letter"] = letter
            except Exception as e:
                st.error(f"Couldn't generate cover letter: {e}")

        if st.session_state.get("cover_letter"):
            st.text_area("Generated cover letter", st.session_state["cover_letter"], height=350)
            st.download_button(
                "Download as .txt",
                st.session_state["cover_letter"],
                file_name="cover_letter.txt",
                mime="text/plain",
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_map["Download Report"]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("Generate a PDF summary of this analysis to save or share.")
        if st.button("Generate PDF report"):
            with st.spinner("Building PDF..."):
                pdf_bytes = build_pdf_report(result, formatting_issues, ai_sections, ai_rewrites)
            st.session_state["pdf_bytes"] = pdf_bytes

        if st.session_state.get("pdf_bytes"):
            st.download_button(
                "Download PDF report",
                st.session_state["pdf_bytes"],
                file_name="ats_resume_report.pdf",
                mime="application/pdf",
            )
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.caption(
    "Note: This tool gives an estimate based on keyword matching and AI analysis, "
    "similar to how many ATS systems scan resumes. It does not guarantee how a "
    "specific employer's ATS will score your resume."
)