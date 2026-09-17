"""
OpportunityIQ — Input Validators

Validates user inputs, file uploads, and search parameters.
"""

from pathlib import Path
from typing import Optional


ALLOWED_FILE_TYPES = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_MB = 10


def validate_file_upload(filename: str, file_size_bytes: int) -> tuple[bool, Optional[str]]:
    """
    Validate an uploaded file.
    
    Returns:
        (is_valid, error_message)
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_FILE_TYPES:
        return False, f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_FILE_TYPES)}"
    
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        return False, f"File too large ({file_size_bytes / (1024*1024):.1f} MB). Maximum: {MAX_FILE_SIZE_MB} MB."
    
    return True, None


def validate_search_query(query: str) -> tuple[bool, Optional[str]]:
    """Validate a search query string."""
    if not query or not query.strip():
        return False, "Search query cannot be empty."
    
    if len(query.strip()) < 3:
        return False, "Search query must be at least 3 characters."
    
    if len(query) > 500:
        return False, "Search query must be under 500 characters."
    
    return True, None
