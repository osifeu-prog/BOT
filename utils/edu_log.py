"""
edu_log.py
==========
HE: מודול לוגים חינוכיים — מסביר בזמן ריצה מה קורה במערכת.
EN: Educational logging module — explains at runtime what the system is doing.
"""

from utils.config import DEBUG_MODE

def _print(prefix: str, text: str):
    """
    HE: מדפיס לוג רק אם DEBUG_MODE=True.
    EN: Prints log only if DEBUG_MODE=True.
    """
    if not DEBUG_MODE:
        return
    print(f"{prefix} {text}")

def edu_step(step_number: int, text: str):
    """
    HE: מדפיס שלב ממוספר.
    EN: Prints a numbered step.
    """
    _print(f"🟦 STEP {step_number}:", text)

def edu_path(text: str):
    """
    HE: מדפיס נתיב זרימה (Flow Path).
    EN: Prints a flow path.
    """
    _print("🟪 PATH:", text)

def edu_success(text: str):
    """
    HE: מדפיס הודעת הצלחה.
    EN: Prints a success message.
    """
    _print("🟩 SUCCESS:", text)

def edu_warning(text: str):
    """
    HE: מדפיס אזהרה.
    EN: Prints a warning.
    """
    _print("🟧 WARNING:", text)

def edu_error(text: str):
    """
    HE: מדפיס שגיאה.
    EN: Prints an error.
    """
    _print("🟥 ERROR:", text)
