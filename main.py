import streamlit as st
import requests
import urllib.parse

st.set_page_config(page_title="Mass Assassin", layout="centered")
st.title("🎯 Mass Assassin Tracker")

# MassGIS REST API (Statewide L3 Parcels)
API_URL = "https://services1.arcgis.com/hGd9HplS6ayRM9S_/arcgis/rest/services/L3_Parcels_Statewide/FeatureServer/0/query"

def search_mass_gis(query_text):
    query_text = query_text.strip().upper()
    
    # Common field names in MassGIS L3: OWNER1, SITE_ADDR, CITY, TOTAL_VAL
    params = {
        'where': f"OWNER1 LIKE '%{query_text}%'",
        'outFields': 'OWNER1,SITE_ADDR,CITY,TOTAL_VAL',
        'f': 'json',
        'resultRecordCount': 20,
        'returnGeometry': 'false'
    }
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        features = data.get('features', [])
        
        # Fallback: If no match, search by the last word (assumed Last Name)
        if not features and " " in query_text:
            last_name = query_text.split()[-1]
            params['where'] = f"OWNER1 LIKE '%{last_name}%'"
            response = requests.get(API_URL, params=params)
            features = response.json().get('features', [])
            
        return features
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []

name_input = st.text_input("Enter Target or Parent Name:", placeholder="e.g. SMITH JOHN")

if name_input:
    results = search_mass_gis(name_input)
    
    if not results:
        st.warning("No properties found for that name.")
    else:
        for r in results:
            attr = r['attributes']
            # Using the correct keys we requested in 'outFields'
            owner = attr.get('OWNER1', 'Unknown Owner')
            address = attr.get('SITE_ADDR', 'No Address Listed')
            city = attr.get('CITY', 'MA')
            value = attr.get('TOTAL_VAL', 0)
            
            with st.container():
                st.markdown(f"### {owner}")
                st.write(f"📍 {address}, {city}")
                st.write(f"💰 Assessed Value: ${value:,}")
                
                # Encode the address for a clean Google Maps link
                full_address = f"{address}, {city}, MA"
                encoded_addr = urllib.parse.quote_plus(full_address)
                maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_addr}"
                
                st.link_button("🚀 Directions", maps_url)
                st.divider()
