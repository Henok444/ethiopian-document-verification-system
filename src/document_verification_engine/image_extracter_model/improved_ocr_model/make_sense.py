"""
make_sense.py - clean up OCR text from an ID card.

Input: a .txt file with one OCR line per row, usually "AMHARIC / ENGLISH"
(lines with only one script are fine too).

Usage:
    python make_sense.py ocr.txt only_amh
    python make_sense.py ocr.txt only_eng
    python make_sense.py ocr.txt make_sense --use amh     # Amharic text only
    python make_sense.py ocr.txt make_sense --use eng     # English text only
    python make_sense.py ocr.txt make_sense --use both    # default

From another script:
    from make_sense import process
    print(process(open("ocr.txt", encoding="utf-8").read(), "make_sense", "both"))

Needs:  uv add rapidfuzz
"""
import argparse
import re
from pathlib import Path

from rapidfuzz import fuzz, process as rf_process

LABEL_MIN = 75                     # minimum fuzzy score (0-100) to accept a label

ETH = r"\u1200-\u135A"             # Ethiopic syllables (no Ethiopic numerals)
RE_ETH = re.compile(f"[{ETH}]")
RE_LAT = re.compile(r"[A-Za-z]")

# key, English label, Amharic label, kind of value.
# CHECK THE AMHARIC SPELLINGS against your card before relying on them.
FIELDS = [
    ("surname",     "Surname",           "የአያት ስም",        "text"),
    ("given_name",  "Given Name",        "ስም ከነአባት",       "text"),
    ("nationality", "Nationality",       "ዜግነት",            "text"),
    ("sex",         "Sex",               "ፆታ",              "sex"),
    ("dob",         "Date of Birth",     "የትውልድ ቀን",      "date"),
    ("pob",         "Place of Birth",    "የትውልድ ቦታ",      "text"),
    ("issue_date",  "Date of Issue",     "የተሰጠበት ቀን",     "date"),
    ("expiry_date", "Date of Expiry",    "የሚያበቃበት ቀን",    "date"),
    ("authority",   "Issuing Authority", "የሰጠው ባለስልጣን",   "text"),
    ("id_no",       "Personal No.",      "",                 "id"),
]
KIND = {k: kind for k, _, _, kind in FIELDS}
DATE_FIELDS = [k for k, _, _, kind in FIELDS if kind == "date"]
NAME_FIELDS = {"surname", "given_name"}
MULTILINE = {"authority"}          # fields whose value may run over several lines

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
DATE_RE = re.compile(r"(\d{1,2})\s*([/|\\.\- ])?\s*([A-Za-z]{3})\s*([/|\\.\- ])?\s*(\d{2,4})")
DATE_NUM_RE = re.compile(r"(\d{1,2})\s*([/.\-])\s*(\d{1,2})\s*[/.\-]\s*(\d{4})")
DATE_SLASH = re.compile(r"(\d{1,2})\s*/\s*([A-Za-z]{3}|\d{1,2})\s*/\s*(\d{2,4})")
SEP = "\u0001"                    # stands in for the slashes inside a date
ID_RE = re.compile(r"\b([A-Z]{1,3})\s?(\d{6,9})\b")


# ----------------------------------------------------------------------------
# Parsing lines
# ----------------------------------------------------------------------------
def clean_am(s):
    """Keep Ethiopic syllables, digits, spaces."""
    return " ".join(re.sub(rf"[^{ETH}0-9\s]", "", s).split())


def clean_en(s):
    """Keep Latin letters, digits, spaces, basic punctuation."""
    return " ".join(re.sub(r"[^A-Za-z0-9\s.,'/\-]", "", s).split())


def split_line(line):
    """'AM / EN' -> (am, en). A line with no slash goes to whichever script dominates."""
    line = DATE_SLASH.sub(lambda m: f"{m.group(1)}{SEP}{m.group(2)}{SEP}{m.group(3)}", line)
    if "/" in line:
        am, en = line.split("/", 1)
        return am.replace(SEP, "/"), en.replace(SEP, "/")
    n_am = len(RE_ETH.findall(line))
    n_en = len(RE_LAT.findall(line))
    line = line.replace(SEP, "/")
    return (line, "") if n_am > n_en else ("", line)


def parse(text):
    rows = []
    for raw in text.splitlines():
        raw = raw.strip()
        if raw:
            am, en = split_line(raw)
            rows.append((clean_am(am), clean_en(en)))
    return rows


# ----------------------------------------------------------------------------
# Mode 1 and 2: only one script
# ----------------------------------------------------------------------------
def only_amh(rows):
    return [a for a, _ in rows if RE_ETH.search(a)]


def only_eng(rows):
    return [e for _, e in rows if RE_LAT.search(e) or len(re.findall(r"\d", e)) >= 3]


# ----------------------------------------------------------------------------
# Mode 3: make sense
# ----------------------------------------------------------------------------
def skeleton(s):
    """Collapse every Ethiopic syllable to its consonant family.
    Ge'ez syllables sit in blocks of 8 code points (one per vowel order), so the
    common OCR confusions (ሰ/ስ, አ/እ/ኢ, ው/ዉ) become identical."""
    out = []
    for ch in s:
        cp = ord(ch)
        if 0x1200 <= cp <= 0x135A:
            cp = 0x1200 + ((cp - 0x1200) // 8) * 8
        out.append(chr(cp))
    return "".join(out)


def am_score(line, label):
    a, b = skeleton(line), skeleton(label)
    if len(b.replace(" ", "")) >= 6:           # long labels may sit inside a longer line
        return max(fuzz.ratio(a, b), fuzz.partial_ratio(a, b))
    return fuzz.ratio(a, b)                    # short labels: compare the whole line only


def find_label(am, en, use):
    """Return the field key if this line is a label, else None."""
    if use in ("eng", "both") and en:
        e = re.sub(r"[^a-z ]", "", en.lower()).strip()
        if len(e) >= 3:
            scored = [(fuzz.ratio(e, re.sub(r"[^a-z ]", "", lab.lower())), k)
                      for k, lab, _, _ in FIELDS]
            score, key = max(scored)
            if score >= LABEL_MIN:
                return key
    if use in ("amh", "both") and am:
        scored = [(am_score(am, lab_am), k) for k, _, lab_am, _ in FIELDS if lab_am]
        if scored:
            score, key = max(scored)
            if score >= LABEL_MIN:
                return key
    return None


def parse_date(en):
    m = DATE_RE.search(en)
    if m:
        day, s1, mon, s2, year = m.groups()
        hit = rf_process.extractOne(mon.upper(), MONTHS, scorer=fuzz.ratio)
        if hit and hit[1] >= 66:
            sep = "/" if "/" in ((s1 or "") + (s2 or "")) else " "
            return f"{day}{sep}{hit[0]}{sep}{year}"
    m = DATE_NUM_RE.search(en)
    if m:
        d, sep, mo, y = m.groups()
        return f"{d}{sep}{mo}{sep}{y}"
    return None


def parse_id(en):
    m = ID_RE.search(en.upper())
    return f"{m.group(1)}{m.group(2)}" if m else None


def parse_sex(en):
    t = en.strip().upper()
    return t if t in {"M", "F", "MALE", "FEMALE"} else None


def tidy_name(en):
    """Drop 1-2 letter junk tokens when longer tokens exist."""
    toks = en.split()
    if any(len(t) >= 3 for t in toks):
        toks = [t for t in toks if len(t) >= 3]
    return " ".join(toks)


def make_sense(rows, use):
    patterns = use in ("eng", "both")          # dates/IDs are recognised from Latin text
    res = {k: {"am": "", "en": "", "flag": ""} for k, _, _, _ in FIELDS}
    unassigned, current = [], None

    def put(key, am, en, flag=""):
        r = res[key]
        r["am"] = (r["am"] + " " + am).strip()
        r["en"] = (r["en"] + " " + en).strip()
        if flag:
            r["flag"] = flag

    def has_value(key):
        return bool(res[key]["am"] or res[key]["en"])

    for am, en in rows:
        if use == "amh":
            en = ""
        if use == "eng":
            am = ""
        if not am and not en:
            continue

        key = find_label(am, en, use)
        if key:
            current = key
            continue

        if patterns:
            ident = parse_id(en)
            if ident and not res["id_no"]["en"]:
                put("id_no", "", ident)
                continue
            date = parse_date(en)
            if date:
                if current in DATE_FIELDS and not res[current]["en"]:
                    target = current
                else:
                    target = next((k for k in DATE_FIELDS if not res[k]["en"]), None)
                if target:
                    put(target, am, date)
                else:
                    unassigned.append((am, en))
                continue

        if current is None:
            unassigned.append((am, en))
            continue

        kind = KIND[current] if patterns else "text"
        if kind == "sex":
            s = parse_sex(en)
            if s:
                put(current, am, s)
            else:
                put(current, "", "", flag=f"unreadable: {en!r}")
        elif kind in ("date", "id"):
            put(current, am, en, flag="check format")
        elif has_value(current) and (current not in MULTILINE
                                     or (len(am) <= 3 and len(en) <= 3)):
            unassigned.append((am, en))        # extra line for a one-line field, or short junk
        elif current in NAME_FIELDS:
            put(current, am, tidy_name(en))
        else:
            put(current, am, en)

    return render(res, unassigned, use)


def render(res, unassigned, use):
    out = []
    for key, lab_en, lab_am, _ in FIELDS:
        r = res[key]
        if use == "amh":
            label, value = (lab_am or lab_en), r["am"]
        elif use == "eng":
            label, value = lab_en, r["en"]
        else:
            label = f"{lab_en} / {lab_am}" if lab_am else lab_en
            value = " / ".join(x for x in (r["en"], r["am"]) if x)
        line = f"{label}: {value if value else '(not found)'}"
        if r["flag"]:
            line += f"   [{r['flag']}]"
        out.append(line)
    if unassigned:
        out.append("")
        out.append("Unassigned lines (no label matched):")
        for am, en in unassigned:
            shown = {"amh": am, "eng": en}.get(use) or " / ".join(x for x in (am, en) if x)
            out.append(f"  {shown}")
    return "\n".join(out)


# ----------------------------------------------------------------------------
# Entry points
# ----------------------------------------------------------------------------
def process(text, mode, use="both"):
    rows = parse(text)
    if mode == "only_amh":
        return "\n".join(only_amh(rows))
    if mode == "only_eng":
        return "\n".join(only_eng(rows))
    return make_sense(rows, use)


def make_se(argv=None):
    global LABEL_MIN
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="OCR .txt file")
    ap.add_argument("mode", choices=["only_amh", "only_eng", "make_sense"])
    ap.add_argument("--use", choices=["amh", "eng", "both"], default="both",
                    help="for make_sense: which text to use (default both)")
    ap.add_argument("--label-min", type=float, default=LABEL_MIN,
                    help="minimum fuzzy score to accept a label (default 75)")
    ap.add_argument("--out", help="output file (default: <input>_<mode>.txt)")
    args = ap.parse_args(argv)
    LABEL_MIN = args.label_min

    text = Path(args.file).read_text(encoding="utf-8")
    result = process(text, args.mode, args.use)
    print(result)

    suffix = args.mode + (f"_{args.use}" if args.mode == "make_sense" else "")
    out_path = args.out or f"{Path(args.file).stem}_{suffix}.txt"
    Path(out_path).write_text(result + "\n", encoding="utf-8")
    print(f"\nSaved {out_path}")
    return result


