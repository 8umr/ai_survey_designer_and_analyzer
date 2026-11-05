# AI Survey Designer and Analyzer

A comprehensive Streamlit application to design research-backed survey instruments, calculate statistical quantitative metrics, and synthesize qualitative respondent feedback using an AI inference backend.

---

## 🚀 Key Features

1. **Survey Instrument Designer**:
   - Turn research objectives and target audience specifications into structured survey schemas.
   - Generates questions with standardized response types (Likert 1-5, Single Choice, Multiple Choice, Open-ended).
   - Export schemas in JSON or CSV format.

2. **Quantitative Analytics**:
   - Upload survey datasets in CSV or Excel format (or load a built-in sample dataset).
   - Compute descriptive statistics (Mean, Median, Standard Deviation, Ranges) for rating and Likert scales.
   - Interactive distributions and segment boxplots powered by Plotly.

3. **Qualitative Synthesis**:
   - Analyze open-ended free-text responses.
   - Categorize themes, detect sentiment distributions, extract representative verbatim quotes, and generate actionable recommendations.

---

## 📦 Installation & Setup

### 1. Clone or Extract Project
Extract the files into a local folder:
```bash
unzip ai_survey_designer_and_analyzer.zip
cd ai_survey_designer_and_analyzer
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
streamlit run app.py
```

---

## 🔑 Configuration

You can provide your API key in two ways:
- **Interactive Sidebar**: Enter the key directly into the password field inside the application.
- **Environment Variable**: Export your key before launching:
  ```bash
  export AI_API_KEY="your_api_key_here"
  ```

*Endpoint defaults to `https://api.x.ai/v1` with standard models (`grok-beta`, `grok-2-latest`, `grok-2-mini`).*

---

## 📁 File Structure
```
├── app.py              # Main Streamlit web application
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation and guide
```
