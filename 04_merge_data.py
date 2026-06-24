"""
================================================
STEP 4 — Data Merger & Cleaner
================================================
Yeh script teen alag JSON files ko merge karegi:
  1. data/raw/wikipedia_data.json   (history)
  2. data/raw/timing_data.json      (aarti timings)
  3. data/raw/location_data.json    (GPS coordinates)

Output:
  data/processed/temples_master.json ← Final database

Run karo (BAAD ME — pehle steps 1,2,3 complete karo):
  python data_prep/04_merge_data.py
================================================
"""

import json
import os
from difflib import SequenceMatcher


# ================================================
# HELPER: Two strings kitni similar hain?
# Name matching ke liye use hoga
# ================================================
def similarity(a, b):
    """
    Do strings ki similarity 0.0 to 1.0 me batao.
    1.0 = exact match, 0.0 = bilkul alag
    
    Example:
      similarity("Kashi Vishwanath", "Kashi Vishwanath Temple") → 0.89
      similarity("Kedarnath", "Tirupati") → 0.1
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_timing_match(temple_name, timing_list, threshold=0.6):
    """
    Temple name se best matching timing entry dhundho.
    Perfect match nahi milega toh fuzzy matching use karo.
    """
    best_match = None
    best_score = 0

    for timing in timing_list:
        score = similarity(temple_name, timing['name'])
        if score > best_score:
            best_score = score
            best_match = timing

    if best_score >= threshold:
        return best_match
    return None


def find_location_match(temple_name, city, location_temples, threshold=0.5):
    """
    Location data me same temple dhundho (name + city se)
    """
    best_match = None
    best_score = 0

    for loc_temple in location_temples:
        # Name similarity
        name_score = similarity(temple_name, loc_temple.get('name', ''))

        # City bonus — agar same city hai toh score boost karo
        city_match = 0.2 if city.lower() in loc_temple.get('search_city', '').lower() else 0

        total_score = name_score + city_match

        if total_score > best_score:
            best_score = total_score
            best_match = loc_temple

    if best_score >= threshold:
        return best_match
    return None


# ================================================
# MAIN MERGE FUNCTION
# ================================================
def merge_all_data():
    """
    Teen sources ko merge karke ek master JSON banao.
    
    Final structure har temple ka:
    {
        "id":           "kashi_vishwanath_varanasi",
        "name":         "Kashi Vishwanath Temple",
        "city":         "Varanasi",
        "state":        "Uttar Pradesh",
        "deity":        "Shiva",
        "lat":          25.3109,
        "lon":          83.0107,
        "history":      "...",
        "infobox":      {...},
        "timings":      {...},
        "aarti":        {...},
        "best_visit":   "...",
        "special_days": [...],
        "entry_fee":    "...",
        "dress_code":   "...",
        "wiki_url":     "...",
        "data_sources": [...]
    }
    """

    print("=" * 50)
    print("  🔗 Data Merger & Cleaner")
    print("=" * 50)

    # ---- Load Files ----
    def load_json(path, default=[]):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  ✅ Loaded: {path} ({len(data)} records)")
            return data
        else:
            print(f"  ⚠️  Not found: {path} (skipping)")
            return default

    wiki_data    = load_json("data/raw/wikipedia_data.json")
    timing_data  = load_json("data/raw/timing_data.json")

    # Location data nested hai, flatten karo
    location_raw = load_json("data/raw/location_data.json")
    all_loc_temples = []
    for city_entry in location_raw:
        all_loc_temples.extend(city_entry.get('temples', []))
    print(f"  📍 Total OSM temples: {len(all_loc_temples)}")

    # ---- Wikipedia data base hai, uske upar merge karo ----
    print(f"\n🔄 Merging {len(wiki_data)} temples...")

    master_data = []

    for wiki_entry in wiki_data:
        if wiki_entry.get('status') == 'failed':
            continue

        temple_name = wiki_entry['name']
        city        = wiki_entry.get('city', '')
        state       = wiki_entry.get('state', '')

        # --- Timing match dhundho ---
        timing_match = find_timing_match(temple_name, timing_data)

        # --- Location match dhundho ---
        loc_match = find_location_match(temple_name, city, all_loc_temples)

        # --- ID banao (lowercase, spaces → underscore) ---
        temple_id = f"{temple_name.lower().replace(' ', '_').replace(',', '')}_{city.lower()}"

        # --- Merge karo ---
        merged = {
            "id":    temple_id,
            "name":  temple_name,
            "city":  city,
            "state": state,
            "deity": wiki_entry.get('deity', ''),

            # Location
            "lat": loc_match['lat'] if loc_match else None,
            "lon": loc_match['lon'] if loc_match else None,

            # History from Wikipedia
            "history":     wiki_entry.get('history', ''),
            "infobox":     wiki_entry.get('infobox', {}),
            "wiki_url":    wiki_entry.get('wiki_url', ''),

            # Timings from manual dataset
            "opening_time":   timing_match.get('opening_time', 'N/A')   if timing_match else 'N/A',
            "closing_time":   timing_match.get('closing_time', 'N/A')   if timing_match else 'N/A',
            "seasonal_note":  timing_match.get('seasonal_note', '')     if timing_match else '',
            "break_time":     timing_match.get('break_time', '')        if timing_match else '',
            "aarti":          timing_match.get('aarti', {})              if timing_match else {},
            "best_visit_time":timing_match.get('best_visit_time', '')   if timing_match else '',
            "special_days":   timing_match.get('special_days', [])      if timing_match else [],
            "entry_fee":      timing_match.get('entry_fee', 'N/A')      if timing_match else 'N/A',
            "dress_code":     timing_match.get('dress_code', '')        if timing_match else '',

            # Data sources track karo
            "data_sources": {
                "history":  "Wikipedia" if wiki_entry.get('history') else None,
                "timings":  "Manual Curated" if timing_match else None,
                "location": "OpenStreetMap" if loc_match else "Not Found"
            }
        }

        master_data.append(merged)

        # Progress
        loc_status  = "✅ GPS" if loc_match  else "❌ No GPS"
        time_status = "✅ Timing" if timing_match else "⚠️  No Timing"
        print(f"  {temple_name[:35]:<35} {loc_status}  {time_status}")

    # ---- Save Master JSON ----
    os.makedirs("data/processed", exist_ok=True)
    output_file = "data/processed/temples_master.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)

    # ---- Summary ----
    with_location = sum(1 for t in master_data if t['lat'])
    with_timing   = sum(1 for t in master_data if t['aarti'])
    with_history  = sum(1 for t in master_data if t['history'])

    print("\n" + "=" * 50)
    print(f"  Total temples merged:  {len(master_data)}")
    print(f"  With GPS location:     {with_location}/{len(master_data)}")
    print(f"  With Aarti timings:    {with_timing}/{len(master_data)}")
    print(f"  With History:          {with_history}/{len(master_data)}")
    print(f"\n  📁 Master file: {output_file}")
    print("=" * 50)

    return master_data


# ================================================
# BONUS: Data Quality Check
# ================================================
def check_data_quality(master_data):
    """Master data ki quality check karo — missing fields dhundho"""

    print("\n\n📊 Data Quality Report:")
    print("-" * 50)

    issues = []
    for temple in master_data:
        temple_issues = []

        if not temple.get('lat'):
            temple_issues.append("GPS missing")
        if not temple.get('history') or len(temple['history']) < 100:
            temple_issues.append("History too short")
        if not temple.get('aarti'):
            temple_issues.append("Aarti timings missing")
        if not temple.get('opening_time') or temple['opening_time'] == 'N/A':
            temple_issues.append("Opening time missing")

        if temple_issues:
            issues.append({
                "temple": temple['name'],
                "issues": temple_issues
            })

    if issues:
        print(f"\n⚠️  {len(issues)} temples with issues:")
        for item in issues:
            print(f"  • {item['temple']}")
            for issue in item['issues']:
                print(f"      - {issue}")
    else:
        print("  ✅ Sab theek hai! No issues found.")

    # Quality score
    total_fields = len(master_data) * 4
    missing_fields = sum(len(i['issues']) for i in issues)
    quality_score = ((total_fields - missing_fields) / total_fields) * 100
    print(f"\n  📈 Data Quality Score: {quality_score:.1f}%")


if __name__ == "__main__":
    master = merge_all_data()
    if master:
        check_data_quality(master)
