"""
================================================
STEP 3 — Overpass API Location Fetcher
================================================
Yeh script Overpass API se temple locations
fetch karegi (GPS coordinates).

Overpass API = OpenStreetMap ka free search engine
  - Koi API key nahi chahiye
  - Unlimited free requests
  - Puri duniya ka data

Run karo:
  python scrapers/03_overpass_fetcher.py
================================================
"""

import requests
import json
import os


# ================================================
# Overpass API Endpoint
# ================================================
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def fetch_temples_near_location(lat, lon, radius_km=20):
    """
    Diye gaye location ke paas ke sab temples fetch karo.

    Overpass Query Language (Overpass QL) ek special
    language hai OpenStreetMap data query karne ke liye.

    Hum query karenge:
      - amenity = place_of_worship (religious place)
      - religion = hindu           (Hindu temple)
      - area = radius_km ke andar

    Args:
        lat (float): Latitude (e.g. Meerut = 28.9845)
        lon (float): Longitude (e.g. Meerut = 77.7064)
        radius_km (int): Search radius in km

    Returns:
        list: Temple dictionaries with name, lat, lon
    """

    radius_meters = radius_km * 1000

    # ---- Overpass QL Query ----
    # [out:json]     → JSON format me result chahiye
    # node[...]      → sirf points (not areas/ways)
    # (around:R,lat,lon) → R meters ke andar
    # out;           → results show karo

    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="place_of_worship"]["religion"="hindu"]
           (around:{radius_meters},{lat},{lon});
      way["amenity"="place_of_worship"]["religion"="hindu"]
           (around:{radius_meters},{lat},{lon});
    );
    out center;
    """

    print(f"🔍 Querying Overpass API...")
    print(f"   Location: ({lat}, {lon})")
    print(f"   Radius: {radius_km} km")

    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=30,
            headers={'User-Agent': 'DevaPath-Bot/1.0'}
        )
        response.raise_for_status()

        data = response.json()
        elements = data.get("elements", [])

        print(f"\n   Raw results: {len(elements)} elements found")

        # ---- Parse Results ----
        temples = []
        for element in elements:
            tags = element.get("tags", {})

            # Name nikalo (English ya Hindi)
            name = (
                tags.get("name:en") or          # English name
                tags.get("name") or             # Default name
                tags.get("name:hi") or          # Hindi name
                "Unknown Temple"
            )

            # Coordinates (way ke liye "center" use karo)
            if element["type"] == "node":
                lat_e = element["lat"]
                lon_e = element["lon"]
            elif element["type"] == "way":
                center = element.get("center", {})
                lat_e = center.get("lat")
                lon_e = center.get("lon")
            else:
                continue

            if not lat_e or not lon_e:
                continue

            # Sirf named temples lo
            if name == "Unknown Temple" and not tags.get("name"):
                continue

            temple = {
                "osm_id":       element.get("id"),
                "osm_type":     element.get("type"),
                "name":         name,
                "name_hindi":   tags.get("name:hi", ""),
                "lat":          lat_e,
                "lon":          lon_e,
                "deity":        tags.get("deity", ""),
                "website":      tags.get("website", ""),
                "phone":        tags.get("phone", ""),
                "address":      {
                    "street":   tags.get("addr:street", ""),
                    "city":     tags.get("addr:city", ""),
                    "state":    tags.get("addr:state", ""),
                    "postcode": tags.get("addr:postcode", "")
                },
                "source":       "OpenStreetMap"
            }

            temples.append(temple)

        # Duplicates remove karo (same name, nearby location)
        unique_temples = remove_duplicates(temples)
        return unique_temples

    except requests.exceptions.Timeout:
        print("❌ Request timeout — Overpass API slow hai, dobara try karo")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def remove_duplicates(temples, distance_threshold=0.005):
    """
    Bahut paas ke temples (probably same temple) ko merge karo.
    0.005 degrees ≈ 500 meter
    """
    unique = []
    for temple in temples:
        is_duplicate = False
        for existing in unique:
            lat_diff = abs(temple['lat'] - existing['lat'])
            lon_diff = abs(temple['lon'] - existing['lon'])
            if lat_diff < distance_threshold and lon_diff < distance_threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique.append(temple)
    return unique


# ================================================
# MULTIPLE CITIES FETCH KARO
# ================================================

# Famous Indian cities with coordinates
LOCATIONS_TO_FETCH = [
    {"city": "Varanasi",   "lat": 25.3176, "lon": 82.9739, "radius_km": 15},
    {"city": "Vrindavan",  "lat": 27.5794, "lon": 77.6966, "radius_km": 10},
    {"city": "Mathura",    "lat": 27.4924, "lon": 77.6737, "radius_km": 10},
    {"city": "Haridwar",   "lat": 29.9457, "lon": 78.1642, "radius_km": 15},
    {"city": "Meerut",     "lat": 28.9845, "lon": 77.7064, "radius_km": 20},  # User ka city
    {"city": "Delhi",      "lat": 28.6139, "lon": 77.2090, "radius_km": 20},
]


def main():
    os.makedirs("data/raw", exist_ok=True)

    all_locations_data = []
    all_temples_combined = []

    print("=" * 50)
    print("  🗺️  Overpass API Temple Fetcher")
    print("=" * 50)

    for loc in LOCATIONS_TO_FETCH:
        print(f"\n📍 City: {loc['city']}")

        temples = fetch_temples_near_location(
            lat=loc['lat'],
            lon=loc['lon'],
            radius_km=loc['radius_km']
        )

        print(f"   ✅ Found: {len(temples)} unique temples")

        # City ke saath tag karo
        for t in temples:
            t['search_city'] = loc['city']

        location_entry = {
            "city":         loc['city'],
            "center_lat":   loc['lat'],
            "center_lon":   loc['lon'],
            "radius_km":    loc['radius_km'],
            "temples_found": len(temples),
            "temples":      temples
        }

        all_locations_data.append(location_entry)
        all_temples_combined.extend(temples)

        # API pe load mat dalo
        import time
        time.sleep(3)

    # ---- Save: Location-wise ----
    loc_file = "data/raw/location_data.json"
    with open(loc_file, 'w', encoding='utf-8') as f:
        json.dump(all_locations_data, f, ensure_ascii=False, indent=2)

    # ---- Save: All temples flat list ----
    all_file = "data/raw/all_temples_from_osm.json"
    with open(all_file, 'w', encoding='utf-8') as f:
        json.dump(all_temples_combined, f, ensure_ascii=False, indent=2)

    # ---- Summary ----
    print("\n" + "=" * 50)
    print(f"  ✅ Total temples fetched: {len(all_temples_combined)}")
    print(f"  📁 Location data: {loc_file}")
    print(f"  📁 All temples:   {all_file}")
    print("=" * 50)

    # Quick preview
    if all_temples_combined:
        print("\n📋 Sample temples found:")
        for t in all_temples_combined[:5]:
            print(f"  • {t['name']} ({t['search_city']}) — ({t['lat']:.4f}, {t['lon']:.4f})")


# ================================================
# BONUS: Runtime me bhi use kar sakte ho
# Streamlit app me call karoge isko
# ================================================
def get_nearby_temples_realtime(user_lat, user_lon, radius_km=10):
    """
    Streamlit app me use karne ke liye.
    User ki current location de do, temples wapas milenge.
    
    Usage:
        temples = get_nearby_temples_realtime(28.9845, 77.7064, 15)
    """
    return fetch_temples_near_location(user_lat, user_lon, radius_km)


if __name__ == "__main__":
    main()
