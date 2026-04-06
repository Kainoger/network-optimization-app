import streamlit as st
from utils.guide_branding import add_signature

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Network Optimizer | Logistics Portal", 
    page_icon="🚚", 
    layout="wide"
)

# --- 2. CSS TO LOCK NAVIGATION & FIX UI ---
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
        .nav-status { padding: 10px 0px; font-size: 16px; }
        .hero-emoji { font-size: 150px; text-align: center; margin-top: -10px; }
        .problem-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #ff4b4b;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- 4. LOGIN SCREEN ---
def login_screen():
    st.title("🚚 Network Optimization Portal")
    with st.container():
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        with tab1:
            email = st.text_input("Corporate Email", key="login_email", placeholder="user@logistics.com")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login to Dashboard", type="primary"):
                if email and password:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("Please enter credentials to proceed.")
        with tab2:
            st.info("ℹ️ **System Architecture Note**")
            st.markdown("Account registration is currently managed by the System Administrator.")

    add_signature()

# --- 5. MAIN DASHBOARD ---
def main_dashboard():
    # --- SIDEBAR ---
    st.sidebar.title("Navigation")
    st.sidebar.info("🏠 **Main Menu** (Current)")
    st.sidebar.text("📥 Step 1: Data Input")
    st.sidebar.text("🔍 Step 2: Validation")
    st.sidebar.text("🏆 Step 3: Optimization")
    st.sidebar.divider()
    st.sidebar.write(f"👤 **User:** {st.session_state.user_email}")
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        keys_to_clear = ['delivery_data', 'depot_data', 'fleet_config', 'optimized_results']
        for key in keys_to_clear:
            if key in st.session_state: del st.session_state[key]
        st.rerun()

    # --- HERO SECTION ---
    st.title("🚀 Logistics Control Center")
    col_text, col_img = st.columns([2, 1])
    
    with col_text:
        st.subheader("Automated Routing Engine")
        st.markdown("""
        Welcome to the optimization hub. This tool uses mathematical solvers to minimize total transit distance and maximize fleet utilization.
        
        **Standard Operating Procedure:**
        1. **Data Input:** Upload delivery requirements and define fleet capacity.
        2. **Validation:** Verify coordinates and resolve address discrepancies.
        3. **Optimization:** Generate cost-effective routes based on vehicle constraints.
        """)
        if st.button("Launch Optimization Flow →", type="primary", use_container_width=True):
            st.switch_page("pages/1_Data_Input.py")

    with col_img:
        st.markdown('<div class="hero-emoji">🚚</div>', unsafe_allow_html=True)

    st.divider()

    # --- NEW SECTION: PROBLEM STATEMENT ---
    st.subheader("📝 Core Optimization Logic")
    
    with st.container():
        st.markdown("""
        <div class="problem-card">
            <strong>The Mathematical Objective:</strong><br>
            This engine solves the <strong>Capacitated Vehicle Routing Problem (CVRP)</strong>. 
            The goal is to design an optimal set of routes for a fleet of vehicles to deliver goods to a specific set of customers.
        </div>
        """, unsafe_allow_html=True)
        
        st.write("") # Spacer
        
        p1, p2, p3 = st.columns(3)
        with p1:
            st.markdown("#### 🏢 Single Depot")
            st.caption("All routes must start and end at a single warehouse location.")
        with p2:
            st.markdown("#### 📍 Multi-Destination")
            st.caption("Efficiently sequencing multiple delivery points across a diverse geography.")
        with p3:
            st.markdown("#### ⚖️ Capacity Constraints")
            st.caption("Each driver has a maximum load limit; the engine ensures no vehicle is over-capacitated.")

    st.info("🎯 **Primary Aim:** Find the **Lowest Total Cost** by minimizing total travel distance across the entire fleet.")

    st.divider()
    
    # --- METRICS ---
    st.subheader("System Metrics")
    s1, s2, s3 = st.columns(3)
    s1.metric("Engine Status", "Ready", "Optimal")
    s2.metric("Data Storage", "Session", "Encrypted")
    s3.metric("Fleet Mode", "Dynamic", "Multi-Vehicle")

    add_signature()

# --- 6. FLOW CONTROL ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_dashboard()