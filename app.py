import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from openai import OpenAI

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Survey Designer & Analyzer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 1rem;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar: API Key & Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key_input = st.text_input(
        "API Key",
        type="password",
        value=os.getenv("AI_API_KEY", ""),
        help="Enter your API key here (compatible with xAI / OpenAI-compatible endpoint)."
    )
    
    base_url = st.text_input(
        "Base URL",
        value="https://api.x.ai/v1",
        help="Base endpoint URL"
    )
    
    model_name = st.selectbox(
        "Model",
        options=["grok-beta", "grok-2-latest", "grok-2-mini"],
        index=0
    )
    
    st.markdown("---")
    st.info("💡 **Tip:** Formulate specific research objectives for high-quality survey instruments.")

# Helper to initialize client
def get_ai_client():
    if not api_key_input:
        return None
    return OpenAI(api_key=api_key_input, base_url=base_url)

# ---------------------------------------------------------
# Main App Header
# ---------------------------------------------------------
st.markdown('<div class="main-title">📋 AI Survey Designer & Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Generate targeted survey questions from research goals, analyze responses with statistics, and extract qualitative feedback insights.</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎯 1. Design Survey", "📊 2. Quantitative Analytics", "💬 3. Qualitative Insights"])

# ---------------------------------------------------------
# Tab 1: Survey Design
# ---------------------------------------------------------
with tab1:
    st.subheader("Generate Survey from Research Objective")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        research_objective = st.text_area(
            "Research Objective / Topic",
            placeholder="e.g., Evaluate user satisfaction with our new mobile banking app onboarding flow and identify onboarding friction points.",
            height=120
        )
    with col2:
        target_audience = st.text_input("Target Audience", placeholder="e.g., Tech-savvy young adults (18-35)")
        num_questions = st.slider("Number of Questions", min_value=3, max_value=15, value=6)
        include_demographics = st.checkbox("Include Demographic Questions", value=True)

    if st.button("Generate Survey Schema", type="primary"):
        client = get_ai_client()
        if not client:
            st.error("Please enter a valid API key in the sidebar.")
        elif not research_objective.strip():
            st.warning("Please provide a research objective.")
        else:
            with st.spinner("Drafting survey questions and response structures..."):
                prompt = f"""
You are an expert survey methodologist and research designer.
Create a structured survey based on:
- Research Objective: {research_objective}
- Target Audience: {target_audience if target_audience else 'General public'}
- Total Questions: {num_questions}
- Include Demographics: {include_demographics}

Return your answer strictly in valid JSON with this format:
{{
  "survey_title": "Title of survey",
  "survey_description": "Brief description for respondents",
  "questions": [
    {{
      "id": "Q1",
      "text": "Question text here?",
      "type": "Likert (1-5)" | "Single Choice" | "Multiple Choice" | "Open-ended" | "Numerical",
      "options": ["Option 1", "Option 2"] or null,
      "purpose": "Why this question was included"
    }}
  ]
}}
"""
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "You are a professional survey designer that outputs strictly valid JSON without markdown wrapping."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3
                    )
                    content = response.choices[0].message.content.strip()
                    # Clean markdown if present
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                    
                    survey_data = json.loads(content.strip())
                    st.session_state["generated_survey"] = survey_data
                    st.success("Survey generated successfully!")
                except Exception as e:
                    st.error(f"Error generating survey: {str(e)}")

    if "generated_survey" in st.session_state:
        survey = st.session_state["generated_survey"]
        st.markdown(f"### {survey.get('survey_title', 'Generated Survey')}")
        st.write(survey.get("survey_description", ""))
        
        q_list = []
        for q in survey.get("questions", []):
            opts = ", ".join(q["options"]) if q.get("options") else "N/A"
            q_list.append({
                "ID": q.get("id"),
                "Question": q.get("text"),
                "Type": q.get("type"),
                "Options": opts,
                "Measurement Rationale": q.get("purpose")
            })
            
        df_questions = pd.DataFrame(q_list)
        st.dataframe(df_questions, use_container_width=True)
        
        # Download schema
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📥 Download Survey Schema (JSON)",
                data=json.dumps(survey, indent=2),
                file_name="survey_instrument.json",
                mime="application/json"
            )
        with col_d2:
            st.download_button(
                label="📥 Download Questions (CSV)",
                data=df_questions.to_csv(index=False).encode("utf-8"),
                file_name="survey_questions.csv",
                mime="text/csv"
            )

# ---------------------------------------------------------
# Tab 2: Quantitative Analytics
# ---------------------------------------------------------
with tab2:
    st.subheader("Quantitative Statistics & Visualizations")
    
    uploaded_file = st.file_uploader("Upload Survey Responses (CSV or Excel)", type=["csv", "xlsx"], key="quant_upload")
    
    # Option to generate sample data
    if st.button("Generate & Load Sample Dataset"):
        np.random.seed(42)
        n = 120
        sample_df = pd.DataFrame({
            "Respondent_ID": [f"RESP_{i+1:03d}" for i in range(n)],
            "Age_Group": np.random.choice(["18-24", "25-34", "35-44", "45-54", "55+"], n, p=[0.2, 0.35, 0.25, 0.12, 0.08]),
            "Overall_Satisfaction": np.random.choice([1, 2, 3, 4, 5], n, p=[0.05, 0.10, 0.20, 0.45, 0.20]),
            "Ease_of_Use": np.random.choice([1, 2, 3, 4, 5], n, p=[0.03, 0.07, 0.25, 0.40, 0.25]),
            "Feature_Utility": np.random.choice([1, 2, 3, 4, 5], n, p=[0.08, 0.12, 0.30, 0.35, 0.15]),
            "Net_Promoter_Score": np.random.randint(1, 11, n),
            "Feedback_Comments": np.random.choice([
                "Loved the clean interface and fast checkout experience.",
                "Navigation feels unintuitive on small screens. Needs improvement.",
                "Customer support responded within minutes, very impressive!",
                "Prices are a bit high compared to competitors.",
                "The app crashes occasionally during payment verification.",
                "Overall good, but search filters should be more granular.",
                "Fantastic updates recently, highly recommended!"
            ], n)
        })
        st.session_state["survey_data"] = sample_df
        st.success("Sample dataset with 120 respondents loaded!")

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state["survey_data"] = df
            st.success(f"Loaded {uploaded_file.name} successfully!")
        except Exception as e:
            st.error(f"Error loading file: {e}")

    if "survey_data" in st.session_state:
        df = st.session_state["survey_data"]
        
        st.markdown("#### Response Preview")
        st.dataframe(df.head(6), use_container_width=True)
        
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        
        st.markdown("---")
        st.markdown("#### Summary Metrics")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Total Responses", len(df))
        m_col2.metric("Total Variables", len(df.columns))
        m_col3.metric("Numeric Scales", len(num_cols))
        m_col4.metric("Categorical/Text", len(cat_cols))

        if num_cols:
            st.markdown("#### Descriptive Statistics (Numeric & Likert Scales)")
            stats_df = df[num_cols].describe().T[["mean", "std", "min", "50%", "max"]]
            stats_df.columns = ["Mean", "Std Dev", "Min", "Median (50%)", "Max"]
            st.dataframe(stats_df.round(2), use_container_width=True)
            
            st.markdown("#### Data Visualizations")
            vcol1, vcol2 = st.columns(2)
            with vcol1:
                selected_num = st.selectbox("Select Numeric Metric to Plot", num_cols, index=0)
                fig_hist = px.histogram(
                    df,
                    x=selected_num,
                    nbins=10,
                    title=f"Distribution of {selected_num}",
                    color_discrete_sequence=["#3B82F6"]
                )
                fig_hist.update_layout(bargap=0.1)
                st.plotly_chart(fig_hist, use_container_width=True)
                
            with vcol2:
                if cat_cols:
                    selected_cat = st.selectbox("Segment By (Categorical)", cat_cols, index=0)
                    fig_box = px.box(
                        df,
                        x=selected_cat,
                        y=selected_num,
                        title=f"{selected_num} by {selected_cat}",
                        color=selected_cat
                    )
                    st.plotly_chart(fig_box, use_container_width=True)
                else:
                    st.info("No categorical columns available for segmentation.")
        else:
            st.warning("No numeric columns detected for statistical computation.")

# ---------------------------------------------------------
# Tab 3: Qualitative Analysis
# ---------------------------------------------------------
with tab3:
    st.subheader("Qualitative Analysis & Feedback Synthesis")
    
    if "survey_data" not in st.session_state:
        st.info("Please upload a dataset or load the sample dataset in Tab 2 to perform qualitative analysis.")
    else:
        df = st.session_state["survey_data"]
        text_cols = df.select_dtypes(include=["object"]).columns.tolist()
        
        if not text_cols:
            st.warning("No text columns found in the loaded dataset.")
        else:
            selected_text_col = st.selectbox("Select Open-Ended / Feedback Column", text_cols)
            
            sample_size = st.slider("Sample responses to analyze", min_value=10, max_value=min(200, len(df)), value=min(50, len(df)))
            
            if st.button("Synthesize & Extract Themes", type="primary"):
                client = get_ai_client()
                if not client:
                    st.error("Please enter a valid API key in the sidebar.")
                else:
                    feedback_items = df[selected_text_col].dropna().astype(str).tolist()[:sample_size]
                    feedback_text = "\n- ".join(feedback_items)
                    
                    with st.spinner("Analyzing sentiments, themes, and executive action items..."):
                        analysis_prompt = f"""
You are a qualitative research specialist and data analyst.
Analyze the following user feedback responses collected from a survey:

Responses:
- {feedback_text}

Provide a comprehensive qualitative synthesis with:
1. **Executive Summary**: Core sentiment and overarching narrative.
2. **Top Key Themes & Recurring Issues**: Categorize into 3-5 distinct themes with frequency perception (High/Medium/Low).
3. **Sentiment Distribution Estimate**: Breakdown (Positive %, Neutral %, Negative %).
4. **Representative Quotes**: Select 3 notable quotes that highlight critical insights.
5. **Actionable Recommendations**: Bulleted, prioritized steps for product and service improvement.
"""
                        try:
                            response = client.chat.completions.create(
                                model=model_name,
                                messages=[
                                    {"role": "system", "content": "You are an expert qualitative research analyst."},
                                    {"role": "user", "content": analysis_prompt}
                                ],
                                temperature=0.2
                            )
                            analysis_result = response.choices[0].message.content
                            st.session_state["qual_analysis"] = analysis_result
                            st.success("Analysis complete!")
                        except Exception as e:
                            st.error(f"Error conducting qualitative analysis: {str(e)}")
                            
            if "qual_analysis" in st.session_state:
                st.markdown("### 📝 Qualitative Insights Report")
                st.markdown(st.session_state["qual_analysis"])
                
                st.download_button(
                    label="📥 Download Qualitative Report (Markdown)",
                    data=st.session_state["qual_analysis"],
                    file_name="qualitative_survey_analysis.md",
                    mime="text/markdown"
                )
