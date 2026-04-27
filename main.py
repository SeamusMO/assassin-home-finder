import streamlit as st
import requests

st.set_page_config(page_title="Mass Assassin", layout="centered")
st.title("🎯 Mass Assassin Tracker")

# MassGIS REST API for FY2026 Parcels
API_URL = "https://services1.arcgis.com/hGd9HplS6ayRM9S_/" \
          "ArcGIS/rest/services/L3_Parcels_Statewide/FeatureServer/0/query"

def search_mass_gis(query_text):
    query_text = query_text.strip().upper()
    # Try exact(ish) first
    where_clause = f"OWNER1 LIKE '%{query_text}%'"
    
    params = {
        'where': where_clause,
        'outFields': 'OWNER1,FULL_STR,TOWN_ID,TOTAL_VAL',
        'f': 'json',
        'resultRecordCount': 10
    }
    
    res = requests.get(API_URL, params=params).json()
    features = res.get('features', [])
    
    # Fallback: Search by Last Name only if first fails
    if not features and " " in query_text:
        last_name = query_text.split()[-1]
        st.warning(f"No exact match. Searching for '{last_name}'...")
        params['where'] = f"OWNER1 LIKE '%{last_name}%'"
        res = requests.get(API_URL, params=params).json()
        features = res.get('features', [])
        
    return features

name_input = st.text_input("Enter Target/Parent Name:", placeholder="e.g. SMITH JOHN")

if name_input:
    results = search_mass_gis(name_input)
    if not results:
        st.error("No properties found.")
    for r in results:
        attr = r['attributes']
        with st.container():
            st.markdown(f"### {attr['OWNER1']}")
            st.write(f"📍 {attr['FULL_STR']}, {attr['TOWN_ID']}")
            st.write(f"💰 Value: ${attr['TOTAL_VAL']:,}")
            
            # Google Maps Link
            addr = f"{attr['FULL_STR']}, {attr['TOWN_ID']}, MA".replace(" ", "+")
            st.link_button("🚀 Open in Maps", f"https://www.google.com/maps/search/?api=1&query={addr}")
            st.divider()
