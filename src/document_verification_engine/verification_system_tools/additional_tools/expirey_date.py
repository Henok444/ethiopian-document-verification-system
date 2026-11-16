"""
expiry_dates.py - find the date of expiry (Ethiopian and Gregorian) in OCR text.

    from expiry_dates import extract_expiry_dates
    extract_expiry_dates(text)
    # {'ethiopian': '12/ጥር/2024', 'gregorian': '19/SEP/2031'}   (None where not found)

Needs:  uv add rapidfuzz
"""
import re

from rapidfuzz import fuzz

ETH = r"\u1200-\u135A"                      # Ethiopic syllables
SEP = r"[/|\\.\-'\s]"                       # separators OCR may produce between date parts

# day  month  year, with any of the separators (or none) between them
ETH_DATE = re.compile(rf"(\d{{1,2}})\s*{SEP}?\s*([{ETH}]{{2,}})\s*{SEP}?\s*(\d{{2,4}})")
GREG_DATE = re.compile(rf"(\d{{1,2}})\s*{SEP}?\s*([A-Za-z]{{3}})\s*{SEP}?\s*(\d{{2,4}})")
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

# name: (English label, Amharic label), spaces removed.
# CHECK THE AMHARIC SPELLINGS against your card.
LABELS = {
    "expiry": ("dateofexpiry", "የሚያበቃበትቀን"),
    "issue":  ("dateofissue",  "የተሰጠበትቀን"),
    "birth":  ("dateofbirth",  "የትውልድቀን"),
}
LABEL_MIN = 80                              # minimum fuzzy score (0-100) to accept a label


def skeleton(s):
    """Collapse each Ethiopic syllable to its consonant family (ሰ/ስ, አ/እ/ኢ, ው/ዉ match)."""
    return "".join(
        chr(0x1200 + ((ord(c) - 0x1200) // 8) * 8) if 0x1200 <= ord(c) <= 0x135A else c
        for c in s
    )


def norm(s):
    """Keep only letters (Latin + Ethiopic), lowercase. Drops spaces, digits, punctuation."""
    return re.sub(rf"[^A-Za-z{ETH}]", "", s).lower()


def label_of(line):
    """Return 'expiry', 'issue', 'birth' or None."""
    n = norm(line)
    if not n:
        return None
    best, score = None, 0
    for name, (en, am) in LABELS.items():
        s = max(fuzz.partial_ratio(en, n),
                fuzz.partial_ratio(skeleton(am), skeleton(n)))
        if s > score:
            best, score = name, s
    return best if score >= LABEL_MIN else None


def find_dates(s):
    """Return {'ethiopian': ..., 'gregorian': ...} for whatever dates the string holds."""
    out = {}
    m = ETH_DATE.search(s)
    if m:
        out["ethiopian"] = f"{m[1]}/{m[2]}/{m[3]}"
    m = GREG_DATE.search(s)
    if m:
        score, month = max((fuzz.ratio(m[2].upper(), mo), mo) for mo in MONTHS)
        if score >= 66:                     # tolerate a slightly misread month
            out["gregorian"] = f"{m[1]}/{month}/{m[3]}"
    return out


def extract_expiry_dates(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    result = {"ethiopian": None, "gregorian": None}

    for i, line in enumerate(lines):
        if label_of(line) != "expiry":
            continue
        chunk = [line]                              # the label line itself may hold the date
        for nxt in lines[i + 1:i + 3]:              # then the next two lines
            if label_of(nxt):                       # another label: that is a different field
                break
            chunk.append(nxt)
        for piece in chunk:
            for kind, value in find_dates(piece).items():
                result[kind] = result[kind] or value
        break  
    print(f"found dates ;-  {result}")                                     # first expiry label only
    return result


if __name__ == "__main__":
    sample = """የተሰጠበት ቀን / Date of Issue
12/ጥር/2016 / 20/Jan/2024
የሚያበቃበት ቀን / Date of Expiry
12/ጥር/2024 / 19/Sep/2031"""
    print(extract_expiry_dates(sample))