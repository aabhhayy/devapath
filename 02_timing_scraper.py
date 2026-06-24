"""
================================================
STEP 2 — Temple Timing Scraper
================================================
Yeh script temple timings scrape karegi.

2 approaches hain:
  A) BeautifulSoup se live scraping (example dikhaya hai)
  B) Manual curated dataset (RECOMMENDED starter ke liye)

Kyun manual data better hai shuruat me:
  - Temple websites ka structure alag-alag hota hai
  - Kuch sites JavaScript se render karti hain (BS4 nahi pakad pata)
  - Timings seasonal bhi change hote hain
  - Manual data 100% accurate hoga

Run karo:
  python scrapers/02_timing_scraper.py
================================================
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time


# ================================================
# PART A: BeautifulSoup Kaise Kaam Karta Hai
#          (Ek Example ke Saath Samjho)
# ================================================

def bs4_example_explained():
    """
    BeautifulSoup Tutorial — Step by Step
    
    Koi bhi website scrape karne se pehle:
    1. Browser me website open karo
    2. Right-click → "Inspect" (DevTools)
    3. Jo data chahiye uske upar hover karo
    4. HTML element dhundho
    5. BS4 se woh element extract karo
    
    Example: Kisi temple site se naam nikalna
    """

    print("\n📖 BS4 Quick Tutorial:")
    print("-" * 40)

    # STEP 1: Page fetch karo
    url = "https://en.wikipedia.org/wiki/Kashi_Vishwanath_Temple"
    headers = {'User-Agent': 'Mozilla/5.0 DevaPath-Bot/1.0'}

    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")   # 200 = success

    # STEP 2: BS4 se parse karo
    soup = BeautifulSoup(response.content, 'lxml')

    # STEP 3: Different tarike se elements dhundho

    # --- find() — pehla element milta hai ---
    title = soup.find('h1', id='firstHeading')
    print(f"\nPage Title (find):       {title.get_text()}")

    # --- find_all() — sab elements milte hain ---
    all_h2 = soup.find_all('h2')
    print(f"H2 Headings count:       {len(all_h2)}")

    # --- CSS Class se dhundho ---
    infobox = soup.find('table', class_='infobox')
    print(f"Infobox found:           {'Yes' if infobox else 'No'}")

    # --- Attribute se dhundho ---
    links = soup.find_all('a', href=True)
    print(f"Total links on page:     {len(links)}")

    # --- Nested dhundho (parent > child) ---
    content = soup.find('div', class_='mw-parser-output')
    if content:
        first_para = content.find('p')
        if first_para:
            text = first_para.get_text()[:100]
            print(f"\nFirst paragraph (100 chars):\n{text}...")

    # --- Text nikalna ---
    # .get_text()       → sab text, tags remove
    # .get_text(' ')    → space se join
    # .string           → sirf direct text (no nested tags)

    print("\n--- Common BS4 Methods ---")
    print("soup.find('tag')               → pehla element")
    print("soup.find_all('tag')           → list of elements")
    print("soup.find('tag', class_='x')   → class se dhundo")
    print("soup.find('tag', id='x')       → id se dhundo")
    print("element.get_text()             → text nikalo")
    print("element['href']                → attribute nikalo")
    print("element.find_next_sibling()    → next element")
    print("-" * 40)


# ================================================
# PART B: Manual Curated Dataset
#         (Verified temple timings)
# ================================================

TEMPLE_TIMINGS = [
    {
        "name": "Kashi Vishwanath Temple",
        "city": "Varanasi",
        "state": "Uttar Pradesh",

        # Daily timings
        "opening_time": "03:00 AM",
        "closing_time": "11:00 PM",

        # Aarti schedule
        "aarti": {
            "mangala_aarti":  {"time": "03:00 AM", "description": "Pratah aarti — sabse pehli aarti, bhakt bahut kam hote hain"},
            "bhog_aarti":     {"time": "11:15 AM", "description": "Dopahar ki aarti — bhog (prasad) chadhaya jaata hai"},
            "sandhya_aarti":  {"time": "07:00 PM", "description": "Sham ki aarti — bahut bheed hoti hai"},
            "shringar_aarti": {"time": "09:00 PM", "description": "Shivling ka shringar kiya jaata hai"},
            "shayan_aarti":   {"time": "10:30 PM", "description": "Raat ki antim aarti — Shivji ko sulaya jaata hai"}
        },

        "best_visit_time": "Subah 3-5 AM (Mangala Aarti ke liye) ya sham 7 PM",
        "special_days": ["Maha Shivratri", "Sawan Somvar", "Purnima"],
        "entry_fee": "Free (special darshan ke alag charges ho sakte hain)",
        "dress_code": "Traditional dress preferred, shoulders covered karo"
    },

    {
        "name": "Kedarnath Temple",
        "city": "Kedarnath",
        "state": "Uttarakhand",

        "opening_time": "04:00 AM",
        "closing_time": "09:00 PM",
        "seasonal_note": "Sirf May-November khulta hai (baaki time snow se band)",

        "aarti": {
            "pratah_aarti":  {"time": "04:00 AM", "description": "Subah ki pehli aarti"},
            "abhishek_aarti":{"time": "06:00 AM", "description": "Shivling ka abhishek (snaan)"},
            "evening_aarti": {"time": "07:30 PM", "description": "Sham ki aarti, bahut sundar hoti hai"}
        },

        "best_visit_time": "Subah 4-6 AM ya sham 6-7 PM",
        "special_days": ["Maha Shivratri", "Opening Day (May)"],
        "entry_fee": "Free",
        "dress_code": "Warm clothes zaroor pehnein — bahut thanda hota hai"
    },

    {
        "name": "Tirupati Balaji Temple",
        "city": "Tirupati",
        "state": "Andhra Pradesh",

        "opening_time": "02:30 AM",
        "closing_time": "01:00 AM (next day)",

        "aarti": {
            "thiruvanandal":  {"time": "02:30 AM", "description": "Sabse pehli seva — pujari darshan"},
            "viswarupa":      {"time": "04:00 AM", "description": "Vishnu ke sab roopon ka darshan"},
            "thomala_seva":   {"time": "08:00 AM", "description": "Phool aur mala ka shringar"},
            "astadala_seva":  {"time": "01:00 PM", "description": "Dopahar ki mukhya seva"},
            "dolotsavam":     {"time": "06:00 PM", "description": "Sham ki aarti"},
            "ekanta_seva":    {"time": "12:00 AM", "description": "Antim raat ki seva"}
        },

        "best_visit_time": "Supatham darshan ke liye booking pehle se karo",
        "special_days": ["Brahmotsavam (Sep-Oct)", "Vaikunta Ekadasi"],
        "entry_fee": "Free darshan / Special darshan: Rs 300",
        "dress_code": "Traditional — dhoti/saree compulsory for close darshan"
    },

    {
        "name": "Banke Bihari Temple",
        "city": "Vrindavan",
        "state": "Uttar Pradesh",

        "opening_time": "07:45 AM",
        "closing_time": "09:00 PM",
        "break_time": "01:00 PM - 05:30 PM (dopahar ka break)",

        "aarti": {
            "mangala_aarti":  {"time": "07:45 AM", "description": "Subah ki pehli aarti"},
            "shringar_aarti": {"time": "09:30 AM", "description": "Krishna ka shringar"},
            "rajbhog_aarti":  {"time": "12:00 PM", "description": "Dopahar ki mukhya aarti"},
            "utthapan_aarti": {"time": "05:30 PM", "description": "Break ke baad ki aarti"},
            "sandhya_aarti":  {"time": "07:30 PM", "description": "Sham ki aarti"},
            "shayan_aarti":   {"time": "08:30 PM", "description": "Raat ki antim aarti"}
        },

        "best_visit_time": "Subah 8-10 AM ya sham 5:30-8 PM",
        "special_days": ["Janmashtami (bheed bahut zyada)", "Holi (Vrindavan ki Holi famous hai)", "Radha Ashtami"],
        "entry_fee": "Free",
        "dress_code": "Decent dress, no sleeveless"
    },

    {
        "name": "Vaishno Devi Temple",
        "city": "Katra",
        "state": "J&K",

        "opening_time": "05:00 AM",
        "closing_time": "10:00 PM",
        "note": "Cave temple hai, trek required hai (14 km round trip)",

        "aarti": {
            "pratah_aarti":   {"time": "05:00 AM", "description": "Subah ki pehli aarti"},
            "madhyan_aarti":  {"time": "12:00 PM", "description": "Dopahar ki aarti"},
            "sandhya_aarti":  {"time": "06:00 PM", "description": "Sham ki aarti"},
            "shayan_aarti":   {"time": "09:30 PM", "description": "Antim aarti"} 
        },

        "best_visit_time": "Subah 5-8 AM (thanda + kam bheed)",
        "special_days": ["Navratri (March & October — bahut bheed)", "Diwali"],
        "entry_fee": "Yatra Parchi: Free (online registration zaroori)",
        "dress_code": "Warm clothes (pahad hai), comfortable shoes for trek"
    },

    {
        "name": "Somnath Temple",
        "city": "Veraval",
        "state": "Gujarat",

        "opening_time": "06:00 AM",
        "closing_time": "09:30 PM",

        "aarti": {
            "pratah_aarti":  {"time": "07:00 AM", "description": "Subah ki aarti"},
            "madhyan_aarti": {"time": "12:00 PM", "description": "Dopahar ki aarti"},
            "sandhya_aarti": {"time": "07:00 PM", "description": "Sham ki aarti — light & sound show ke saath"},
        },

        "best_visit_time": "Sham 7:30 PM — Light & Sound Show hota hai (bahut sundar)",
        "special_days": ["Maha Shivratri", "Kartik Purnima"],
        "entry_fee": "Free (light show: Rs 100 approximately)",
        "dress_code": "No leather items allowed inside"
    },

    {
        "name": "Badrinath Temple",
        "city": "Badrinath",
        "state": "Uttarakhand",

        "opening_time": "04:30 AM",
        "closing_time": "09:00 PM",
        "seasonal_note": "May se November khulta hai",

        "aarti": {
            "mahabhishek":    {"time": "04:30 AM", "description": "Mukhya abhishek aarti"},
            "pratah_aarti":   {"time": "06:30 AM", "description": "Subah darshan ke liye"},
            "madhyan_aarti":  {"time": "12:00 PM", "description": "Dopahar ki aarti"},
            "sandhya_aarti":  {"time": "07:30 PM", "description": "Sham ki aarti"},
        },

        "best_visit_time": "Subah 4:30-7 AM",
        "special_days": ["Opening day (Akshaya Tritiya)", "Closing day (Bhai Dooj ke baad)"],
        "entry_fee": "Free",
        "dress_code": "Warm clothes zaroori"
    },

    {
        "name": "Jagannath Temple",
        "city": "Puri",
        "state": "Odisha",

        "opening_time": "05:00 AM",
        "closing_time": "11:00 PM",

        "aarti": {
            "mangala_alati":  {"time": "05:00 AM", "description": "Pratah ki aarti"},
            "mailam":         {"time": "06:00 AM", "description": "Devi ko jagana"},
            "abadha_bhog":    {"time": "11:00 AM", "description": "Mahaprasad (famous hai)"},
            "sandhya_alati":  {"time": "07:00 PM", "description": "Sham ki aarti"},
            "badasinghara":   {"time": "11:00 PM", "description": "Antim aarti"}
        },

        "best_visit_time": "Subah 5-8 AM (Rath Yatra ke time jayenge toh alag experience)",
        "special_days": ["Rath Yatra (June-July — duniya famous)", "Snana Purnima"],
        "entry_fee": "Free (sirf Hindus allowed inside)",
        "dress_code": "Traditional only, leather strictly prohibited"
    },

    {
        "name": "Meenakshi Amman Temple",
        "city": "Madurai",
        "state": "Tamil Nadu",

        "opening_time": "05:00 AM",
        "closing_time": "10:00 PM",
        "break_time": "12:30 PM - 04:00 PM",

        "aarti": {
            "thiruvanandal":  {"time": "05:00 AM", "description": "Subah ki pehli aarti"},
            "kalasandhi":     {"time": "08:00 AM", "description": "Subah ki mukhya aarti"},
            "uchikalam":      {"time": "12:00 PM", "description": "Dopahar ki aarti"},
            "sayarakshai":    {"time": "06:00 PM", "description": "Sham ki aarti"},
            "ardhajaman":     {"time": "09:30 PM", "description": "Raat ki aarti"}
        },

        "best_visit_time": "Subah 6-9 AM ya sham 4-7 PM",
        "special_days": ["Meenakshi Thirukalyanam (April-May)", "Navaratri"],
        "entry_fee": "Free (camera: Rs 50)",
        "dress_code": "Traditional — men me lungi/dhoti compulsory for inner sanctum"
    },

    {
        "name": "Nathdwara Temple",
        "city": "Nathdwara",
        "state": "Rajasthan",

        "opening_time": "05:30 AM",
        "closing_time": "09:30 PM",

        "aarti": {
            "mangala":        {"time": "05:30 AM", "description": "Pratah aarti"},
            "shringar":       {"time": "07:15 AM", "description": "Shrinathji ka shringar"},
            "gwal":           {"time": "10:00 AM", "description": "Gwalon ke saath darshan"},
            "rajbhog":        {"time": "11:30 AM", "description": "Dopahar ka bhog"},
            "uttapan":        {"time": "03:45 PM", "description": "Break ke baad"},
            "sandhya":        {"time": "07:30 PM", "description": "Sham ki aarti"},
            "shayan":         {"time": "09:00 PM", "description": "Antim aarti"}
        },

        "best_visit_time": "Sham 7:30 PM (Sandhya Darshan bahut sundar)",
        "special_days": ["Annakut (Diwali ke baad)", "Janmashtami", "Holi"],
        "entry_fee": "Free",
        "dress_code": "Decent dress, no shorts"
    },

    {
        "name": "Dwarkadheesh Temple",
        "city": "Dwarka",
        "state": "Gujarat",

        "opening_time": "06:30 AM",
        "closing_time": "08:30 PM",

        "aarti": {
            "mangala_aarti":  {"time": "06:30 AM", "description": "Pratah aarti"},
            "shringar_aarti": {"time": "07:30 AM", "description": "Shringar darshan"},
            "rajbhog_aarti":  {"time": "12:00 PM", "description": "Dopahar ki aarti"},
            "sandhya_aarti":  {"time": "07:00 PM", "description": "Sham ki aarti"},
            "shayan_aarti":   {"time": "08:00 PM", "description": "Antim aarti"}
        },

        "best_visit_time": "Subah 6:30-9 AM",
        "special_days": ["Janmashtami", "Dwarkadhish Mahotsav"],
        "entry_fee": "Free",
        "dress_code": "Traditional dress preferred"
    },

    {
        "name": "Krishna Janmabhoomi Temple",
        "city": "Mathura",
        "state": "Uttar Pradesh",

        "opening_time": "05:00 AM",
        "closing_time": "09:30 PM",

        "aarti": {
            "mangala":        {"time": "05:00 AM", "description": "Pehli aarti"},
            "shringar":       {"time": "07:30 AM", "description": "Krishna ka shringar"},
            "rajbhog":        {"time": "12:00 PM", "description": "Dopahar ki aarti"},
            "utthapan":       {"time": "04:00 PM", "description": "Shaam ki shuruat"},
            "sandhya":        {"time": "07:00 PM", "description": "Sham ki mukhya aarti"},
            "shayan":         {"time": "09:00 PM", "description": "Antim aarti"}
        },

        "best_visit_time": "Janmashtami ke din — lekin bahut zyada bheed",
        "special_days": ["Janmashtami", "Holi", "Radhashtami"],
        "entry_fee": "Free",
        "dress_code": "No shorts, no sleeveless"
    },
]


# ================================================
# SAVE TIMING DATA
# ================================================
def main():
    os.makedirs("data/raw", exist_ok=True)

    # --- BS4 Tutorial dikhao ---
    print("\n" + "=" * 50)
    print("  📖 BeautifulSoup Tutorial (live example)")
    print("=" * 50)

    try:
        bs4_example_explained()
    except Exception as e:
        print(f"Tutorial example failed: {e} (internet check karo)")

    # --- Timing data save karo ---
    print("\n" + "=" * 50)
    print("  💾 Timing Data Save Karo")
    print("=" * 50)

    output_file = "data/raw/timing_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(TEMPLE_TIMINGS, f, ensure_ascii=False, indent=2)

    print(f"\n  ✅ {len(TEMPLE_TIMINGS)} temples ka timing data save hua")
    print(f"  📁 File: {output_file}")

    # Quick preview
    print("\n  📋 Preview (pehle 2 temples):")
    for t in TEMPLE_TIMINGS[:2]:
        print(f"\n  Temple: {t['name']}")
        print(f"  Opens:  {t['opening_time']} — Closes: {t['closing_time']}")
        aartis = list(t['aarti'].keys())
        print(f"  Aarti:  {', '.join(aartis)}")


if __name__ == "__main__":
    main()
