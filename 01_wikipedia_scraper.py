"""
================================================
STEP 1 — Wikipedia Scraper (API Version)
================================================
Yeh script famous Indian temples ki history
Wikipedia ke OFFICIAL API se fetch karegi.

API scraping HTML scraping se BETTER hai:
  - Official support hai Wikipedia ka
  - Clean text milta hai (no HTML parsing)
  - Block nahi hota
  - BeautifulSoup ki zaroorat nahi Wikipedia ke liye

Wikipedia ke 2 APIs use karenge:
  1. REST API    → quick summary
  2. MediaWiki API → full introductory text

NOTE: BeautifulSoup ka use 02_timing_scraper.py
me dikhaya gaya hai (temple websites ke liye)

Run karo:
  python scrapers/01_wikipedia_scraper.py
================================================
"""

import requests
import json
import time
import re
import os


# ================================================
# TEMPLE LIST — jinhe scrape karna hai
# ================================================
TEMPLES = [
    # --- Uttar Pradesh ---
    {"name": "Kashi Vishwanath Temple",    "wiki": "Kashi_Vishwanath_Temple",         "city": "Varanasi",   "state": "Uttar Pradesh", "deity": "Shiva"},
    {"name": "Banke Bihari Temple",         "wiki": "Banke_Bihari_Mandir",             "city": "Vrindavan",  "state": "Uttar Pradesh", "deity": "Krishna"},
    {"name": "Krishna Janmabhoomi Temple",  "wiki": "Krishna_Janmabhoomi",             "city": "Mathura",    "state": "Uttar Pradesh", "deity": "Krishna"},

    # --- Uttarakhand ---
    {"name": "Kedarnath Temple",            "wiki": "Kedarnath_Temple",                "city": "Kedarnath",  "state": "Uttarakhand",   "deity": "Shiva"},
    {"name": "Badrinath Temple",            "wiki": "Badrinath_Temple",                "city": "Badrinath",  "state": "Uttarakhand",   "deity": "Vishnu"},

    # --- Gujarat ---
    {"name": "Somnath Temple",              "wiki": "Somnath_temple",                  "city": "Veraval",    "state": "Gujarat",       "deity": "Shiva"},
    {"name": "Dwarkadheesh Temple",         "wiki": "Dwarkadhish_Temple",              "city": "Dwarka",     "state": "Gujarat",       "deity": "Krishna"},

    # --- Andhra Pradesh ---
    {"name": "Tirupati Balaji Temple",      "wiki": "Tirumala_Venkateswara_Temple",    "city": "Tirupati",   "state": "Andhra Pradesh","deity": "Vishnu"},

    # --- Tamil Nadu ---
    {"name": "Meenakshi Amman Temple",      "wiki": "Meenakshi_Amman_Temple",          "city": "Madurai",    "state": "Tamil Nadu",    "deity": "Meenakshi"},
    {"name": "Brihadeeswarar Temple",       "wiki": "Brihadisvara_Temple,_Thanjavur",  "city": "Thanjavur",  "state": "Tamil Nadu",    "deity": "Shiva"},

    # --- Odisha ---
    {"name": "Jagannath Temple",            "wiki": "Jagannath_Temple,_Puri",          "city": "Puri",       "state": "Odisha",        "deity": "Jagannath"},

    # --- J&K ---
    {"name": "Vaishno Devi Temple",         "wiki": "Vaishno_Devi",                    "city": "Katra",      "state": "J&K",           "deity": "Vaishno Devi"},

    # --- Rajasthan ---
    {"name": "Nathdwara Temple",            "wiki": "Shrinathji_temple",               "city": "Nathdwara",  "state": "Rajasthan",     "deity": "Krishna"},
]


# Wikipedia API ke liye official User-Agent
HEADERS = {
    'User-Agent': 'DevaPath/1.0 (Educational Portfolio Project; student@example.com)'
}


def clean_text(text):
    """Unwanted characters aur extra spaces remove karo"""
    text = re.sub(r'\[\d+\]', '', text)           # [1][2] references
    text = re.sub(r'\[citation needed\]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)         # Multiple newlines
    text = re.sub(r'  +', ' ', text)               # Double spaces
    return text.strip()


# ================================================
# API 1: Wikipedia REST API — Quick Summary
# ================================================
def get_wikipedia_summary(wiki_title):
    """
    Wikipedia REST API se summary lo.

    Endpoint:
      GET https://en.wikipedia.org/api/rest_v1/page/summary/{title}

    Response me milega:
      extract  → clean summary paragraph
      thumbnail → temple ki image URL
    """
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_title}"

    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    data = response.json()

    return {
        "summary":      data.get("extract", ""),
        "thumbnail":    data.get("thumbnail", {}).get("source", ""),
        "description":  data.get("description", ""),
    }


# ================================================
# API 2: MediaWiki API — Full Introductory Text
# ================================================
def get_wikipedia_full_extract(wiki_title):
    """
    MediaWiki API se poora introductory section lo.

    Parameters samjho:
      action=query     → kuch query karna hai
      prop=extracts    → text content chahiye
      exintro=1        → sirf introduction (baaki sections nahi)
      explaintext=1    → plain text (HTML nahi)
      titles=TITLE     → kaunsa Wikipedia page
      format=json      → JSON response

    Endpoint:
      GET https://en.wikipedia.org/w/api.php?action=query&...
    """
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action":          "query",
        "prop":            "extracts",
        "exintro":         1,
        "explaintext":     1,
        "titles":          wiki_title,
        "format":          "json",
        "exsectionformat": "plain"
    }

    response = requests.get(api_url, params=params, headers=HEADERS, timeout=15)
    response.raise_for_status()
    data = response.json()

    # Response nested hota hai — pages dict ke andar
    # page ID pata nahi hota pehle se, isliye next(iter()) use karo
    pages   = data.get("query", {}).get("pages", {})
    page    = next(iter(pages.values()))
    extract = page.get("extract", "")

    return clean_text(extract)


# ================================================
# MAIN SCRAPER — dono APIs combine karo
# ================================================
def scrape_wikipedia(temple_info):
    """
    Wikipedia se temple ka complete text data fetch karo.

    Strategy:
    1. REST API se summary lo (quick)
    2. MediaWiki API se full text lo (detailed)
    3. Jo bhi zyada content ho use rakhho

    Agar koi fail ho toh dusra try karo.
    """
    wiki_title = temple_info['wiki']

    try:
        # --- Summary ---
        summary_data = get_wikipedia_summary(wiki_title)
        summary      = summary_data.get("summary", "")
        thumbnail    = summary_data.get("thumbnail", "")

        # --- Full Extract ---
        full_extract = get_wikipedia_full_extract(wiki_title)

        # Jo bhi zyada content ho use history ke liye use karo
        history = full_extract if len(full_extract) > len(summary) else summary

        result = {
            "name":      temple_info['name'],
            "city":      temple_info['city'],
            "state":     temple_info['state'],
            "deity":     temple_info.get('deity', ''),
            "wiki_url":  f"https://en.wikipedia.org/wiki/{wiki_title}",
            "thumbnail": thumbnail,
            "history":   history[:3000],
            "status":    "success"
        }

        char_count = len(history)
        print(f"  ✅ {temple_info['name']} ({char_count} chars)")
        return result

    except requests.exceptions.HTTPError as e:
        print(f"  ❌ {temple_info['name']} — HTTP {e.response.status_code}")
        return {
            "name": temple_info['name'], "city": temple_info['city'],
            "state": temple_info['state'], "status": "failed", "error": str(e)
        }
    except Exception as e:
        print(f"  ❌ {temple_info['name']} — {e}")
        return {
            "name": temple_info['name'], "city": temple_info['city'],
            "state": temple_info['state'], "status": "failed", "error": str(e)
        }


# ================================================
# MAIN — Sab temples ke liye run karo
# ================================================
def main():
    os.makedirs("data/raw", exist_ok=True)

    print("=" * 50)
    print("  🛕 Wikipedia API Scraper")
    print("=" * 50)

    all_results = []
    failed      = []

    for idx, temple in enumerate(TEMPLES, 1):
        print(f"\n[{idx:02d}/{len(TEMPLES)}] {temple['name']}...")

        result = scrape_wikipedia(temple)
        all_results.append(result)

        if result['status'] == 'failed':
            failed.append(temple['name'])

        # Respectful scraping — 1.5 second wait
        time.sleep(1.5)

    # Save to JSON
    output_file = "data/raw/wikipedia_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    success_count = len(TEMPLES) - len(failed)
    print("\n" + "=" * 50)
    print(f"  ✅ Success: {success_count}/{len(TEMPLES)}")
    print(f"  📁 Saved:   {output_file}")
    if failed:
        print(f"  ❌ Failed:  {', '.join(failed)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
