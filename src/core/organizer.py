"""
File Organizer

Handles renaming and moving PDF files based on metadata.
"""
import os
import re
import shutil
from typing import Optional
from .metadata import PaperMetadata


# Default naming formats
NAMING_FORMATS = {
    "default": "[{year}] {author} - {title}.pdf",
    "underscore": "{author}_{year}_{title}.pdf",
    "title_first": "{title} ({year}).pdf",
}


def sanitize_filename(name: str, max_length: int = 200) -> str:
    """
    Sanitize a string for use as a filename.
    
    Args:
        name: String to sanitize
        max_length: Maximum length for the filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "", name)
    
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Trim and limit length
    sanitized = sanitized.strip()
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rsplit(' ', 1)[0]
    
    return sanitized


def generate_filename(metadata: PaperMetadata, format_name: str = "default") -> str:
    """
    Generate a filename based on metadata and format.
    
    Args:
        metadata: Paper metadata
        format_name: Name of the format to use
        
    Returns:
        str: Generated filename
    """
    format_string = NAMING_FORMATS.get(format_name, NAMING_FORMATS["default"])
    
    # Prepare values
    year = str(metadata.year) if metadata.year else "Unknown"
    author = sanitize_filename(metadata.author_string)
    title = sanitize_filename(metadata.title)
    
    # Truncate long titles
    if len(title) > 100:
        title = title[:100].rsplit(' ', 1)[0] + "..."
    
    # Format the filename
    filename = format_string.format(
        year=year,
        author=author,
        title=title,
        journal=sanitize_filename(metadata.journal or "")
    )
    
    return filename


def organize_file(
    source_path: str,
    metadata: PaperMetadata,
    output_folder: str,
    format_name: str = "default",
    copy_instead_of_move: bool = False
) -> Optional[str]:
    """
    Rename and move/copy a file based on metadata.
    
    Args:
        source_path: Path to the source PDF
        metadata: Paper metadata
        output_folder: Destination folder
        format_name: Naming format to use
        copy_instead_of_move: If True, copy instead of move
        
    Returns:
        Optional[str]: New file path if successful, None otherwise
    """
    try:
        # Generate new filename
        new_filename = generate_filename(metadata, format_name)
        
        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        # Build destination path
        dest_path = os.path.join(output_folder, new_filename)
        
        # Handle duplicate filenames
        base, ext = os.path.splitext(dest_path)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = f"{base} ({counter}){ext}"
            counter += 1
        
        # Move or copy
        if copy_instead_of_move:
            shutil.copy2(source_path, dest_path)
        else:
            shutil.move(source_path, dest_path)
        
        return dest_path
        
    except Exception as e:
        print(f"File organization failed: {e}")
        return None
