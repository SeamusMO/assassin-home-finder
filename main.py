import streamlit as st
from curl_cffi import requests # Use this instead of standard requests
import urllib.parse

st.set_page_config(page_title="Mass Assassin", layout="centered")
st.title("🎯 Mass Assassin Tracker")

# Verified URL for 2026 MassGIS Parcels
API_URL = "https://services1.arcgis.com/hGd9HplS6ayRM9S_/arcgis/rest/services/L3_Parcels_Statewide/FeatureServer/0/query"

# 1. Create a persistent session
session = requests.Session()

def search_mass_gis(query_text):
    query_text = query_text.strip().upper()
    
    # Advanced headers to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://massgis.maps.arcgis.com",
        "Referer": "https://massgis.maps.arcgis.com/apps/instant/sidebar/index.html"
    }
    
    params = {
        'where': f"OWNER1 LIKE '%{query_text}%'",
        'outFields': 'OWNER1,SITE_ADDR,CITY,TOTAL_VAL',
        'f': 'json',
        'resultRecordCount': 20
    }
    
    try:
        # Use session.get instead of requests.get
        response = session.get(API_URL, params=params, headers=headers, timeout=10)
        
        # If still 403, try a different approach: forcing a JSON content type
        if response.status_code == 403:
            st.error("MassGIS blocked the request. Try searching by Last Name only.")
            return []
            
        response.raise_for_status()
        data = response.json()
        return data.get('features', [])
    except Exception as e:
        st.error(f"Connection Error: {e}")
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
