"""
OpportunityIQ — Logging Configuration

Provides structured logging for all application modules.
Never logs API keys, credentials, or sensitive resume content.
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create a configured logger for a module.
    
    Args:
        name: Module name (typically __name__).
        level: Logging level.
    
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(f"opportunityiq.{name}")
    
    if not logger.handlers:
        logger.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Format: timestamp | level | module | message
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger
