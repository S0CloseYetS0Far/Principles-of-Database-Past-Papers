"""Match every question to the slide that best supports its answer.

Writes src/slides.json: {question_key: [deck_file, pdf_page, printed_slide_no]}.
Run once whenever questions change (needs the course slides folder):
    py src/slidemap.py "D:/IMAMU/Pricepls of data/slides"
Entries listed in OVERRIDES are fixed by hand and win over the automatic match.
"""
import sys, os, re, json, math, hashlib
from collections import Counter
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bank import Q
import bank_added  # noqa: F401  (appends to Q)

DECKS = {
    1: ["CS1370_Chapter1.pdf"], 2: ["CS1370_Chapter2.pdf"], 3: ["CS1370_Chapter3.pdf"],
    4: ["CS1370_Chapter4.pdf"], 5: ["CS1370_Chapter5.pdf"], 6: ["CS1370_Chapter6.pdf"],
    7: ["CS1370_Chapter7.pdf"], 8: ["CS370_Chapter8_DDL.pdf", "CS370_Chapter8_DML_part2.pdf"],
    9: ["CS1370_Chapter9.pdf"],
}
STOP = set("""the a an of to in and or is are be for on by with that this which what from as at it its
can may must each all any one two not no than then there their they will would should could has have had
following above below true false statement answer question given use using used into only also each
diagram relation relations table tables between more most other such these those how many does do""".split())

def qkey(q):
    return hashlib.sha1((q["q"] + "|" + str(q["ch"])).encode("utf-8")).hexdigest()[:10]

def words(s):
    s = re.sub(r"<[^>]+>", " ", s or "").lower()
    s = s.replace("_", " ")
    return [w for w in re.findall(r"[a-z][a-z0-9]{2,}", s) if w not in STOP]

def printed_no(text, page):
    nums = [int(x) for x in re.findall(r"(?m)^\s*(\d{1,2})\s*$", text)]
    for n in (page, page + 1):
        if n in nums:
            return n
    return page

def main(slide_dir):
    pages = {}  # ch -> list of (deck, pdfpage, printed, Counter)
    df = Counter(); N = 0
    for ch, decks in DECKS.items():
        pages[ch] = []
        for deck in decks:
            d = pymupdf.open(os.path.join(slide_dir, deck))
            for i, pg in enumerate(d):
                if i < 2:  # title + outline
                    continue
                t = pg.get_text()
                head = " ".join(l.strip() for l in t.splitlines() if l.strip() and not l.strip().isdigit())[:40].lower()
                if head.startswith(("summary", "outline", "chapter outline", "chapter summary")):
                    continue
                c = Counter(words(t))
                if sum(c.values()) < 6:
                    continue
                pages[ch].append((deck, i + 1, printed_no(t, i + 1), c))
                df.update(set(c)); N += 1
    idf = {w: math.log(N / (1 + n)) + 1 for w, n in df.items()}

    def vec(c):
        v = {w: (1 + math.log(n)) * idf.get(w, 1) for w, n in c.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1
        return {w: x / norm for w, x in v.items()}

    pvec = {ch: [(d, p, pr, vec(c)) for d, p, pr, c in lst] for ch, lst in pages.items()}
    out = {}
    for q in Q:
        parts = [q["q"], q.get("e", "")]
        if q["t"] == "mcq":
            parts.append(q["o"][q["a"]] if q["o"][0] != "True" else "")
        elif q["t"] == "reveal":
            parts.append(q["ans"])
        qv = vec(Counter(words(" ".join(parts))))
        best = max(pvec[q["ch"]], key=lambda r: sum(qv.get(w, 0) * x for w, x in r[3].items()))
        out[qkey(q)] = [best[0], best[1], best[2]]
    for idx, ref in OVERRIDES_IDX.items():
        code, page = ref.split(); deck = DECK_CODE[code]; page = int(page)
        txt = pymupdf.open(os.path.join(slide_dir, deck))[page - 1].get_text()
        out[qkey(Q[idx])] = [deck, page, printed_no(txt, page)]
    json.dump(out, open(os.path.join(HERE, "slides.json"), "w"), indent=0)
    print(len(out), "questions mapped")

# Hand-checked fixes, by question position in the bank: index -> (deck code, PDF page).
# Deck codes: C1..C9 = CS1370_ChapterN.pdf, D = Chapter 8 DDL, M = Chapter 8 DML part 2.
OVERRIDES_IDX = {
 8: "C1 27", 23: "C1 31", 24: "C1 18", 25: "C1 28", 26: "C1 18", 27: "C1 17", 28: "C1 28", 30: "C1 31", 32: "C1 19", 236: "C1 28",
 61: "C3 50", 62: "C3 10", 63: "C3 10", 64: "C3 17", 65: "C3 12", 68: "C3 19", 69: "C3 22", 70: "C3 36", 72: "C3 36", 75: "C3 6",
 76: "C3 46", 77: "C3 47", 78: "C3 47", 79: "C3 54", 81: "C3 18", 82: "C3 14", 83: "C3 39", 84: "C3 47", 85: "C3 46", 86: "C3 50",
 87: "C3 46", 88: "C3 12", 89: "C3 36", 90: "C3 19", 91: "C3 50", 92: "C3 47", 93: "C3 47", 94: "C3 41", 95: "C3 36", 96: "C3 46",
 97: "C3 46", 98: "C3 50", 99: "C3 8", 100: "C3 12", 101: "C3 46", 102: "C3 47", 103: "C3 36", 104: "C3 54", 105: "C3 47",
 106: "C3 46", 107: "C3 46", 108: "C3 46", 109: "C3 47", 110: "C3 50", 111: "C3 12", 112: "C3 32", 113: "C3 12", 114: "C3 8",
 115: "C3 46", 116: "C3 36", 129: "C3 10", 243: "C3 59", 247: "C3 59",
 117: "C4 14", 118: "C4 21", 119: "C4 21", 121: "C4 21", 122: "C4 9", 123: "C4 21", 124: "C4 21", 125: "C3 46", 126: "C3 12",
 127: "C3 47", 128: "C3 47", 130: "C4 14", 131: "C4 14", 132: "C4 21", 133: "C3 54", 134: "C3 32", 135: "C4 9", 136: "C3 54",
 137: "C3 54", 138: "C3 54", 244: "C4 34", 245: "C4 34", 246: "C4 34", 248: "C4 34", 249: "C4 34", 250: "C4 34",
 142: "C5 31", 143: "C5 31", 144: "C5 31", 145: "C5 31", 146: "C5 31", 147: "C5 27",
 152: "C6 2", 153: "C6 12", 156: "C6 12", 159: "C6 6", 162: "C6 6", 163: "C6 6",
 164: "C7 15", 165: "C7 10", 166: "C7 38", 167: "C7 47", 168: "C7 47", 170: "C7 8", 255: "C7 8", 256: "C7 10", 257: "C7 40",
 174: "M 33", 175: "M 33", 176: "D 25", 177: "M 6", 178: "D 18", 180: "M 21", 181: "M 30", 182: "D 18", 183: "D 19", 184: "M 7",
 185: "M 23", 186: "M 21", 188: "M 31", 189: "C7 29", 190: "M 15", 191: "M 21", 192: "M 28", 193: "M 31", 194: "C7 25",
 195: "M 22", 196: "M 6", 197: "M 21", 198: "M 7", 199: "D 20", 200: "D 20", 201: "M 19", 202: "M 34", 203: "C7 25", 205: "M 21",
 206: "M 22", 207: "D 20", 208: "M 13", 209: "C7 25", 210: "M 35", 211: "D 20", 212: "M 20", 213: "M 34", 214: "D 19", 215: "D 26",
 216: "D 27", 217: "M 27", 219: "M 43", 220: "M 28", 221: "M 7", 222: "M 21", 223: "M 15", 259: "D 19", 260: "M 28", 261: "M 10",
 262: "M 35", 263: "M 10",
 232: "C9 31", 233: "C9 47", 234: "C9 48",
}
DECK_CODE = {**{f"C{n}": f"CS1370_Chapter{n}.pdf" for n in (1, 2, 3, 4, 5, 6, 7, 9)},
             "D": "CS370_Chapter8_DDL.pdf", "M": "CS370_Chapter8_DML_part2.pdf"}

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "D:/IMAMU/Pricepls of data/slides")
