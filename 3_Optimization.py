import streamlit as st
import pandas as pd
import folium
import random
from streamlit_folium import st_folium
from utils.solver import solve_vrp
from utils.guide_branding import add_signature

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Optimization | Logistics Optimizer", 
    page_icon="🏆",
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
    st.text("📥 Step 1: Data Input")
    st.text("🔍 Step 2: Validation")
    st.info("🏆 Step 3: Optimization (Current)")
    
    st.divider()
    st.write(f"👤 **User:** {st.session_state.get('user_email', 'Guest')}")
    if st.sidebar.button("Log Out"):
        st.session_state.clear()
        st.switch_page("main.py")

st.title("🏆 Step 3: Route Optimization")

# --- 4. DATA PERSISTENCE & SESSION CHECK ---
if 'delivery_data' not in st.session_state or 'fleet_config' not in st.session_state:
    st.error("❌ No data found. Please complete Step 1: Data Input first.")
    if st.button("← Go to Step 1"):
        st.switch_page("pages/1_Data_Input.py")
    st.stop()

depot = st.session_state['depot_data']
customers = st.session_state['delivery_data']
fleet = st.session_state['fleet_config']

if 'optimized_results' not in st.session_state:
    st.session_state['optimized_results'] = None

# --- 5. HELPER FUNCTIONS ---
def get_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

MARKER_COLORS = [
    'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 
    'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 
    'pink', 'lightblue', 'lightgreen', 'gray'
]

# --- 6. OPTIMIZATION CONTROL ---
st.info("The algorithm assigns unique colors to each route. Match the colored dot in the driver details to the lines on the map.")

col_calc, col_reset = st.columns([4, 1])

with col_calc:
    if st.button("🚀 Calculate Optimal Routes", type="primary", use_container_width=True):
        if not depot['Latitude'] or not depot['Longitude']:
            st.error("❌ Depot coordinates are missing. Please fix this in Step 1.")
        else:
            with st.spinner("Analyzing routes and vehicle capacities..."):
                try:
                    depot_coords = (depot['Latitude'], depot['Longitude'])
                    results = solve_vrp(depot_coords, customers, fleet)
                    
                    if results:
                        for i, r in enumerate(results):
                            r['hex_color'] = get_random_color()
                            r['marker_color'] = MARKER_COLORS[i % len(MARKER_COLORS)]
                        
                        st.session_state['optimized_results'] = results
                        st.success(f"Calculated {len(results)} optimal routes!")
                    else:
                        st.error("❌ No solution found. Check if Total Demand exceeds Total Fleet Capacity.")
                except Exception as e:
                    st.error(f"❌ An error occurred during optimization: {e}")

with col_reset:
    if st.button("Clear Results", use_container_width=True):
        st.session_state['optimized_results'] = None
        st.rerun()

st.divider()

# --- 7. RESULTS DASHBOARD ---
if st.session_state['optimized_results'] is not None:
    results = st.session_state['optimized_results']
    col_stats, col_map = st.columns([1, 2])
    
    with col_stats:
        st.subheader("📊 Route Summary")
        total_dist = sum(r['distance_km'] for r in results)
        total_cost = sum(r['cost'] for r in results)
        
        st.metric("Total Distance", f"{total_dist:.2f} km")
        st.metric("Total Estimated Cost", f"{total_cost:,.0f} VND")
        
        st.write("---")
        
        for r in results:
            color_dot = f"<span style='color:{r['hex_color']}; font-size: 22px;'>●</span>"
            with st.expander(f"🚚 Driver: {r['driver_id']}"):
                st.markdown(f"**Map Line Color:** {color_dot} `{r['hex_color']}`", unsafe_allow_html=True)
                st.write(f"**Distance:** {r['distance_km']:.2f} km")
                st.write(f"**Estimated Cost:** {r['cost']:,.0f} VND")
                st.write("**Sequence:**")
                st.caption(" → ".join(r['readable_path']) + " → Depot")

    with col_map:
        st.subheader("🗺️ Route Visualization")
        m = folium.Map(location=[depot['Latitude'], depot['Longitude']], zoom_start=12)
        
        folium.Marker(
            [depot['Latitude'], depot['Longitude']], 
            tooltip="WAREHOUSE / DEPOT", 
            icon=folium.Icon(color='black', icon='home')
        ).add_to(m)
        
        for r in results:
            line_color = r['hex_color']
            m_color = r['marker_color']
            path_points = [[depot['Latitude'], depot['Longitude']]]
            
            for node_idx in r['path_indices']:
                if node_idx != 0: 
                    c_row = customers.iloc[node_idx - 1]
                    point = [c_row['Latitude'], c_row['Longitude']]
                    path_points.append(point)
                    
                    folium.Marker(
                        point,
                        popup=f"<b>Stop</b><br>Driver: {r['driver_id']}<br>Address: {c_row['Address']}",
                        icon=folium.Icon(color=m_color, icon='info-sign')
                    ).add_to(m)
            
            path_points.append([depot['Latitude'], depot['Longitude']])
            folium.PolyLine(
                path_points, 
                color=line_color, 
                weight=5, 
                opacity=0.8,
                tooltip=f"Route: {r['driver_id']}"
            ).add_to(m)
        
        st_folium(m, width=800, height=600, returned_objects=[])

# --- 8. FINAL NAVIGATION ---
st.divider()
if st.button("← Back to Validation"):
    st.switch_page("pages/2_Validation.py")

add_signature()