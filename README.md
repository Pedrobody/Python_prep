# BCG X | Data Science Technical Assessment Simulator

**Pedro: empieza por [EMPIEZA_AQUI.md](EMPIEZA_AQUI.md).**

A **fictional practice assessment**, not an official BCG X assessment. Complete it using **Python + Pandas + NumPy + scikit-learn**, without installing anything locally.

## Start in GitHub Codespaces (recommended)
1. Make a **private GitHub repository**, upload the contents of this folder (including dot-folders), then select **Code -> Codespaces -> Create codespace on main**. Alternatively, import this project into an existing private repo.
2. Codespaces automatically installs `requirements.txt` (Python 3.11). Open `notebooks/assessment.ipynb` to see tasks and trigger tests sequentially, or edit `assessment/solution.py` directly.
3. Execute tests for each stage in the terminal: `python -m pytest -q tests/test_01_clean.py` (then 02, 03, 04, 05). The initial tests **must fail** because starter functions are intentionally blank.
4. After each stage, use **Source Control -> Commit -> Sync Changes** in Codespaces. This makes your code accessible from the connected GitHub repository for review. Uncommitted changes in your cloud VM are not visible to ChatGPT.
5. Optionally use **Actions -> Mock assessment grade -> Run workflow** to run a given stage's tests on GitHub servers (only works after uploading the `.github` directory and enabling Actions).

## Mode A: guided practice
Work by stage, run its tests, inspect failures and ask for a hint. Keep a personal record of what you didn't remember. Use Python library docs if needed.

## Mode B: timed mock (100 minutes)
- 0–18 min: Stage 1, clean data
- 18–43 min: Stage 2, feature engineering
- 43–55 min: Stage 3, NumPy
- 55–85 min: Stage 4, sklearn
- 85–100 min: Stage 5, targeting + 3 oral questions

Tests can be run after each stage. A passing test is **not proof the solution is perfect**; edge cases and code quality can be reviewed separately. The exercises, rubrics, and mock timetable are original training materials, not BCG X's verified exam.

## Files
- `TASKS.md` — complete exam instructions and expected contracts, in English like a real interview.
- `assessment/solution.py` — the only file you should modify for coding.
- `data/*.csv` — realistic synthetic historical/live customer and event data.
- `tests/test_0*.py` — staged, automated public checks (pytest).
- `notebooks/assessment.ipynb` — interactive navigator to inspect data and run tests.
- `ANSWERS.md` — your business/ML interpretation; no solutions provided.

### Important
The `data/` directory contains **synthetic, non-sensitive** records. Never upload confidential employer/client data. The package intentionally excludes example solutions. When sharing progress, send the repo URL in chat after uploading; it cannot be inferred from the zip. Share only if comfortable with ChatGPT reviewing committed code.
