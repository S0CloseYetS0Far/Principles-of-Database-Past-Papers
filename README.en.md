**English** | [العربية](README.md)

# Principles of Database Bank

Practice site for **CS370 Introduction to Database**: 265 questions from past midterms, finals and quizzes, sorted by chapter (1–9) and, inside each chapter, from the newest exam to the oldest.

## How to use

### Open it

1. On this repository's page, click **Code → Download ZIP**, then unzip it. (Or, if you use git: `git clone` the repository.)
2. Double-click `index.html`. It opens in your browser.

That's it. It is a single file with no installation, and it works offline.

### Practice

1. **Pick a chapter** on the home page (or **All chapters mixed** for a mock exam). Each card shows how many questions it has and your progress.
2. **One question per page.** Click an option to answer it, or press **Show solution**. The correct answer turns green; a wrong pick turns red.
3. **The solution** shows the answer, a short explanation, and a box with:
   - **Slides:** the chapter and slide number in your slides folder that the answer comes from;
   - **Answer from:** how the answer was obtained (see the table below);
   - **Exam source:** the exam(s) the question appeared in.
4. **Move** with **← Prev** and **Next →** at the bottom, or click any square in the progress strip to jump.
5. **⤮ Shuffle** (top right of each question) randomizes the order; **↺ Newest first** puts it back. You can also turn shuffling on by default on the home page.
6. **Finish:** after the last question you get your score, then:
   - **Review my mistakes:** goes through only the questions you got wrong, with the answers shown;
   - **Retry them from scratch:** clears those answers so you can try again;
   - **Go to the skipped** ones you haven't answered.

- **Written questions** (SQL, mapping, normalization): work it out first, press **Show solution**, then mark yourself **Yes, I got it** or **No, review later**.
- **Drawing questions** (ER/EER diagrams): there's no model answer. Draw it on paper and compare with the notation slide shown. They aren't scored.
- **Question types:** on the home page you can turn multiple choice, true/false, written and drawing questions on or off.
- **Keyboard:** `←` `→` move, `1`–`4` or `A`–`D` pick an option, `T` / `F` for true/false, `Enter` shows the solution.
- **Theme:** the button at the top right switches between system, light and dark.

Your progress is saved in the browser on your device. It won't carry over to another browser or device. **Reset my answers** on the home page clears it.

## Where the answers come from

Every question shows which exam it came from and where its answer came from:

| Label | Meaning |
|---|---|
| Official key | Answer key printed in the exam file |
| Graded paper | A student's paper the instructor marked |
| Marked + checked | Answer selected on a quiz screenshot, checked against the slides |
| From slides | No answer on the paper; taken from the chapter slides |
| Worked out | No answer on the paper; worked out from the question's own tables or diagram |
| No model answer | Drawing question; draw it yourself (not scored) |

The full source list is at the bottom of the page. **Worked out** answers are the ones most worth double-checking.

## Editing the questions

Questions live in `src/bank.py` (newer ones in `src/bank_added.py`), the page template in `src/page.html`, exam diagrams in `src/img/`, and each question's slide reference in `src/slides.json` (made by `src/slidemap.py` from the slides folder, with hand-checked fixes). Rebuild with:

```bash
pip install pymupdf
python src/build.py
```

This regenerates `index.html`.
