"""
OpportunityIQ — Helper Utilities

Shared utility functions used across modules.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def load_json_file(filepath: str | Path) -> dict:
    """Load and parse a JSON file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(data: Any, filepath: str | Path) -> None:
    """Save data to a JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def timestamp_now() -> str:
    """Return current ISO timestamp."""
    return datetime.now().isoformat()


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_match_score(score: float) -> str:
    """Format a 0-1 match score as a percentage string."""
    return f"{int(score * 100)}%"
