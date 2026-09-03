# Prompt Optimizer AI 🚀

A modern, full-stack prompt engineering dashboard that elevates simple, vague drafts into detailed, highly effective, and structured prompts optimized specifically for leading AI models (ChatGPT, Gemini, Claude, Midjourney, DALL·E, and GitHub Copilot).

---

## 📸 Overview
Prompt Optimizer AI evaluates input prompt drafts locally, utilizes the **Google Gemini API** to optimize context, constraints, tone, and formatting, and ranks quality upgrades dynamically. Users can visualize before-and-after improvements, inspect metric breakdowns, export printable PDF/TXT reports, and track past entries in a local SQLite history module.

---

## ✨ Features
1. **Interactive Prompt Drafting**: Input vague prompts (e.g., *"Write a resume"*).
2. **AI Model Targeting**: Custom prompt optimizations specific to models like ChatGPT, Gemini, Midjourney, etc.
3. **Multi-Parameter Optimization**: Fine-tune Tone (Professional, Friendly, Technical, etc.), Category, and output length targets.
4. **Before-and-After Analysis**: Displays original vs. optimized prompts side-by-side.
5. **Quality Metric Breakdown**: Standard progress meters scoring prompt *Clarity*, *Context*, *Specificity*, *Structure*, and *Completeness* from 0 to 100.
6. **"Why It Is Better" Accordion**: In-depth checklist detailing exact formatting, constraint, and objective adjustments.
7. **One-Click Actions**:
   - 📋 Copy prompt to clipboard (supports custom browser-safe JS clipboard copying).
   - 💾 Download as standard plain-text report.
   - 📄 Download as a structured, print-ready PDF document.
   - ⭐ Mark items as favorites.
8. **Pre-defined Templates Sidebar**: 12+ preset templates across categories like coding, SQL query, presentation, and marketing to test instantly.
9. **SQLite Prompt History**: Retrieve, search, favorite, load back into workspace, or delete past optimizations.
10. **Statistics Dashboard**: Monitor metrics such as total prompts optimized, category preferences, average scores, and volume trends over time.

---

## 🛠️ Technologies Used
- **Frontend/UI**: [Streamlit](https://streamlit.io/) (Python Web App Framework)
- **AI Core**: [Google Gemini API](https://ai.google.dev/) (SDK: `google-generativeai`)
- **Database**: SQLite3 (Local file-based SQL store)
- **Analytics**: Pandas (Aggregations and dataframes)
- **Document Export**: ReportLab (High-fidelity PDF document creation)
- **Styling**: Custom CSS overrides (Glassmorphism, linear-gradients, dark theme cards)

---

## 📂 Folder Structure
```
anti-gravity/
│
├── app.py                  # Main Streamlit orchestration file
├── optimizer.py            # Gemini API prompt optimizer & mock fallback service
├── database.py             # SQLite helper functions for history & stats
├── utils.py                # Plain text & ReportLab PDF exporter utilities
├── templates.py            # Preset templates for categories in the sidebar
├── prompt_scorer.py        # Local rule-based analyzer for initial drafts
├── test_modules.py        # Local unit tests checking SQLite, Scorers, Exporters
├── requirements.txt        # Third-party package dependencies
├── assets/                 # Custom static style layouts
│   └── style.css           # Premium glassmorphism design parameters
└── database/               # Created at runtime to hold SQLite database
    └── history.db
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
Navigate to your desired folder location on your machine:
```bash
cd C:\Users\new\OneDrive\Desktop\anti-gravity
```

### 2. Set up virtual environment (Optional)
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install required packages
Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### 4. Provide Gemini API Key (Optional)
You can set your API key as an environment variable:
```bash
# On Windows PowerShell:
$env:GEMINI_API_KEY="your_api_key_here"

# On CMD:
set GEMINI_API_KEY=your_api_key_here
```
*Note: If no API key is specified, the application will automatically fall back to the built-in Smart Mock Optimizer, allowing you to test the full range of frontend features without any configuration!*

### 5. Launch the Application
Start the Streamlit development server:
```bash
streamlit run app.py
```

---

## 🧪 Verification & Testing
To execute backend verification checks:
```bash
python test_modules.py
```
This tests scoring logic, database operations, mock fallbacks, and PDF report compilation.

---

## 🚀 Future Enhancements
- **Multi-language support**: Allow optimization and output in languages like Spanish, French, and Japanese.
- **Voice-to-text integration**: Live Web Audio API integration for standard dictation.
- **AI Suggestions preview**: Real-time auto-complete suggestions as the user drafts prompts.
- **Prompt Share**: Quick web link generation to share optimized prompts.

---

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
