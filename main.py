import streamlit as st
import requests

# 1. UPDATED VERIFIED URL (L3 Parcels - Statewide)
API_URL = "https://services1.arcgis.com/hGd9HplS6ayRM9S_/arcgis/rest/services/L3_Parcels_Statewide/FeatureServer/0/query"

def search_mass_gis(query_text):
    query_text = query_text.strip().upper()
    
    params = {
        'where': f"OWNER1 LIKE '%{query_text}%'",
        'outFields': 'OWNER1,SITE_ADDR,CITY,TOTAL_VAL', # SITE_ADDR and CITY are more reliable
        'f': 'json',
        'resultRecordCount': 20,
        'returnGeometry': 'false' # Keeps the response light/fast
    }
    
    try:
        response = requests.get(API_URL, params=params)
        # 2. ADD THIS: Catch HTML errors before trying to parse JSON
        response.raise_for_status() 
        
        data = response.json()
        
        # Check if the API returned an 'error' key inside a valid JSON response
        if "error" in data:
            st.error(f"API Error: {data['error'].get('message')}")
            return []
            
        features = data.get('features', [])
        
        # Fallback Logic
        if not features and " " in query_text:
            last_name = query_text.split()[-1]
            params['where'] = f"OWNER1 LIKE '%{last_name}%'"
            response = requests.get(API_URL, params=params)
            features = response.json().get('features', [])
            
        return features
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return []
