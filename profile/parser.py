"""
OpportunityIQ — Resume Parser

Extracts text from PDF, DOCX, and TXT resumes.
Parses extracted text into a structured UserProfile.
"""

import io
import json
from pathlib import Path
from typing import Optional

from profile.models import UserProfile, Education, Experience, Project
from utils.logger import get_logger
from utils.validators import validate_file_upload

logger = get_logger(__name__)


class ResumeParseError(Exception):
    """Raised when resume parsing fails."""
    pass


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise ResumeParseError(f"Failed to extract text from PDF: {e}") from e


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        raise ResumeParseError(f"Failed to extract text from DOCX: {e}") from e


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from a TXT file."""
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return file_bytes.decode("latin-1")
        except Exception as e:
            raise ResumeParseError(f"Failed to decode text file: {e}") from e


def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Extract text from a resume file based on extension.
    
    Args:
        filename: Original filename with extension.
        file_bytes: Raw file content.
    
    Returns:
        Extracted text string.
    """
    ext = Path(filename).suffix.lower()
    
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == ".docx":
        return extract_text_from_docx(file_bytes)
    elif ext == ".txt":
        return extract_text_from_txt(file_bytes)
    else:
        raise ResumeParseError(f"Unsupported file type: {ext}")


def parse_resume_with_llm(resume_text: str) -> Optional[dict]:
    """
    Use LLM to extract structured profile data from resume text.
    
    Returns a dict that can be used to create a UserProfile,
    or None if LLM is not configured.
    """
    from config import config
    
    if not config.llm.is_configured:
        logger.warning("LLM not configured — cannot parse resume with AI")
        return None

    prompt = f"""Extract structured profile information from this resume text.

Return ONLY a valid JSON object with these fields:
{{
    "name": "Full Name",
    "education": {{
        "degree": "Degree name",
        "field_of_study": "Field",
        "university": "University name",
        "year": "Year or level (e.g., 3rd Year, Graduate)"
    }},
    "location": "City, State/Country",
    "skills": ["skill1", "skill2"],
    "experiences": [
        {{
            "title": "Role",
            "organization": "Company",
            "duration": "Duration",
            "description": "Brief description"
        }}
    ],
    "projects": [
        {{
            "name": "Project name",
            "description": "Brief description",
            "technologies": ["tech1", "tech2"]
        }}
    ],
    "certifications": ["cert1", "cert2"],
    "preferred_domains": ["domain1", "domain2"]
}}

If any field is not found in the resume, use null or empty list.
Do NOT fabricate information that is not in the resume.

Resume text:
{resume_text}
"""

    try:
        if config.llm.provider == "gemini":
            return _parse_with_gemini(prompt, config)
        elif config.llm.provider == "openai":
            return _parse_with_openai(prompt, config)
        else:
            logger.error(f"Unknown LLM provider: {config.llm.provider}")
            return None
    except Exception as e:
        logger.error(f"LLM resume parsing failed: {e}")
        return None


def _parse_with_gemini(prompt: str, config) -> Optional[dict]:
    """Parse resume using Google Gemini."""
    import google.generativeai as genai
    
    genai.configure(api_key=config.llm.api_key)
    model = genai.GenerativeModel(config.llm.model_name)
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Extract JSON from response
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    
    return json.loads(text)


def _parse_with_openai(prompt: str, config) -> Optional[dict]:
    """Parse resume using OpenAI."""
    from openai import OpenAI
    
    client = OpenAI(api_key=config.llm.api_key)
    response = client.chat.completions.create(
        model=config.llm.model_name,
        messages=[
            {"role": "system", "content": "You extract structured data from resumes. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    
    text = response.choices[0].message.content.strip()
    return json.loads(text)


def dict_to_profile(data: dict) -> UserProfile:
    """Convert a parsed dict into a UserProfile object."""
    education = None
    if data.get("education"):
        edu = data["education"]
        education = Education(
            degree=edu.get("degree"),
            field_of_study=edu.get("field_of_study"),
            university=edu.get("university"),
            year=edu.get("year"),
        )
    
    experiences = []
    for exp in data.get("experiences", []):
        experiences.append(Experience(
            title=exp.get("title"),
            organization=exp.get("organization"),
            duration=exp.get("duration"),
            description=exp.get("description"),
        ))
    
    projects = []
    for proj in data.get("projects", []):
        projects.append(Project(
            name=proj.get("name"),
            description=proj.get("description"),
            technologies=proj.get("technologies", []),
        ))
    
    return UserProfile(
        name=data.get("name"),
        education=education,
        location=data.get("location"),
        skills=data.get("skills", []),
        experiences=experiences,
        projects=projects,
        certifications=data.get("certifications", []),
        preferred_domains=data.get("preferred_domains", []),
    )


def parse_resume(filename: str, file_bytes: bytes) -> tuple[str, UserProfile]:
    """
    Full resume parsing pipeline.
    
    1. Validates file
    2. Extracts text
    3. Uses LLM for structured extraction (if available)
    4. Falls back to basic parsing
    
    Returns:
        (extracted_text, profile)
    """
    # Validate
    is_valid, error = validate_file_upload(filename, len(file_bytes))
    if not is_valid:
        raise ResumeParseError(error)
    
    # Extract text
    text = extract_text(filename, file_bytes)
    if not text.strip():
        raise ResumeParseError("No text could be extracted from the file.")
    
    logger.info(f"Extracted {len(text)} characters from {filename}")
    
    # Try LLM parsing
    parsed_data = parse_resume_with_llm(text)
    if parsed_data:
        profile = dict_to_profile(parsed_data)
        logger.info("Resume parsed with LLM successfully")
        return text, profile
    
    # Basic fallback: return text with empty profile
    logger.info("LLM not available — returning basic profile")
    profile = UserProfile(name=None, skills=[])
    return text, profile


def parse_resume_file(file_bytes: bytes, filename: str) -> Optional[UserProfile]:
    """Helper for UI file upload integration."""
    try:
        text, profile = parse_resume(filename, file_bytes)
        return profile
    except Exception as e:
        logger.error(f"Error parsing resume file {filename}: {e}")
        return None

