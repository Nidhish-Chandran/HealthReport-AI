import json
import streamlit as st
from agent import run_health_report_agent

st.set_page_config(
    page_title="HealthReport AI",
    page_icon="🩺",
    layout="wide",
)

st.markdown("""
<style>
    .hero {
        padding: 28px 30px;
        border-radius: 18px;
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: white;
        margin-bottom: 24px;
    }
    .hero h1 { margin: 0; font-size: 42px; }
    .hero p { margin: 8px 0 0; color: #cbd5e1; font-size: 17px; }
    .step {
        padding: 14px;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background: #f8fafc;
        text-align: center;
    }
    .normal { color: #15803d; font-weight: 800; }
    .attention { color: #b45309; font-weight: 800; }
    .unknown { color: #64748b; font-weight: 800; }
    .disclaimer {
        padding: 16px;
        border-radius: 12px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #7c2d12;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🩺 HealthReport AI</h1>
    <p>Agentic AI-powered laboratory report analysis and health information assistant</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🤖 Agent Workflow")
    st.write("**1. Extraction Agent**")
    st.caption("Reads the uploaded laboratory report.")
    st.write("**2. Parameter Agent**")
    st.caption("Identifies test names, values, units and ranges.")
    st.write("**3. Analysis Agent**")
    st.caption("Classifies values using the report's own ranges.")
    st.write("**4. Explanation Agent**")
    st.caption("Creates an easy-to-understand educational summary.")
    st.divider()
    st.caption("Academic prototype — not a diagnostic system.")

st.subheader("Upload Laboratory Report")
uploaded = st.file_uploader(
    "Choose a text-based PDF laboratory report",
    type=["pdf"],
    help="Use a PDF containing selectable text for this one-day prototype.",
)

if uploaded:
    st.success(f"✓ {uploaded.name}")

    if st.button("🚀 Analyze Report", type="primary", use_container_width=True):
        progress = st.progress(0, text="Starting HealthReport AI...")

        try:
            progress.progress(15, text="Agent 1/4 — extracting report text...")
            result = run_health_report_agent(
                uploaded.getvalue(),
                progress_callback=lambda value, message: progress.progress(value, text=message)
            )
            progress.progress(100, text="Analysis completed.")
            st.session_state["result"] = result
        except Exception as e:
            progress.empty()
            st.error(f"Analysis failed: {e}")

if "result" in st.session_state:
    result = st.session_state["result"]

    if result.get("error"):
        st.error(result["error"])
        st.stop()

    st.divider()
    st.subheader("📊 Report Overview")

    params = result.get("parameters", [])
    attention = sum(1 for p in params if p.get("status") in ["Low", "High"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Parameters", len(params))
    c2.metric("Needs Attention", attention)
    c3.metric("Overall Status", result.get("overall_status", "Review"))

    st.subheader("🧪 Laboratory Results")

    if not params:
        st.warning("No laboratory parameters were confidently identified.")
    else:
        for p in params:
            status = p.get("status", "Unknown")
            css = "normal" if status == "Normal" else "attention" if status in ["Low", "High"] else "unknown"

            with st.container(border=True):
                a, b, c, d = st.columns([2.1, 1.3, 2.0, 1.0])
                a.markdown(f"**{p.get('name', 'Unknown')}**")
                b.write(f"{p.get('value', 'N/A')} {p.get('unit', '')}")
                c.write(p.get("reference_range", "Not available"))
                d.markdown(f'<span class="{css}">{status}</span>', unsafe_allow_html=True)

                if p.get("explanation"):
                    st.caption(p["explanation"])

    st.subheader("🧠 AI Summary")
    st.info(result.get("summary", "No summary generated."))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔎 Key Observations")
        for item in result.get("key_observations", []):
            st.write(f"• {item}")

    with col2:
        st.markdown("#### 💡 General Guidance")
        for item in result.get("general_guidance", []):
            st.write(f"• {item}")

    st.subheader("⚙️ Agent Execution")
    steps = [
        ("1", "Document Extraction", "Text extracted from PDF"),
        ("2", "Parameter Identification", "Tests and values identified"),
        ("3", "Range Analysis", "Values compared with report ranges"),
        ("4", "Health Explanation", "Educational summary generated"),
    ]
    cols = st.columns(4)
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f'<div class="step"><b>{num}. {title}</b><br><small>{desc}</small></div>',
                unsafe_allow_html=True
            )

    download_data = json.dumps(result, indent=2)
    st.download_button(
        "⬇️ Download Analysis JSON",
        data=download_data,
        file_name="healthreport_analysis.json",
        mime="application/json",
    )

    st.markdown("---")
    st.markdown("""
    <div class="disclaimer">
    <b>Medical safety notice:</b> HealthReport AI is an educational prototype.
    It does not diagnose diseases, prescribe medicines, or replace a healthcare
    professional. Reference ranges differ between laboratories and individuals.
    Always use the reference range printed on the original report and seek
    professional medical advice for clinical decisions.
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Upload a laboratory PDF and click Analyze Report to start.")
