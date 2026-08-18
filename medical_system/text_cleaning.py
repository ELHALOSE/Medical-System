import re


def clean_page_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?i)\s*---\s*PAGE\s*\d+\s*---\s*", "\n", text)
    text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ch.isprintable()).replace("\t", " ")
    broken_words = {"str ength": "strength", "r ecommendations": "recommendations", "Car diovascular": "Cardiovascular", "Fr equency": "Frequency", "tr eatment": "treatment", "Pr egnancy": "Pregnancy", "pr otocols": "protocols", "r esearch": "research", "Futur e": "Future", "Gr oup": "Group", "inter nal": "internal", "Exter nal": "External", "meth odologist": "methodologist", "anal ysis": "analysis", "med ications": "medications", "pr essure": "pressure", "befor e": "before", "T arget": "Target", "Resear ch": "Research", "appr oach": "approach", "r eplaced": "replaced", "alr eady": "already", "ther e": "there", "P atient": "Patient", "labor atory": "laboratory", "diur etics": "diuretics", "thr eshold": "threshold", "r ecommendation": "recommendation"}
    for broken, fixed in broken_words.items():
        text = re.sub(rf"\b{re.escape(broken)}\b", fixed, text, flags=re.IGNORECASE)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[ \t]+([,.!?;:])", r"\1", text)
    text = re.sub(r"([\(\[]) +", r"\1", text)
    text = re.sub(r" +([\)\]])", r"\1", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def clean_full_text(text: str) -> str:
    if not text:
        return ""
    pages = re.split(r"(\n--- PAGE \d+ ---\n)", text)
    parts = [clean_page_text(part) for part in pages if not re.fullmatch(r"\n--- PAGE \d+ ---\n", part or "")]
    return "\n\n".join(part.strip() for part in parts if part.strip())


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r", "\n").replace("\t", " ")
    text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?i)\b(?:[a-z]\s+){2,}[a-z]\b", lambda match: re.sub(r"\s+", "", match.group(0)), text)
    text = re.sub(r"(?i)\s*---\s*PAGE\s*\d+\s*---\s*", " ", text)
    text = re.sub(r"\s*---\s*---\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"([\(\[])\s+", r"\1", text)
    return re.sub(r"\s+([\)\]])", r"\1", text).strip()