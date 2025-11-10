# Data Saving Options for Experiment

## Current CSV Approach ✅

### What You Can Measure with Current Data

The current CSV data saving system **is fully capable** of supporting the types of tests you want to conduct. Here's what you can measure:

#### 1. **Reading Behavior**
- Reading time per article
- Scroll depth (engagement)
- Summary views (synchronous mode)
- Summary viewing time during reading

#### 2. **AI Summary Engagement** ⭐
- **Time spent viewing summary** (`time_spent_seconds` in `summary_viewing` phase)
- Pre-reading vs post-reading comparison
- Integrated vs segmented comparison
- Correlation with performance

#### 3. **Recall Performance**
- Free recall text (qualitative analysis)
- Sentence/word/character counts
- Confidence ratings
- Perceived difficulty
- Time spent on recall
- Paste attempts (data quality)

#### 4. **MCQ Performance**
- Correct/incorrect answers
- Performance by article
- Performance by condition (timing, structure)
- Relationship to summary viewing time

#### 5. **AI Trust & Demographics**
- Trust scores
- AI tool usage patterns
- Participant characteristics
- Correlation with performance

### Current System: Pros & Cons

**✅ Pros:**
- **Simple & readable** - Easy to open in Excel/Google Sheets
- **No database setup** - Works immediately
- **Good for small-medium studies** - Perfect for dozens to hundreds of participants
- **Easy backup** - Just copy the folder
- **Human-readable** - Can inspect data directly
- **Easy to share** - Send CSV files to collaborators
- **Works with all analysis tools** - Python, R, Excel, SPSS

**⚠️ Cons:**
- **Not ideal for very large studies** - Gets slower with thousands of participants
- **No concurrent write protection** - Rare issue, but possible with multiple simultaneous submissions
- **No built-in data validation** - Need to check data quality manually
- **No real-time queries** - Need to load files into analysis tools
- **Cloud deployment** - Data stored on server, need to export regularly

### Recommendation for Current Scale

**For experiments with < 500 participants: CSV is PERFECT** ✅

The current CSV system is:
- Efficient enough
- Easy to manage
- Suitable for academic research
- Compatible with all analysis tools
- No additional setup needed

## Alternative Options (If Needed)

### Option 1: SQLite Database (Recommended for 500-5000 participants)

**What it is:** Lightweight file-based database (single file, like CSV but structured)

**Pros:**
- ✅ More efficient for larger datasets
- ✅ Built-in data integrity
- ✅ SQL queries (complex analysis)
- ✅ Still file-based (easy backup)
- ✅ No server setup needed
- ✅ Easy to export to CSV

**Cons:**
- ⚠️ Requires database setup
- ⚠️ Less human-readable (need database browser)
- ⚠️ Slightly more complex code

**When to use:**
- 500-5000 participants
- Need complex queries
- Want data validation
- Still want file-based storage

**Implementation effort:** Medium (2-3 days)

---

### Option 2: PostgreSQL/MySQL (Recommended for 5000+ participants or cloud deployment)

**What it is:** Full database server (separate from web app)

**Pros:**
- ✅ Highly scalable (millions of records)
- ✅ Concurrent access safe
- ✅ Advanced features (transactions, replication)
- ✅ Real-time queries
- ✅ Best for cloud deployment

**Cons:**
- ⚠️ Requires database server setup
- ⚠️ More complex configuration
- ⚠️ Need to manage database separately
- ⚠️ Cloud databases cost money (free tiers available)

**When to use:**
- 5000+ participants
- Cloud deployment (Render, Railway, etc.)
- Need real-time data access
- Multiple researchers accessing data

**Implementation effort:** High (1 week)

---

### Option 3: Cloud Storage (AWS S3, Google Cloud Storage)

**What it is:** Store CSV files in cloud storage instead of local filesystem

**Pros:**
- ✅ Persistent storage (survives server restarts)
- ✅ Easy backup
- ✅ Can still use CSV format
- ✅ Accessible from anywhere

**Cons:**
- ⚠️ Requires cloud account
- ⚠️ Small cost (usually very cheap)
- ⚠️ Need to download files to analyze

**When to use:**
- Cloud deployment
- Want CSV simplicity
- Need persistent storage
- Want automatic backups

**Implementation effort:** Low (1 day)

---

## My Recommendation

### For Your Current Experiment:

**Stick with CSV** ✅

Reasons:
1. **Your data is perfect for CSV** - All measurements (time, text, scores) work great in CSV
2. **Easy analysis** - You can immediately analyze in Python/R/Excel
3. **No setup complexity** - Works out of the box
4. **Academic standard** - Most research uses CSV/Excel for data sharing
5. **All your tests are supported** - Reading time, summary viewing time, recall, MCQ all saved perfectly

### When to Consider Upgrading:

**Consider SQLite if:**
- You have > 500 participants
- You want to run complex queries directly on data
- You want automatic data validation

**Consider PostgreSQL if:**
- You have > 5000 participants
- You're deploying to cloud long-term
- Multiple researchers need real-time access
- You need advanced features

**Consider Cloud Storage if:**
- You're deploying to cloud
- You want automatic backups
- You want to keep CSV simplicity

## Data Analysis Workflow

### Current CSV Workflow:

1. **Collect data** → CSV files in `experiment_data/`
2. **Export data** → Use `/admin/export` or copy folder
3. **Load in Python/R** → `pd.read_csv()` or `read.csv()`
4. **Analyze** → All standard analysis tools work
5. **Share** → Send CSV files to collaborators

### Example Analysis:

```python
import pandas as pd

# Load all participant data
participants = ['P001', 'P002', 'P003']  # Add all IDs
all_data = []

for pid in participants:
    df = pd.read_csv(f'experiment_data/{pid}_log.csv')
    all_data.append(df)

combined = pd.concat(all_data)

# Analyze summary viewing time
summary_times = combined[combined['phase'] == 'summary_viewing']
avg_time = summary_times.groupby(['mode', 'structure'])['time_spent_seconds'].mean()
print(avg_time)

# Analyze recall performance
recall_data = combined[combined['phase'] == 'recall_response']
avg_sentences = recall_data.groupby('article_key')['sentence_count'].mean()
print(avg_sentences)

# Analyze MCQ performance
mcq_data = combined[combined['phase'] == 'mcq_responses']
# Parse JSON and calculate accuracy
# ... (see CSV_DATA_INTERPRETATION.md for examples)
```

## Conclusion

**Your current CSV data saving is excellent for your experiment.** It supports all the tests you want to conduct, is easy to use, and works with all analysis tools. 

**No changes needed unless:**
- You expect > 500 participants (consider SQLite)
- You're deploying to cloud long-term (consider cloud storage)
- You need real-time data access (consider database)

For now, **focus on running your experiment** - the data saving is working perfectly! 🎉

