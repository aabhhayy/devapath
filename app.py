import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(page_title="DevaPath", layout="wide")
st.title("🛕 DevaPath — AI Temple Guide")

# Jinke GPS nahi mila unke liye fallback coordinates
FALLBACK_COORDS = {
    "Kashi Vishwanath Temple":   {"lat": 25.3109, "lon": 83.0107},
    "Tirupati Balaji Temple":    {"lat": 13.6288, "lon": 79.4192},
    "Meenakshi Amman Temple":    {"lat": 9.9195,  "lon": 78.1193},
    "Brihadeeswarar Temple":     {"lat": 10.7828, "lon": 79.1318},
    "Jagannath Temple":          {"lat": 19.8054, "lon": 85.8315},
    "Somnath Temple":            {"lat": 20.8880, "lon": 70.4013},
    "Dwarkadheesh Temple":       {"lat": 22.2442, "lon": 68.9676},
    "Kedarnath Temple":          {"lat": 30.7352, "lon": 79.0669},
    "Badrinath Temple":          {"lat": 30.7433, "lon": 79.4938},
    "Vaishno Devi Temple":       {"lat": 32.9917, "lon": 74.9523},
    "Banke Bihari Temple":       {"lat": 27.5794, "lon": 77.6966},
    "Krishna Janmabhoomi Temple":{"lat": 27.5036, "lon": 77.6610},
    "Nathdwara Temple":          {"lat": 24.9322, "lon": 73.8205},
}

# Data load karo
with open("data/processed/temples_master.json", "r", encoding="utf-8") as f:
    temples = json.load(f)

# Missing coordinates fix karo
for temple in temples:
    if not temple.get("lat") or not temple.get("lon"):
        fallback = FALLBACK_COORDS.get(temple["name"])
        if fallback:
            temple["lat"] = fallback["lat"]
            temple["lon"] = fallback["lon"]

# Map banao
m = folium.Map(location=[22.5, 80.0], zoom_start=5)

for temple in temples:
    if temple.get("lat") and temple.get("lon"):
        folium.Marker(
            location=[temple["lat"], temple["lon"]],
            popup=temple["name"],
            tooltip=temple["name"],
            icon=folium.Icon(color="orange", icon="star")
        ).add_to(m)

map_data = st_folium(m, width=1200, height=500)

# Temple click pe details dikhao
if map_data["last_object_clicked_popup"]:
    temple_name = map_data["last_object_clicked_popup"]
    temple = next((t for t in temples if t["name"] == temple_name), None)

    if temple:
        st.subheader(f"🛕 {temple['name']}")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"📍 **Location:** {temple['city']}, {temple['state']}")
            st.write(f"🙏 **Deity:** {temple['deity']}")
            st.write(f"🕐 **Opens:** {temple['opening_time']}")
            st.write(f"🕙 **Closes:** {temple['closing_time']}")
            st.write(f"💰 **Entry:** {temple['entry_fee']}")
            st.write(f"👗 **Dress Code:** {temple['dress_code']}")
            if temple.get("best_visit_time"):
                st.write(f"⭐ **Best Time:** {temple['best_visit_time']}")

        with col2:
            st.markdown("**🔔 Aarti Schedule:**")
            aarti = temple.get("aarti", {})
            if aarti:
                for aarti_name, details in aarti.items():
                    st.write(f"• **{aarti_name.replace('_', ' ').title()}** — {details['time']}")
                    st.caption(f"  {details['description']}")
            else:
                st.write("Aarti timings available on site")

        st.markdown("---")
        st.markdown("**📖 History:**")
        st.info(temple["history"])