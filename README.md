# 🛕 DevaPath — AI Temple Guide
**Data Science Portfolio Project**

---

## Project Structure

```
devapath/
├── scrapers/
│   ├── 01_wikipedia_scraper.py   ← Temple history
│   ├── 02_timing_scraper.py      ← Aarti timings 
│   └── 03_overpass_fetcher.py    ← GPS coordinates (OpenStreetMap)
├── data_prep/
│   └── 04_merge_data.py          ← merged json data
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
# .env.example copy krna hai
cp .env.example .env

# .env file open krke aur Groq key dalni hai
# Groq key free hai: https://console.groq.com
```

### Step 3 — Data Scraping (In Order!)
```bash
# 1. Wikipedia se history scrape hogi
python scrapers/01_wikipedia_scraper.py

# 2. Aarti timing data yha se ayega
python scrapers/02_timing_scraper.py

# 3. GPS coordinates yaha milenga
python scrapers/03_overpass_fetcher.py

# 4. esme sara merged data hai
python data_prep/04_merge_data.py
```

### Step 4 — App chaleha
--esse phale folder ke andar steamlit ko "pip install stremalit" krna padega
```bash
streamlit run app.py
```

---

## Data Sources (Sab Free!)
| Source | goods | Cost |
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
