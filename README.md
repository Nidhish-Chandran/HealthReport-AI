# 🩺 HealthReport AI

**HealthReport AI** is an agentic AI-powered web application that analyzes laboratory reports and generates an easy-to-understand educational summary using the **Google Gemini API**.

The application extracts laboratory parameters from uploaded PDF reports, compares numerical values with the reference ranges provided in the report, classifies the results as **Normal, Low, High, or Unknown**, and uses Gemini to generate a concise explanation.

> **Disclaimer:** This project is an academic prototype. It is not a medical diagnostic system and must not be used to make medical or treatment decisions.

## ✨ Features

* 📄 Upload laboratory reports in PDF format
* 🔍 Extract text using PyMuPDF
* 🤖 Gemini-powered parameter extraction
* 🧠 Agentic multi-stage analysis workflow
* 📊 Compare values with report-specific reference ranges
* 🟢 Normal / 🟠 High / 🔵 Low / Unknown classification
* 💬 AI-generated educational explanation
* 📋 Key observations and general guidance
* 📥 Download analysis results as JSON
* 🌐 Interactive Streamlit web interface
* 🔐 API key stored using environment variables

## 🏗️ Agentic Architecture

```text
                    USER
                     │
                     ▼
            Upload Laboratory PDF
                     │
                     ▼
        ┌──────────────────────────┐
        │  Document Extraction     │
        │  Agent / PyMuPDF         │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │  Parameter Extraction    │
        │  Gemini AI Agent         │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │ Reference Range Analysis │
        │ Deterministic Python Tool│
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │ Explanation Agent        │
        │ Gemini AI                │
        └────────────┬─────────────┘
                     │
                     ▼
              Streamlit Dashboard
```

### Agent Workflow

1. **Document Extraction** — Extracts readable text from the uploaded laboratory PDF.
2. **Parameter Extraction Agent** — Gemini identifies laboratory test names, values, units, and reference ranges.
3. **Reference-Range Analysis Tool** — Python performs numerical comparison.
4. **Explanation Agent** — Gemini generates an educational summary.
5. **Dashboard** — Streamlit displays the structured results.

## 🛠️ Technology Stack

| Technology        | Purpose                         |
| ----------------- | ------------------------------- |
| Python            | Core application logic          |
| Streamlit         | Web interface                   |
| Google Gemini API | AI agents and explanation       |
| Google GenAI SDK  | Gemini API integration          |
| PyMuPDF           | PDF text extraction             |
| Pydantic          | Structured AI responses         |
| python-dotenv     | Environment variable management |

## 📁 Project Structure

```text
HealthReportAI/
│
├── app.py
├── agent.py
├── requirements.txt
├── .env.example
├── .gitignore
├── sample_report.pdf
└── README.md
```

## 🚀 Installation

```bash
git clone https://github.com/YOUR_USERNAME/HealthReportAI.git
cd HealthReportAI
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 🔑 Gemini API Configuration

Create a Gemini API key using Google AI Studio.

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.6-flash
```

**Never commit your `.env` file or expose your API key publicly.**

## ▶️ Run the Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## 🧪 Demo

The repository includes:

```text
sample_report.pdf
```

Upload it through the web interface and click **Analyze Report**.

The sample contains normal, low, and high laboratory values to demonstrate the complete workflow.

## 📊 Example Output

```text
Hemoglobin
10.8 g/dL
Reference: 13.0 - 17.0 g/dL
Status: LOW

Fasting Blood Glucose
96 mg/dL
Reference: 70 - 100 mg/dL
Status: NORMAL

Total Cholesterol
218 mg/dL
Reference: < 200 mg/dL
Status: HIGH

Vitamin D
19 ng/mL
Reference: 30 - 100 ng/mL
Status: LOW
```

## 🔐 Security

The Gemini API key is loaded through an environment variable.

Do not hard-code API keys in Python source code.

Do not commit:

```text
.env
```

to GitHub.

## ⚠️ Medical Safety

HealthReport AI is an **educational software prototype**.

It:

* Does not diagnose diseases.
* Does not prescribe medicines.
* Does not replace a doctor.
* Does not determine treatment.
* Does not guarantee clinical accuracy.

Users should consult a qualified healthcare professional for interpretation of actual laboratory results.

## 🔮 Future Enhancements

* OCR support for scanned reports
* Image-based report analysis
* Patient history tracking
* Report comparison over time
* Authentication and user accounts
* Database integration
* Personalized health dashboards
* Multilingual explanations
* Cloud deployment
* Doctor/clinician review workflow
* Advanced medical-document extraction

## 🎯 Project Objectives

1. Automate extraction of information from laboratory reports.
2. Use generative AI to convert complex report information into understandable language.
3. Provide structured classification of laboratory parameters.
4. Demonstrate an agentic AI workflow in a healthcare-related application.
5. Build an accessible web interface for interacting with the AI system.

## 👨‍💻 Project Status

**Status:** Prototype / Academic Project

The current version focuses on text-based laboratory PDF reports and educational analysis.

## 📜 License

This project is intended for academic and educational purposes.
::: 
