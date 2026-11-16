"""
id_reader.py - read pre-cropped ID card lines (Amharic + English) with Tesseract.

Pipeline per crop:
  1. preprocess (upscale, grayscale, pad)
  2. OCR twice: amh and eng (text + mean word confidence)
  3. slash rule: Amharic = left of first '/', English = right of last '/'
  4. classify: label / value / number / junk
  5. assemble fields in reading order (a label sets the current field,
     the values after it fill that field)

Setup:
    sudo apt install tesseract-ocr
    uv add pytesseract opencv-python rapidfuzz
    (tessdata_best amh.traineddata + eng.traineddata in ~/tessdata_best)

Run:
    uv run python id_reader.py auto_crops
    uv run python id_reader.py auto_crops --conf-min 40 --label-min 70
"""
import argparse
import csv
import json
import os
import pathlib
import re

import cv2
import pytesseract
from pytesseract import Output
from rapidfuzz import fuzz, process

BASE = pathlib.Path(__file__).resolve().parents[4]
results_dir = BASE / "data" / "results"
results_dir.mkdir( exist_ok=True)


# ----------------------------------------------------------------------------
# Settings you will tune
# ----------------------------------------------------------------------------
CONF_MIN = 50    # minimum OCR confidence (0-100) for a value half to count as real
LABEL_MIN = 75   # minimum fuzzy-match score (0-100) to accept a label
TESSDATA = os.path.expanduser("~/tessdata_best")
CFG = "--oem 1 --psm 7 -c load_system_dawg=0 -c load_freq_dawg=0"

ETH_LETTERS = r"\u1200-\u135A"      # Ethiopic syllables only (no Ethiopic numerals)

# English label text -> field key. Fragments (Given, Birth, Issue, ...) are
# included because a label can be split across two crops.
LABELS = {
    "Surname": "surname",
    "Given Name": "given_name", "Given": "given_name",
    "Name": "name",
    "Nationality": "nationality",
    "Sex": "sex",
    "Date of Birth": "dob", "Birth": "dob",
    "Date of Issue": "issue_date", "Issue": "issue_date",
    "Issuing Authority": "authority", "Authority": "authority",
    "Personal No": "id_no",
    "Signature": "signature",
}


# ----------------------------------------------------------------------------
# OCR
# ----------------------------------------------------------------------------
SEP = "\u0001"      # stands in for the slashes inside a date
DATE_SLASH = re.compile(r"(\d{1,2})\s*/\s*([A-Za-z]{3}|\d{1,2})\s*/\s*(\d{2,4})")
MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
DATE_MON = re.compile(r"(\d{1,2})\s*([/|\\.\- ])?\s*([A-Za-z]{3})\s*([/|\\.\- ])?\s*(\d{2,4})")
DATE_NUM = re.compile(r"(\d{1,2})\s*([/.\-])\s*(\d{1,2})\s*[/.\-]\s*(\d{4})")


def protect_dates(s):
    """Hide the slashes inside dates so they aren't taken as the AM/EN separator."""
    return DATE_SLASH.sub(lambda m: f"{m.group(1)}{SEP}{m.group(2)}{SEP}{m.group(3)}", s)


def has_separator(am, en):
    return "/" in protect_dates(am) and "/" in protect_dates(en)


def find_date(s):
    m = DATE_MON.search(s)
    if m:
        day, s1, mon, s2, year = m.groups()
        hit = process.extractOne(mon.upper(), MONTHS, scorer=fuzz.ratio)
        if hit and hit[1] >= 66:
            sep = "/" if "/" in ((s1 or "") + (s2 or "")) else " "
            return f"{day}{sep}{hit[0]}{sep}{year}"
    m = DATE_NUM.search(s)
    if m:
        d, sep, mo, y = m.groups()
        return f"{d}{sep}{mo}{sep}{y}"
    return None
def prep(img):
    """Upscale 2.5x, grayscale, add a white border."""
    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.copyMakeBorder(g, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)


def ocr_conf(img, lang):
    """Return (text, mean word confidence 0-100)."""
    d = pytesseract.image_to_data(img, lang=lang, config=CFG, output_type=Output.DICT)
    words = [(t.strip(), float(c)) for t, c in zip(d["text"], d["conf"])
             if t.strip() and float(c) >= 0]          # conf -1 = layout row, not a word
    text = " ".join(t for t, _ in words)
    conf = sum(c for _, c in words) / len(words) if words else 0.0
    return text, conf


# ----------------------------------------------------------------------------
# Text cleaning and the slash rule
# ----------------------------------------------------------------------------
def clean_am(s):
    """Keep Ethiopic syllables, digits, spaces."""
    return re.sub(rf"[^{ETH_LETTERS}0-9\s]", "", s).strip()


def clean_en(s):
    """Keep Latin letters, digits, spaces, basic punctuation (and '/' for dates)."""
    return re.sub(r"[^A-Za-z0-9\s.,'/\-]", "", s).strip()


def read_label(am, en):
    am_p, en_p = protect_dates(am), protect_dates(en)
    am_part = clean_am(am_p.split("/", 1)[0].replace(SEP, "/"))
    en_part = clean_en(en_p.rsplit("/", 1)[-1].replace(SEP, "/"))
    return am_part, en_part


# ----------------------------------------------------------------------------
# Classification
# ----------------------------------------------------------------------------
def match_label(en_part):
    """Fuzzy-match an English half against the label vocabulary.
    Return (field, score) or (None, best_score)."""
    text = re.sub(r"[^A-Za-z ]", "", en_part).strip()
    if len(text) < 3:
        return None, 0
    hit = process.extractOne(text, LABELS.keys(), scorer=fuzz.WRatio)
    if hit is None:
        return None, 0
    name, score = hit[0], hit[1]
    return (LABELS[name] if score >= LABEL_MIN else None), round(score)


def count(pattern, s):
    return len(re.findall(pattern, s))


def parse_crop(am, am_conf, en, en_conf):
    """Decide what one crop is. Returns a dict with kind, am, en, label_score."""
    am_part, en_part = read_label(am, en)
    am_part, en_part = read_label(am, en)
    has_slash = has_separator(am, en)                 # was: "/" in am and "/" in en

    date = find_date(en)                              # NEW: a date is never a label
    if date:
        return dict(kind="value", label_score=0,
                    am=am_part if has_slash else "", en=date)

    field, lscore = match_label(en_part)
    
    if field:
        return dict(kind="label", field=field, label_score=lscore,
                    am=am_part if has_slash else "", en=en_part)

    en_ok = count(r"[A-Za-z]", en_part) >= 3 and en_conf >= CONF_MIN
    am_ok = count(f"[{ETH_LETTERS}]", am_part) >= 2 and am_conf >= CONF_MIN

    if has_slash and (en_ok or am_ok):               # bilingual value: keep both halves
        return dict(kind="value", label_score=lscore,
                    am=am_part if am_ok else "", en=en_part if en_ok else "")
    if en_ok and (not am_ok or en_conf >= am_conf):  # English wins
        return dict(kind="value", label_score=lscore, am="", en=en_part)
    if am_ok:                                        # Amharic wins
        return dict(kind="value", label_score=lscore, am=am_part, en="")
    if re.fullmatch(r"[0-9 ]{3,}", en_part) and en_conf >= CONF_MIN:
        return dict(kind="number", label_score=lscore, am="", en=en_part)
    return dict(kind="junk", label_score=lscore, am="", en="")


# ----------------------------------------------------------------------------
# Assembling fields in reading order
# ----------------------------------------------------------------------------
def assemble(parsed):
    fields, current = {}, None
    for p in parsed:
        if p["kind"] == "label":
            current = p["field"]
            f = fields.setdefault(current, dict(am="", en=""))
            f["am"] = f["am"] or p["am"]             # label crops can carry the Amharic label
            continue
        if p["kind"] == "junk" or current is None:
            continue
        f = fields[current]
        f["am"] = (f["am"] + " " + p["am"]).strip()
        f["en"] = (f["en"] + " " + p["en"]).strip()
    return fields


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main(crop_path ="data/crop"  , CONF_MIN = CONF_MIN, LABEL_MIN = LABEL_MIN , txt_conf = CONF_MIN ):

    out_put_path = "id_result"

    ("data/crop", "--txt-conf", "0")
    os.environ["TESSDATA_PREFIX"] = TESSDATA

    files = sorted(p for p in pathlib.Path(crop_path).iterdir()
                   if p.suffix.lower() in {".png", ".jpg", ".jpeg"})
    if not files:
        raise SystemExit(f"No images found in {crop_path}")

    parsed, rows, txt_lines = [], [], []
    for path in files:
        raw = cv2.imread(str(path))
        if raw is None:
            print(f"skip (unreadable): {path.name}")
            continue
        img = prep(raw)
        am, am_c = ocr_conf(img, "amh")
        en, en_c = ocr_conf(img, "eng")
        p = parse_crop(am, am_c, en, en_c)
        parsed.append(p)

        # .txt output: one line per crop, each language kept only if its own
        # confidence is >= txt_conf. Amharic half first, then English half.
        am_half, en_half = read_label(am, en)
        pieces = []
        if am_c >= txt_conf and am_half:
            pieces.append(am_half)
        if en_c >= txt_conf and en_half:
            pieces.append(en_half)
        if pieces:
            txt_lines.append(" / ".join(pieces))
        rows.append(dict(file=path.name, kind=p["kind"], field=p.get("field", ""),
                         label_score=p["label_score"],
                         am_conf=round(am_c), en_conf=round(en_c),
                         am_raw=am, en_raw=en, am=p["am"], en=p["en"]))
        print(f"{path.name:<13} {p['kind']:<7} am_c={am_c:3.0f} en_c={en_c:3.0f} "
              f"lbl={p['label_score']:>3}  AM={p['am']!r}  EN={p['en']!r}")

    fields = assemble(parsed)

    print("\n=== FIELDS ===")
    for k, v in fields.items():
        print(f"{k:<12} {v['en']}   |   {v['am']}")

    # Save everything so you can inspect and tune offline
    with open(results_dir / f"{out_put_path}_crops.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    with open(results_dir / f"{out_put_path}_fields.json", "w", encoding="utf-8") as f:
        json.dump(fields, f, ensure_ascii=False, indent=2)
    with open(results_dir / f"{out_put_path}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines) + "\n")
    print(f"\nSaved {out_put_path}_crops.csv, {out_put_path}_fields.json and {out_put_path}.txt "
          f"({len(txt_lines)} lines at confidence >= {txt_conf:g})")
    


if __name__ == "__main__":
    main()