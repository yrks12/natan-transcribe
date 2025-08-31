import os
import tempfile
from pathlib import Path
import hashlib
from typing import Optional
import streamlit as st

from config.settings import TEMP_DIR, MAX_FILE_SIZE_MB


def save_uploaded_file(uploaded_file) -> Optional[Path]:
    """Save uploaded file to temporary directory."""
    if uploaded_file is None:
        return None
    
    # Show file size info (but no limit check for local usage)
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    # Create unique filename using hash
    file_hash = hashlib.md5(uploaded_file.name.encode()).hexdigest()[:8]
    file_extension = Path(uploaded_file.name).suffix
    temp_filename = f"{file_hash}_{uploaded_file.name}"
    temp_path = TEMP_DIR / temp_filename
    
    # Save file
    try:
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return temp_path
    except Exception as e:
        st.error(f"שגיאה בשמירת הקובץ: {str(e)}")
        return None


def cleanup_file(file_path: Path) -> None:
    """Remove temporary file."""
    try:
        if file_path and file_path.exists():
            os.remove(file_path)
    except Exception as e:
        st.warning(f"Could not clean up temporary file: {e}")


def get_file_info(file_path: Path) -> dict:
    """Get information about a file."""
    if not file_path or not file_path.exists():
        return {}
    
    stats = os.stat(file_path)
    return {
        "name": file_path.name,
        "size_mb": stats.st_size / (1024 * 1024),
        "extension": file_path.suffix.lower().lstrip(".")
    }


def create_download_link(content: str, filename: str) -> bytes:
    """Create downloadable content."""
    return content.encode('utf-8')