import io
import json
import os
from typing import List

import pymupdf
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()


# ---------- Structured schemas ----------

class ExtractedParameter(BaseModel):
    name: str
    value: str
    unit: str
    reference_range: str
    notes: str = ""


class ExtractionResult(BaseModel):
    parameters: List[ExtractedParameter]


class ExplanationResult(BaseModel):
    overall_status: str
    summary: str
    key_observations: List[str]
    general_guidance: List[str]


# ---------- PDF tool ----------

def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Tool used by the agent to extract text from the uploaded PDF."""
    text = []

    with pymupdf.open(stream=io.BytesIO(pdf_bytes), filetype="pdf") as doc:
        for page in doc:
            text.append(page.get_text("text"))

    return "\n".join(text).strip()


# ---------- Agent 1: extraction ----------

def extraction_agent(client, report_text: str) -> ExtractionResult:
    prompt = f"""
You are the Document Extraction Agent in HealthReport AI.

Extract laboratory test parameters from the supplied report text.

For every confidently identified test, return:
- name
- exact value as written
- unit
- reference range exactly as written when available
- notes if useful

Rules:
- Never invent missing values.
- Never invent reference ranges.
- Ignore patient identifiers and unrelated administrative text.
- Do not diagnose anything.

REPORT:
{report_text[:30000]}
"""

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=ExtractionResult,
        ),
    )

    return ExtractionResult.model_validate_json(response.text)


# ---------- Deterministic range tool ----------

def classify_value(value_text: str, range_text: str) -> str:
    """
    Safely classify simple numeric ranges.

    Supported examples:
    12.0 - 16.0
    70-100
    < 200
    > 5

    If the format is not confidently understood, return Unknown.
    """
    import re

    try:
        value_match = re.search(r"-?\d+(?:\.\d+)?", value_text.replace(",", ""))
        if not value_match:
            return "Unknown"

        value = float(value_match.group())

        r = range_text.replace(",", "").strip()

        # Range: 12 - 16
        m = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(-?\d+(?:\.\d+)?)", r)
        if m:
            low, high = float(m.group(1)), float(m.group(2))
            if value < low:
                return "Low"
            if value > high:
                return "High"
            return "Normal"

        # Less than
        m = re.search(r"<\s*(-?\d+(?:\.\d+)?)", r)
        if m:
            return "Normal" if value < float(m.group(1)) else "High"

        # Less than or equal
        m = re.search(r"<=\s*(-?\d+(?:\.\d+)?)", r)
        if m:
            return "Normal" if value <= float(m.group(1)) else "High"

        # Greater than
        m = re.search(r">\s*(-?\d+(?:\.\d+)?)", r)
        if m:
            return "Normal" if value > float(m.group(1)) else "Low"

        # Greater than or equal
        m = re.search(r">=\s*(-?\d+(?:\.\d+)?)", r)
        if m:
            return "Normal" if value >= float(m.group(1)) else "Low"

    except Exception:
        pass

    return "Unknown"


# ---------- Agent 2: explanation ----------

def explanation_agent(client, analyzed_parameters: list) -> ExplanationResult:
    prompt = f"""
You are the Explanation Agent in HealthReport AI.

Create a cautious educational explanation of the laboratory results below.

Rules:
- Do NOT diagnose diseases.
- Do NOT prescribe medicines or treatment.
- Do NOT claim that an abnormal result proves a disease.
- Explain that interpretation depends on age, sex, symptoms, history and the
  laboratory's reference range.
- If a value is Low or High, explain only generally why that parameter can
  deserve attention.
- Give practical but non-prescriptive guidance such as discussing abnormal
  results with a healthcare professional.
- Keep the summary concise.

LAB RESULTS:
{json.dumps(analyzed_parameters, indent=2)}
"""

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=ExplanationResult,
        ),
    )

    return ExplanationResult.model_validate_json(response.text)


# ---------- Agent orchestrator ----------

def run_health_report_agent(pdf_bytes: bytes, progress_callback=None):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "error": (
                "GEMINI_API_KEY is missing. Create a .env file and add your API key."
            )
        }

    def progress(value, message):
        if progress_callback:
            progress_callback(value, message)

    # Create Gemini client.
    client = genai.Client(api_key=api_key)

    # Step 1: document tool
    report_text = extract_pdf_text(pdf_bytes)

    if not report_text:
        return {
            "error": (
                "No selectable text was found in this PDF. "
                "For today's version, use a text-based laboratory PDF."
            )
        }

    progress(35, "Agent 2/4 — identifying laboratory parameters...")
    extracted = extraction_agent(client, report_text)

    # Step 2: deterministic analysis tool
    progress(60, "Agent 3/4 — checking values against report ranges...")
    analyzed = []

    for p in extracted.parameters:
        status = classify_value(p.value, p.reference_range)
        analyzed.append({
            "name": p.name,
            "value": p.value,
            "unit": p.unit,
            "reference_range": p.reference_range or "Not available",
            "status": status,
            "explanation": "",
        })

    # Step 3: explanation agent
    progress(80, "Agent 4/4 — generating educational explanation...")
    explanation = explanation_agent(client, analyzed)

    # Add parameter-level explanations with a small, safe mapping.
    explanations = {
        "Low": "This value is below the reference range shown on the report and may deserve professional review.",
        "High": "This value is above the reference range shown on the report and may deserve professional review.",
        "Normal": "This value falls within the reference range shown on the report.",
        "Unknown": "A reliable classification was not possible from the available reference range.",
    }

    for p in analyzed:
        p["explanation"] = explanations[p["status"]]

    return {
        "parameters": analyzed,
        "overall_status": explanation.overall_status,
        "attention_count": sum(
            1 for p in analyzed if p["status"] in ["Low", "High"]
        ),
        "summary": explanation.summary,
        "key_observations": explanation.key_observations,
        "general_guidance": explanation.general_guidance,
    }
