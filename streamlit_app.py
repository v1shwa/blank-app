import streamlit as st
import json
import requests

st.set_page_config(page_title="AI Theme Generator", page_icon="🎈")

st.title("🤖 AI Theme Generator")
# st.markdown(
#     "Configure an interview session by providing the Job Description, duration, and required skills."
# )

# ── Section 1: Job Description ──────────────────────────────────────────────
st.header("📋 Job Description")
jd_text = st.text_area(
    "Paste the full Job Description here",
    height=200,
    placeholder="e.g. We are looking for a Senior ML Engineer with experience in LLM fine-tuning, RAG pipelines...",
)

# ── Section 2: Interview Duration ───────────────────────────────────────────
st.header("⏱️ Interview Duration")
interview_duration_minutes = st.number_input(
    "Duration (in minutes)",
    min_value=10,
    max_value=180,
    value=45,
    step=5,
    help="Typical interviews range from 30 to 90 minutes.",
)

# ── Section 3: Skills ────────────────────────────────────────────────────────
st.header("🛠️ Skills")
st.markdown(
    "Provide skills as a **JSON array**. Each skill object must have `skill`, `type` (`mandatory` or `preferred`), and `context (optional)`."
)

skills_example = json.dumps(
    [
        {
            "skill": "Python",
            "type": "mandatory",
            "context": "Core backend development and ML scripting",
        },
        {
            "skill": "LangChain",
            "type": "preferred",
            "context": "Building LLM-based RAG pipelines",
        },
        {
            "skill": "System Design",
            "type": "mandatory",
            "context": "Designing scalable AI inference systems",
        },
    ],
    indent=2,
)

skills_json_input = st.text_area(
    "Skills (JSON list)",
    value=skills_example,
    height=250,
    help="Each object: { skill, type: mandatory|preferred, context }",
)

# ── Parse & Validate Skills ──────────────────────────────────────────────────
skills = []
skills_valid = False
try:
    parsed = json.loads(skills_json_input)
    if not isinstance(parsed, list):
        st.error("❌ Skills must be a JSON **array** (list).")
    else:
        required_keys = {"skill", "type"}
        errors = []
        for i, item in enumerate(parsed):
            missing = required_keys - item.keys()
            if missing:
                errors.append(f"Item {i+1} is missing keys: {missing}")
            if item.get("type") not in ("mandatory", "preferred"):
                errors.append(
                    f"Item {i+1}: `type` must be 'mandatory' or 'preferred', got '{item.get('type')}'"
                )
        if errors:
            for e in errors:
                st.warning(f"⚠️ {e}")
        else:
            skills = parsed
            skills_valid = True
            st.success(f"✅ {len(skills)} skill(s) parsed successfully.")
except json.JSONDecodeError as e:
    st.error(f"❌ Invalid JSON: {e}")

# # ── Skills Preview Table ─────────────────────────────────────────────────────
# if skills_valid and skills:
#     st.subheader("Skills Preview")
#     col_headers = st.columns([2, 1.5, 4])
#     col_headers[0].markdown("**Skill**")
#     col_headers[1].markdown("**Type**")
#     col_headers[2].markdown("**Context**")
#     st.divider()
#     for s in skills:
#         cols = st.columns([2, 1.5, 4])
#         cols[0].write(s["skill"])
#         badge = "🔴 Mandatory" if s["type"] == "mandatory" else "🟡 Preferred"
#         cols[1].write(badge)
#         cols[2].write(s.get("context", "—"))

# ── Submit ───────────────────────────────────────────────────────────────────
# st.divider()
submit = st.button(
    "🚀 Generate Interview Plan", type="primary", disabled=not skills_valid
)

if submit:
    if not jd_text.strip():
        st.error("❌ Please enter a Job Description before submitting.")
    else:
        payload = {
            "jd_text": jd_text,
            "interview_duration_minutes": interview_duration_minutes,
            "skills": skills,
        }

        with st.spinner("⏳ Generating themes..."):
            try:
                response = requests.post(
                    "https://arya-ai.up.railway.app/api/v1/themes/generate",
                    json=payload,
                    timeout=30,
                )
                response.raise_for_status()
                result = response.json()

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Could not connect to the backend at `127.0.0.1:8000`. Make sure the server is running."
                )
                st.stop()
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. The server took too long to respond.")
                st.stop()
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Server returned an error: {e}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")
                st.stop()

        # ── Display Themes Table ─────────────────────────────────────────────
        themes = result.get("themes", [])
        count = result.get("count", len(themes))

        st.success(f"✅ {count} interview theme(s) generated!")
        st.subheader("🎯 Interview Themes")

        # Table header
        hcols = st.columns([0.5, 3, 1.5, 4])
        hcols[0].markdown("**#**")
        hcols[1].markdown("**Theme Name**")
        hcols[2].markdown("**Type**")
        hcols[3].markdown("**Skills Covered**")
        st.divider()

        for theme in themes:
            row = st.columns([0.5, 3, 1.5, 4])
            row[0].write(theme.get("theme_id", "—"))
            row[1].write(theme.get("label", "—"))
            t_type = theme.get("type", "")
            row[2].write("🔴 Mandatory" if t_type == "mandatory" else "🟡 Preferred")
            skills_list = theme.get("skills", [])
            row[3].write(", ".join(skills_list))
