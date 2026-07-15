"""
File management — natural-language-ish file operations.
Searches, lists, organizes files in common user folders.

Safety: destructive ops (delete) always require confirmation,
and organize only MOVES files (never deletes).
"""
import os
import shutil
from pathlib import Path

# Folders JARVIS is allowed to touch
SAFE_ROOTS = [
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Downloads",
    Path.home() / "Pictures",
]

CATEGORY_MAP = {
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"},
    "Documents": {".pdf", ".docx", ".doc", ".txt", ".md", ".rtf", ".odt"},
    "Spreadsheets": {".xlsx", ".xls", ".csv"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a", ".ogg"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".json", ".cpp", ".java", ".lua"},
    "Installers": {".exe", ".msi", ".dmg"},
}


def find_files(keyword: str, limit: int = 15) -> str:
    """Search filenames across safe folders."""
    keyword = keyword.lower()
    hits = []
    for root in SAFE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and keyword in path.name.lower():
                hits.append(str(path))
                if len(hits) >= limit:
                    break
        if len(hits) >= limit:
            break
    if not hits:
        return f"No files matching '{keyword}' found, sir."
    listing = "\n".join(hits)
    return f"Found {len(hits)} file(s):\n{listing}"


def organize_folder(folder_name: str = "Downloads") -> str:
    """Sort a folder's files into category subfolders. Move-only, never deletes."""
    folder = Path.home() / folder_name.capitalize()
    if not folder.exists():
        return f"I can't find a {folder_name} folder, sir."

    moved = 0
    for item in folder.iterdir():
        if not item.is_file():
            continue
        ext = item.suffix.lower()
        for category, exts in CATEGORY_MAP.items():
            if ext in exts:
                dest_dir = folder / category
                dest_dir.mkdir(exist_ok=True)
                dest = dest_dir / item.name
                # Never overwrite — append number if name exists
                counter = 1
                while dest.exists():
                    dest = dest_dir / f"{item.stem}_{counter}{item.suffix}"
                    counter += 1
                shutil.move(str(item), str(dest))
                moved += 1
                break
    return f"Organized {moved} files in {folder_name} into category folders, sir."


def biggest_files(folder_name: str = "Downloads", top: int = 5) -> str:
    """Report the largest files (helps find what's eating disk space)."""
    folder = Path.home() / folder_name.capitalize()
    if not folder.exists():
        return f"No {folder_name} folder found."
    files = [(f.stat().st_size, f) for f in folder.rglob("*") if f.is_file()]
    files.sort(reverse=True)
    lines = [f"{size / 1024 / 1024:.1f} MB — {f.name}" for size, f in files[:top]]
    return "Largest files:\n" + "\n".join(lines) if lines else "Folder is empty."
