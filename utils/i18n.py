def detect_language_from_telegram(lang_code):
    if lang_code and lang_code.startswith("he"):
        return "he"
    return "en"

def t(lang, he, en):
    return he if lang == "he" else en
