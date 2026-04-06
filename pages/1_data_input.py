import streamlit as st
import pandas as pd
import io
import re
from utils.guide_branding import add_signature

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Data Input | Logistics Optimizer", 
    page_icon="📥", 
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

# --- 3. CUSTOM SIDEBAR CONTENT ---
with st.sidebar:
    st.title("Navigation")
    st.text("🏠 Main Menu")
    st.info("📥 Step 1: Data Input (Current)")
    st.text("🔍 Step 2: Validation")
    st.text("🏆 Step 3: Optimization")
    
    st.divider()
    st.write(f"👤 **User:** {st.session_state.get('user_email', 'Guest')}")
    if st.sidebar.button("Log Out"):
        st.session_state.clear()
        st.switch_page("main.py")

st.title("📥 Step 1: Data Input")

# --- 4. COORDINATE GUIDES ---
col_guide1, col_guide2 = st.columns(2)

with col_guide1:
    with st.expander("🖱️ How to get Individual Coordinates (Manual)"):
        st.write("""
        1. Open **Google Maps**.
        2. **Right-click** the exact location.
        3. Click the **coordinates** (e.g., 10.7766, 106.7015) to copy.
        4. Paste into the Latitude and Longitude columns below.
        """)

with col_guide2:
    with st.expander("⚡ How to get Mass Coordinates (Fast)"):
        st.write("""
        If you have a long list of addresses, use these tools to get coordinates for your entire file at once:
        - **Google Sheets:** Use the 'Geocode Cells' add-on.
        - **BatchGeo.com:** Paste your list and export to Excel.
        """)
        st.info("💡 **Tip:** Ensure Latitudes are ~10.0 and Longitudes are ~106.0 for the HCMC area.")

# --- 5. TEMPLATE PREPARATION ---
def create_template(cols):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(columns=cols).to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

st.subheader("🛠️ Template Preparation")
col_t1, col_t2 = st.columns(2)
with col_t1:
    st.download_button("📥 Download Customer Template", 
                       data=create_template(["Address", "Demand_Qty", "Latitude", "Longitude"]),
                       file_name="customer_template.xlsx")
with col_t2:
    st.download_button("📥 Download Driver Template", 
                       data=create_template(["Driver_ID", "Capacity", "Cost_per_km"]),
                       file_name="driver_template.xlsx")

st.divider()

# --- 6. DATA PROCESSING CALLBACKS ---
def handle_customer_upload():
    if st.session_state.cust_uploader_key:
        df = pd.read_excel(st.session_state.cust_uploader_key)
        # Pre-process numeric columns to prevent editor crashes
        for col in ['Demand_Qty', 'Latitude', 'Longitude']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        st.session_state['delivery_data'] = df
        st.session_state['cust_v'] += 1

def handle_fleet_upload():
    if st.session_state.fleet_uploader_key:
        df = pd.read_excel(st.session_state.fleet_uploader_key)
        df['Driver_ID'] = df['Driver_ID'].astype(str).str.replace(r'\.0$', '', regex=True)
        for col in ['Capacity', 'Cost_per_km']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        st.session_state['fleet_config'] = df
        st.session_state['fleet_v'] += 1

# --- 7. INITIALIZING SESSION STATES ---
if 'depot_data' not in st.session_state:
    st.session_state['depot_data'] = {"Latitude": None, "Longitude": None}
if 'delivery_data' not in st.session_state:
    st.session_state['delivery_data'] = pd.DataFrame(columns=["Address", "Demand_Qty", "Latitude", "Longitude"])
if 'fleet_config' not in st.session_state:
    st.session_state['fleet_config'] = pd.DataFrame(columns=["Driver_ID", "Capacity", "Cost_per_km"])
if 'cust_v' not in st.session_state: st.session_state['cust_v'] = 0
if 'fleet_v' not in st.session_state: st.session_state['fleet_v'] = 0

# --- 8. SECTION 1: WAREHOUSE / DEPOT ---
st.subheader("1. Warehouse / Depot")
depot_mode = st.radio("Depot Input Method:", ["Direct Coordinates", "Google Maps Link"], horizontal=True)

if depot_mode == "Direct Coordinates":
    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat_in = st.text_input("Depot Latitude", 
                               value=str(st.session_state['depot_data']['Latitude']) if st.session_state['depot_data']['Latitude'] else "",
                               placeholder="e.g. 10.7717")
    with col_lon:
        lon_in = st.text_input("Depot Longitude", 
                               value=str(st.session_state['depot_data']['Longitude']) if st.session_state['depot_data']['Longitude'] else "",
                               placeholder="e.g. 106.7042")
    if lat_in and lon_in:
        try:
            st.session_state['depot_data'].update({"Latitude": float(lat_in), "Longitude": float(lon_in)})
        except: pass

else:
    st.caption("Paste the full Google Maps URL (e.g. https://www.google.com/maps/@10.7...)")
    maps_url = st.text_input("Paste Google Maps URL")
    if maps_url:
        match = re.search(r'@([-+]?\d+\.\d+),([-+]?\d+\.\d+)', maps_url)
        if match:
            st.session_state['depot_data'].update({"Latitude": float(match.group(1)), "Longitude": float(match.group(2))})
            st.success(f"📍 Extracted: {match.group(1)}, {match.group(2)}")
        else:
            st.error("❌ Could not find coordinates in that link.")

st.divider()

# --- 9. SECTION 2: CUSTOMER DESTINATIONS ---
st.subheader("2. Customer Destinations")
st.file_uploader("Upload Customer Excel", type=["xlsx"], key="cust_uploader_key", on_change=handle_customer_upload)

st.session_state['delivery_data'] = st.data_editor(
    st.session_state['delivery_data'],
    key=f"cust_table_v{st.session_state['cust_v']}",
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Demand_Qty": st.column_config.NumberColumn("Demand", min_value=0),
        "Latitude": st.column_config.NumberColumn("Lat", format="%.6f"),
        "Longitude": st.column_config.NumberColumn("Long", format="%.6f")
    }
)

st.divider()

# --- 10. SECTION 3: FLEET CONFIGURATION ---
st.subheader("3. Fleet Configuration")
st.file_uploader("Upload Driver Excel", type=["xlsx"], key="fleet_uploader_key", on_change=handle_fleet_upload)

st.session_state['fleet_config'] = st.data_editor(
    st.session_state['fleet_config'],
    key=f"fleet_table_v{st.session_state['fleet_v']}",
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Driver_ID": st.column_config.TextColumn("Driver ID"),
        "Capacity": st.column_config.NumberColumn("Capacity", min_value=0),
        "Cost_per_km": st.column_config.NumberColumn("Cost/km", min_value=0)
    }
)

# --- 11. FINAL VALIDATION & SUBMISSION ---
st.divider()
if st.button("Proceed to Validation →", type="primary", use_container_width=True):
    d = st.session_state['depot_data']
    c = st.session_state['delivery_data']
    f = st.session_state['fleet_config']
    
    # Check for empty values
    if not d['Latitude'] or not d['Longitude']:
        st.error("❌ Depot coordinates are missing.")
    elif c.empty or c.isnull().values.any():
        st.error("❌ Customer table is incomplete (Check for empty cells).")
    elif f.empty or f.isnull().values.any():
        st.error("❌ Fleet table is incomplete (Check for empty cells).")
    else:
        try:
            # HARD NUMERIC VALIDATION
            pd.to_numeric(c['Demand_Qty'])
            pd.to_numeric(c['Latitude'])
            pd.to_numeric(c['Longitude'])
            pd.to_numeric(f['Capacity'])
            pd.to_numeric(f['Cost_per_km'])
            
            st.success("✅ All data validated!")
            # Updated to match your new lowercase filename
            st.switch_page("pages/validation.py")
            
        except Exception:
            st.error("❌ Format error: Coordinates, Demand, and Capacity must be numbers.")

if st.button("Reset All Data"):
    st.session_state.clear()
    st.rerun()

add_signature()