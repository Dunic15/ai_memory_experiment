### 3. Verify Setup

```bash
python setup-script.py
```

This script checks Python/Flask versions, the presence of all templates, creates `experiment_data/`, and writes a `config.py` with default timing values (including the two break durations).

### 4. Copy Files

...

### 5. Run the Application

...

**Phase 2: Reading & Testing (~70 min)**

1. Read article (up to 12 min soft limit, 15 min hard cap)
2. Answer multiple-choice questions (up to 7 min)
3. **Break after reading (pre-test)** — 5 min
4. **Break after test (before next article)** — 30 s
5. Next article or test

...

**Timing Enforcement**

- Reading time soft limit (12 min) and hard cap (15 min)
- Pre-reading minimum time (90 s)
- Recall and MCQ time limits (3 min and 7 min)
- 5-minute pre-test break and 30-second inter-article break are enforced automatically

...

**To Change Timing:**

Modify constants in `config.py` (created by `setup-script.py`):
```python
READING_TIME_SOFT_LIMIT = 12 * 60 * 1000  # 12 minutes
READING_TIME_HARD_CAP   = 15 * 60 * 1000  # 15 minutes
PRE_READING_MIN_TIME    = 90 * 1000       # 90 seconds
RECALL_TIME_LIMIT       = 3 * 60 * 1000   # 3 minutes
MCQ_TIME_LIMIT          = 7 * 60 * 1000   # 7 minutes
BREAK_AFTER_READING_MS  = 5 * 60 * 1000   # 5 minutes (pre-test break)
BREAK_BETWEEN_ARTICLES_MS = 30 * 1000     # 30 seconds (after-test break)
```
