"""
content.py
==========
HE: קריאת קבצי Markdown של הקורס וחלוקה לעמודים.
EN: Reading course Markdown files and splitting into pages.
"""

import os
from utils.edu_log import edu_step, edu_error

PAGE_SEPARATOR = "--- PAGE ---"

def load_markdown(path: str) -> str:
    """
    HE: קורא קובץ Markdown ומחזיר את התוכן שלו.
    EN: Reads a Markdown file and returns its content.
    """
    edu_step(1, f"Loading markdown file: {path}")
    if not os.path.exists(path):
        edu_error(f"Markdown file not found: {path}")
        return "⚠️ File not found."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_markdown_pages(path: str) -> list[str]:
    """
    HE: מחלק את הקובץ לעמודים לפי PAGE_SEPARATOR.
    EN: Splits the file into pages using PAGE_SEPARATOR.
    """
    content = load_markdown(path)
    pages = [p.strip() for p in content.split(PAGE_SEPARATOR)]
    return [p for p in pages if p]
