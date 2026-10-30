import json, base64, pymupdf, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from bank import Q
import bank_added  # appends the later questions to Q
HERE = os.path.dirname(__file__)

SOURCES = {
 "M23S":  ("Midterm, Summer 2023", "Exams/Mid/Mid-CS370-3rd-2023-MA.pdf", "Official model answer inside the file"),
 "M24_2": ("Midterm, 2nd semester 2024", "Exams/Mid/2024/Midterm_2nd_2024.pdf", "Official answer key inside the file"),
 "M23_1": ("Midterm, 1st semester 2023 (same paper as 2021)", "Exams/Mid/Midterm_S1_2023_Manal Alsabhan.pdf + Exams/Mid/Mid1-CS370-1st-2021-MA/", "Graded student papers, full marks on these parts"),
 "M24_1": ("Midterm, 1st semester 2024", "Exams/Mid/2024/Midterm_1st_2024.pdf", "No answers on the paper; answers from the slides"),
 "M25_2": ("Midterm, 2nd semester 2025", "Exams/Mid/2025/Midterm_2nd_2025.pdf", "No answers on the paper; answers from the slides and the diagram"),
 "M25_3": ("Midterm, 3rd semester 2025", "Exams/Mid/2025/Midterm_3rd_2025.pdf", "No answers on the paper; answers from the slides and the diagram"),
 "F23_1": ("Final, 1st semester 2023", "Exams/Final/2023/Final_1st_2023.pdf", "One answer boxed on the paper; the rest from the slides and the diagram"),
 "F24_1": ("Final, 1st semester 2024", "Exams/Final/2024/Final_1st_2024.pdf", "No answers on the paper; answers from the slides and worked out from the tables"),
 "F25_2": ("Final, 2nd semester 2025", "Exams/Final/2025/Final_2nd_2025.pdf", "No answers on the paper; answers from the slides and worked out from the tables"),
 "F25_3": ("Final, 3rd semester 2025", "Exams/Final/2025/Final_3rd_2025.pdf", "No answers on the paper; answers from the slides and worked out from the tables"),
 "Q23_2": ("Quiz 2, 2nd semester 2023 (Dr. Dalal)", "Exams/Quiz/2023/Quiz2_2nd_2023_Female_Dr.Dalal_Alduwaila.pdf", "Blackboard screenshots with selected answers; each one re-checked"),
 "Q24_S": ("Quiz 1, Summer 2024", "Exams/Quiz/2024/QUIZ1_SUMMER 2024.pdf", "Microsoft Forms screenshots with selected answers; checked against the slides"),
 "Q24_1": ("Quiz 1, 1st semester 2024", "Exams/Quiz/2024/Quiz1_1st_2024.pdf", "Blackboard screenshots with selected answers; checked against the slides (one corrected)"),
 "Q24_1b":("Quiz 2, 1st semester 2024", "Exams/Quiz/2024/Quiz2_1st_2024.pdf", "No answers on the paper; worked out from the tables"),
 "Q25_1": ("Quiz 1, 1st semester 2025/2026", "Exams/Quiz/2025/Quiz1-1st Semester 2025_2026.pdf", "No answers on the paper; answers from the slides"),
 "Q25_2": ("Quiz 1, 2nd semester 2025", "Exams/Quiz/2025/Quiz1_2nd_2025.pdf", "No answers on the paper; answers from the slides"),
 "Q25_3": ("Quiz 1, 3rd semester 2025", "Exams/Quiz/2025/Quiz1_3rd_2025.pdf", "No answers on the paper; answers from the slides and the diagram"),
 "Q25_3b":("Quiz 2, 3rd semester 2025", "Exams/Quiz/2025/Quiz2_3rd_2025.pdf", "No answers on the paper (the red mark on item 1 is a redaction); answers from the slides"),
 "Q26_2": ("Quiz 1, 2nd semester 2026", "Exams/Quiz/2026/Quiz1_2nd_2026.pdf", "Written questions; answers from the slides"),
 "Q22":   ("Quiz 1, Fall 2022", "Exams/Quiz/Quiz1-Fall2022/", "Graded student paper; answers taken from the parts marked correct"),
 "Q21":   ("Quiz 1, Fall 2021 (Ms. Amal Alamr)", "Exams/Quiz/Quiz1-Ms.AmalAlamr-Fall2021-cs370/", "Graded student paper; both MCQs were marked wrong, so the correct choice is from the slides"),
 "M26":   ("Midterm 1, 2nd semester 2026", "Exams/Mid/Midterm1_2nd_2026.pdf", "No answers on the paper; answers from the slides"),
 "M21_2": ("Midterm 2, 1st semester 2021", "Exams/Mid/Mid2-CS370-1st-2021-MA/", "Official model answer (photos of the answer PDF)"),
}
SKIPPED = [
 "Model answers for the drawing questions (ER/EER diagrams, three-schema architecture). The questions are in the bank, but there's no single right drawing to check against.",
 "Mapping questions whose diagram is too blurry or cut off (insurance company, hospital, Father/Child, Lecturer/Course).",
 "SQL question 4 of Midterm 2, 1st semester 2021 — that page wasn't photographed.",
 "Quiz 1, 3rd semester 2024 — the file contains question stems only, no answer choices.",
 "Questions where the photo is cut off or the answer is genuinely ambiguous (e.g. the podcast 'Entity vs Instance' version in Quiz 1 2nd 2025, the 'NOT a type of data model' question in Quiz 1 Summer 2024, the Magazine normalization in Final 1st 2024).",
 "The Arabic recollection sheet on page 3 of Final_1st_2023.pdf.",
]
CHAPTERS = {  # title, deck(s), slide count
 1: ("Databases and Database Users", "CS1370_Chapter1.pdf", 32),
 2: ("Database System Concepts and Architecture", "CS1370_Chapter2.pdf", 23),
 3: ("Data Modeling Using the ER Model", "CS1370_Chapter3.pdf", 60),
 4: ("The Enhanced ER (EER) Model", "CS1370_Chapter4.pdf", 36),
 5: ("The Relational Model and Constraints", "CS1370_Chapter5.pdf", 35),
 6: ("ER/EER-to-Relational Mapping", "CS1370_Chapter6.pdf", 29),
 7: ("Relational Algebra and Calculus", "CS1370_Chapter7.pdf", 69),
 8: ("SQL: Definition, Constraints, Queries, Views", "CS370_Chapter8_DDL.pdf + CS370_Chapter8_DML_part2.pdf", 70),
 9: ("Functional Dependencies and Normalization", "CS1370_Chapter9.pdf", 49),
}
DECKS = {"CS370_Chapter8_DDL.pdf": 8, "CS370_Chapter8_DML_part2.pdf": 8,
         **{f"CS1370_Chapter{n}.pdf": n for n in (1, 2, 3, 4, 5, 6, 7, 9)}}
# When each exam was given (year + .2 spring / .5 summer / .8 fall), used to sort newest first.
DATES = {"M26": 2026.2, "Q26_2": 2026.2, "Q25_1": 2025.8,
         "F25_3": 2025.5, "M25_3": 2025.5, "Q25_3": 2025.5, "Q25_3b": 2025.5,
         "F25_2": 2025.2, "M25_2": 2025.2, "Q25_2": 2025.2,
         "F24_1": 2024.8, "M24_1": 2024.8, "Q24_1": 2024.8, "Q24_1b": 2024.8, "Q24_S": 2024.5, "M24_2": 2024.2,
         "F23_1": 2023.8, "M23_1": 2023.8, "M23S": 2023.5, "Q23_2": 2023.2, "Q22": 2022.8, "Q21": 2021.8, "M21_2": 2021.8}
SLIDES = json.load(open(os.path.join(HERE, "slides.json")))
from slidemap import qkey

# embed images as compressed JPEG data URIs
imgs = {}
for q in Q:
    k = q.get("img")
    if k and k not in imgs:
        pix = pymupdf.Pixmap(os.path.join(HERE, "img", k + ".png"))
        if pix.alpha: pix = pymupdf.Pixmap(pix, 0)
        if pix.width > 1000:
            pix = pymupdf.Pixmap(pix, 1000, int(pix.height * 1000 / pix.width), None)
        imgs[k] = "data:image/jpeg;base64," + base64.b64encode(pix.tobytes("jpg", jpg_quality=82)).decode()

out = []
for i, q in enumerate(Q):
    for s in q["s"]: assert s in SOURCES and s in DATES, s
    r = dict(id=qkey(q), ch=q["ch"], q=q["q"], e=q.get("e", ""), p=q["p"], sl=SLIDES[qkey(q)],
             from_=sorted(q["s"], key=lambda s: -DATES[s]), _i=i)
    if q["t"] == "mcq":
        r.update(t="tf" if q["o"] == ["True", "False"] else "mcq", o=q["o"], a=q["a"])
    elif q["t"] == "reveal":
        r.update(t="short", a=q["ans"])
    else:
        r.update(t="draw")
    if q.get("img"): r["img"] = q["img"]
    if q.get("ctx"): r["ctx"] = q["ctx"]
    r["_d"] = DATES[r["from_"][0]]
    out.append(r)
# chapter order, then newest exam first; ties keep the bank's original order
out.sort(key=lambda r: (r["ch"], -r["_d"], r["_i"]))
for r in out:
    r["from"] = r.pop("from_"); del r["_d"], r["_i"]
assert len({r["id"] for r in out}) == len(out), "duplicate question ids"

data = dict(questions=out,
            sources={k: dict(label=v[0], file=v[1].split("Exams/", 1)[1], how=v[2], date=DATES[k]) for k, v in SOURCES.items()},
            chapters={k: dict(title=v[0], deck=v[1], slides=v[2]) for k, v in CHAPTERS.items()},
            decks=DECKS, img=imgs, skipped=SKIPPED)
tpl = open(os.path.join(HERE, "page.html"), encoding="utf-8").read()
page = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
standalone = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
              "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
              "<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n"
              "</head>\n<body>\n" + page + "\n</body>\n</html>\n")
open(os.path.join(HERE, "..", "index.html"), "w", encoding="utf-8").write(standalone)
if len(sys.argv) > 1:  # optional: page without the HTML wrapper (for the hosted version)
    open(sys.argv[1], "w", encoding="utf-8").write(page)
from collections import Counter
print(len(out), "questions", dict(sorted(Counter(r["ch"] for r in out).items())),
      dict(Counter(r["t"] for r in out)), "size", len(page) // 1024, "KB")
