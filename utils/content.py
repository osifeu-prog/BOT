"""
utils/content.py
=================
קריאת קבצי Markdown מתוך תיקיית course/
ופיצול לעמודים לפי מפריד --- PAGE ---.
"""

import os

PAGE_SEPARATOR = "--- PAGE ---"

def load_markdown(filename: str) -> str:
    """
    קורא קובץ Markdown מתוך התיקייה course/
    ומחזיר את התוכן שלו כמחרוזת.
    """
    path = os.path.join("course", filename)

    if not os.path.exists(path):
        return "⚠️ הקובץ לא נמצא."

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_markdown_pages(filename: str) -> list[str]:
    """
    קורא קובץ Markdown ומחזיר רשימת עמודים.

    מפריד בין עמודים לפי השורה:
    --- PAGE ---
    """
    content = load_markdown(filename)
    pages = [p.strip() for p in content.split(PAGE_SEPARATOR)]
    return [p for p in pages if p]
