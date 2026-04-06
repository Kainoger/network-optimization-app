import streamlit as st
import pandas as pd
from utils.guide_branding import add_signature

# --- 0. IMPORT GOOGLE MAPS LIBRARY ---
try:
    import googlemaps
except ImportError:
    st.error("🚀 **Missing Library:** Please run `pip install googlemaps` in your terminal.")
    st.stop()

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Validation | Logistics Optimizer", 
    page_icon="🔍", 
    layout="wide"
)

# --- 2. GLOBAL SIDEBAR LOCK (NON-CLICKABLE NAVIGATION) ---
st.markdown("""
    <style>
        /* Disables all clicks on the default sidebar navigation */
        [data-testid="stSidebarNav"] {
            pointer-events: none;
            cursor: default;
        }
        /* Visual styling to show it's a progress tracker */
        [data-testid="stSidebarNav"] ul {
            opacity: 0.7;
        }
        /* Highlight the current page */
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            opacity: 1 !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. GOOGLE MAPS SETUP & UTILS ---
def get_gmaps_client():
    try:
        # Accesses the key from .streamlit/secrets.toml
        api_key = st.secrets["MAPS_API_KEY"]
        return googlemaps.Client(key=api_key)
    except Exception:
        return None

def geocode_address(address, client):
    if client is None:
        return None
    try:
        geocode_result = client.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
        return None
    except Exception as e:
        st.error(f"Geocoding Error for '{address}': {e}")
        return None

# --- 4. CUSTOM SIDEBAR CONTENT ---
with st.sidebar:
    st.title("Navigation")
    st.text("🏠 Main Menu")
    st.text("📥 Step 1: Data Input")
    st.info("🔍 Step 2: Validation (Current)")
    st.text("🏆 Step 3: Optimization")
    
    st.divider()
    st.write(f"👤 **User:** {st.session_state.get('user_email', 'Guest')}")
    if st.button("Log Out"):
        st.session_state.clear()
        st.switch_page("main.py")

st.title("🔍 Step 2: Address Validation")

# Ensure data exists from Step 1
if 'depot_data' not in st.session_state or 'delivery_data' not in st.session_state:
    st.warning("⚠️ No data found. Please go back to Step 1: Data Input.")
    if st.button("← Go to Step 1"):
        # Corrected to your exact lowercase numbered filename
        st.switch_page("pages/1_data_input.py")
    st.stop()

# --- 5. START VALIDATION PROCESS ---
if st.button("Start Geocoding & Validation", type="primary"):
    gmaps_client = get_gmaps_client()
    
    # A. DEPOT VALIDATION
    depot = st.session_state['depot_data']
    if depot.get("Latitude") is None or depot.get("Longitude") is None:
        if gmaps_client and depot.get('Address'):
            with st.spinner(f"Geocoding Depot: {depot['Address']}..."):
                coords = geocode_address(depot['Address'], gmaps_client)
                if coords:
                    st.session_state['depot_data'].update({
                        "Latitude": coords[0], "Longitude": coords[1], "Status": "Verified"
                    })
                    st.success(f"✅ Depot Verified: {coords}")
                else:
                    st.error("❌ Geocoding Failed for Depot. Check address or use Manual Input on Page 1.")
        else:
            st.error("❌ Depot coordinates missing and no API key found.")
    else:
        st.info(f"✅ Using provided Depot coordinates: {depot['Latitude']}, {depot['Longitude']}")

    # B. CUSTOMER VALIDATION
    df = st.session_state['delivery_data']
    with st.spinner("Geocoding Customer Addresses..."):
        for index, row in df.iterrows():
            # Skip if already have coordinates
            if pd.notnull(row.get('Latitude')) and pd.notnull(row.get('Longitude')):
                continue
            
            if gmaps_client:
                coords = geocode_address(row['Address'], gmaps_client)
                if coords:
                    df.at[index, 'Latitude'] = coords[0]
                    df.at[index, 'Longitude'] = coords[1]
            else:
                st.warning(f"⚠️ Missing coordinates for: {row['Address']} (No API Key)")
    
    st.session_state['delivery_data'] = df
    st.success("Validation complete!")

# --- 6. PREVIEW & MAP SECTION ---
st.divider()
col_data, col_map = st.columns([1, 1])

with col_data:
    st.subheader("Validated Data")
    st.dataframe(st.session_state['delivery_data'], use_container_width=True)

with col_map:
    st.subheader("Map Preview")
    
    # Prepare Customer Data (Blue)
    map_cust = st.session_state['delivery_data'][['Latitude', 'Longitude']].dropna().copy()
    map_cust['color'] = "#0000FF" # Blue
    
    # Prepare Depot Data (Red)
    d_lat = st.session_state['depot_data'].get('Latitude')
    d_lon = st.session_state['depot_data'].get('Longitude')
    
    if d_lat is not None and d_lon is not None:
        map_depot = pd.DataFrame([{'Latitude': d_lat, 'Longitude': d_lon, 'color': "#FF0000"}]) # Red
        full_map_df = pd.concat([map_cust, map_depot]).dropna()
        
        # Streamlit Native Map
        st.map(full_map_df, latitude="Latitude", longitude="Longitude", color="color", size=25)
        st.caption("🔴 Red = Warehouse (Depot) | 🔵 Blue = Customer Destinations")
    else:
        st.info("The map will appear once Depot coordinates are verified.")

# --- 7. PROCEED ---
st.divider()
footer_c1, footer_c2 = st.columns([1, 1])
with footer_c1:
    if st.button("← Back to Step 1"):
        # Corrected to your exact lowercase numbered filename
        st.switch_page("pages/1_data_input.py")

with footer_c2:
    if st.button("Proceed to Optimization →", type="primary"):
        if st.session_state['depot_data'].get('Latitude') is not None:
            # Corrected to your exact lowercase numbered filename
            st.switch_page("pages/3_optimization.py")
        else:
            st.error("Please validate coordinates before proceeding.")

add_signature()