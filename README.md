# 🛕 DevaPath — AI Temple Guide
**Data Science Portfolio Project**

---

## Project Structure

```
devapath/
├── scrapers/
│   ├── 01_wikipedia_scraper.py   ← Temple history
│   ├── 02_timing_scraper.py      ← Aarti timings + BS4 tutorial
│   └── 03_overpass_fetcher.py    ← GPS coordinates (OpenStreetMap)
├── data_prep/
│   └── 04_merge_data.py          ← Sab data merge karo
├── data/
│   ├── raw/                      ← Scraped raw files
│   └── processed/                ← Final master JSON
├── requirements.txt
├── .env.example
└── README.md
```

---

## Step by Step Setup

### Step 1 — Environment Setup
```bash
# Virtual environment banao
python -m venv venv

# Activate karo (Windows)
venv\Scripts\activate

# Activate karo (Mac/Linux)
source venv/bin/activate

# Libraries install karo
pip install -r requirements.txt
```

### Step 2 — API Keys Setup
```bash
# .env.example copy karo
cp .env.example .env

# .env file open karo aur Groq key daalo
# Groq key free hai: https://console.groq.com
```

### Step 3 — Data Scraping (In Order!)
```bash
# 1. Wikipedia se history scrape karo
python scrapers/01_wikipedia_scraper.py

# 2. Aarti timing data save karo
python scrapers/02_timing_scraper.py

# 3. GPS coordinates fetch karo
python scrapers/03_overpass_fetcher.py

# 4. Sab data merge karo
python data_prep/04_merge_data.py
```

### Step 4 — App Chalao (coming next)
```bash
streamlit run app.py
```

---

## Data Sources (Sab Free!)
| Source | Kya milega | Cost |
|--------|-----------|------|
| Wikipedia API | Temple history | Free |
| Overpass API | GPS coordinates | Free |
| Manual Dataset | Aarti timings | Self-created |
| Groq API | LLM insights | Free tier |

---

## Tech Stack
- **Scraping**: BeautifulSoup4, Requests
- **AI/NLP**: LangChain, Groq (Llama 3), ChromaDB
- **App**: Streamlit, Folium
- **TTS**: gTTS (Google Text-to-Speech)
