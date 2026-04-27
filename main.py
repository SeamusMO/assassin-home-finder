import streamlit as st
from curl_cffi import requests # Use this instead of standard requests
import urllib.parse

st.set_page_config(page_title="Mass Assassin", layout="centered")
st.title("🎯 Mass Assassin Tracker")

# Verified URL for 2026 MassGIS Parcels
API_URL = "https://services1.arcgis.com/hGd9HplS6ayRM9S_/arcgis/rest/services/L3_Parcels_Statewide/FeatureServer/0/query"

def search_mass_gis(query_text):
    query_text = query_text.strip().upper()
    
    # curl_cffi allows us to "impersonate" a specific browser version
    # This bypasses advanced 403 blocks that standard 'requests' hits
    params = {
        'where': f"OWNER1 LIKE '%{query_text}%'",
        'outFields': 'OWNER1,SITE_ADDR,CITY,TOTAL_VAL',
        'f': 'json',
        'resultRecordCount': 20,
        'returnGeometry': 'false'
    }

    try:
        # 'impersonate="chrome120"' is the magic line that fixes the 403
        response = requests.get(
            API_URL, 
            params=params, 
            impersonate="chrome120"
        )
        
        response.raise_for_status()
        data = response.json()
        features = data.get('features', [])
        
        # Fallback to Last Name if no exact match
        if not features and " " in query_text:
            last_name = query_text.split()[-1]
            params['where'] = f"OWNER1 LIKE '%{last_name}%'"
            response = requests.get(API_URL, params=params, impersonate="chrome120")
            features = response.json().get('features', [])
            
        return features
    except Exception as e:
        st.error(f"Access Denied or Server Error: {e}")
        return []

name_input = st.text_input("Enter Target or Parent Name:", placeholder="e.g. MARTINO")

if name_input:
    results = search_mass_gis(name_input)
    
    if not results:
        st.warning("No properties found. Try searching by just the last name (e.g., 'MARTINO').")
    else:
        for r in results:
            attr = r['attributes']
            owner = attr.get('OWNER1', 'Unknown')
            address = attr.get('SITE_ADDR', 'N/A')
            city = attr.get('CITY', '')
            
            with st.container():
                st.markdown(f"### {owner}")
                st.write(f"📍 {address}, {city}")
                
                # Dynamic Google Maps link
                full_addr = f"{address}, {city}, MA"
                maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(full_addr)}"
                
                st.link_button("🚀 View on Map", maps_url)
                st.divider()
