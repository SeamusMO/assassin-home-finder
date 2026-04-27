import streamlit as st
import requests
import urllib.parse

st.set_page_config(page_title="Mass Assassin", layout="centered")
st.title("🎯 Mass Assassin Tracker")

# Verified 2026 MassGIS API URL
API_URL = "https://services1.arcgis.com/hGd9HplS6ayRM9S_/arcgis/rest/services/L3_Parcels_Statewide/FeatureServer/0/query"

def search_mass_gis(query_text):
    query_text = query_text.strip().upper()
    
    # 1. ADD HEADERS to bypass the 403 Forbidden error
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://massgis.maps.arcgis.com/"
    }
    
    params = {
        'where': f"OWNER1 LIKE '%{query_text}%'",
        'outFields': 'OWNER1,SITE_ADDR,CITY,TOTAL_VAL',
        'f': 'json',
        'resultRecordCount': 20,
        'returnGeometry': 'false'
    }
    
    try:
        # 2. Include the headers in your request
        response = requests.get(API_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        features = data.get('features', [])
        
        if not features and " " in query_text:
            last_name = query_text.split()[-1]
            params['where'] = f"OWNER1 LIKE '%{last_name}%'"
            response = requests.get(API_URL, params=params, headers=headers)
            features = response.json().get('features', [])
            
        return features
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []

name_input = st.text_input("Enter Target or Parent Name:", placeholder="e.g. MARTINO JOHN")

if name_input:
    results = search_mass_gis(name_input)
    
    if not results:
        st.warning("No properties found. Try searching by just the Last Name.")
    else:
        for r in results:
            attr = r['attributes']
            # Using .get() ensures the app doesn't crash if a field is missing
            owner = attr.get('OWNER1', 'Unknown')
            address = attr.get('SITE_ADDR', 'No Address')
            city = attr.get('CITY', '')
            value = attr.get('TOTAL_VAL', 0)
            
            with st.container():
                st.markdown(f"### {owner}")
                st.write(f"📍 {address}, {city}")
                st.write(f"💰 Value: ${value:,}")
                
                # Google Maps Link
                full_addr = f"{address}, {city}, MA"
                maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(full_addr)}"
                st.link_button("🚀 Open in Maps", maps_url)
                st.divider()
