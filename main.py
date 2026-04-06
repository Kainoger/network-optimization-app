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
        /* Hide the default Streamlit sidebar navigation links */
        [data-testid="stSidebarNav"] {
            display: none;
        }
        
        /* Large Emoji Icon Styling */
        .hero-emoji {
            font-size: 150px;
            text-align: center;
            margin-top: -10px;
        }

        /* Problem Card Styling */
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

# --- 4. LOGIN SCREEN COMPONENT ---
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
            st.info("🔐 **Access & Registration Policy**")
            st.markdown("""
            ### Why is self-registration disabled?
            To maintain the integrity of the logistics network and ensure data security, this portal does not currently support public account creation. 
            
            **Key Reasons for Manual Management:**
            1.  **Corporate Security:** This tool handles sensitive supply chain data, including warehouse locations, customer coordinates, and fleet cost structures. Access is restricted to authorized personnel only.
            2.  **Data Governance:** To ensure the "Digital Twin" remains accurate, user profiles must be mapped to specific regional logistics clusters by the System Administrator.
            3.  **Resource Allocation:** Optimization solvers require significant computational power. Manual onboarding allows us to manage server load effectively during this phase.

            **Project Scope & Proof of Concept (PoC):**
            This portal is a specialized digital tool designed to demonstrate **automated route optimization**. By centralizing fragmented logistics data into a single digital environment, we aim to:
            * Eliminate manual planning errors prevalent in traditional Excel-based workflows.
            * Drastically reduce "Empty Miles" and improve overall vehicle utilization.
            * Enable data-driven decision-making for Business Development and Supply Chain Excellence.

            ---
            💡 **Guest Access:** To explore the features and the optimization engine, you may use **any email and password** in the **Login** tab for this demonstration version.
            """)

    add_signature()

# --- 5. MAIN DASHBOARD COMPONENT ---
def main_dashboard():
    # --- SIDEBAR ---
    st.sidebar.title("Navigation")
    st.sidebar.info("🏠 **Main Menu** (Current)")
    st.sidebar.text("📥 Step 1: Data Input")
    st.sidebar.text("🔍 Step 2: Validation")
    st.sidebar.text("🏆 Step 3: Optimization")
    
    st.sidebar.divider()
    st.sidebar.write(f"👤 **User:** {st.session_state.get('user_email', 'Guest')}")
    
    if st.sidebar.button("Log Out"):
        st.session_state.clear()
        st.rerun()

    # --- HERO SECTION ---
    st.title("🚀 Logistics Control Center")
    col_text, col_img = st.columns([2, 1])
    
    with col_text:
        st.subheader("Automated Routing Engine")
        st.markdown("""
        Welcome to the optimization hub. This tool uses mathematical solvers to minimize total transit distance and maximize fleet utilization.
        
        **Standard Operating Procedure:**
        1. **Data Input:** Upload delivery requirements (Excel/CSV) and define fleet capacity.
        2. **Validation:** Verify coordinates and resolve address discrepancies via Google Maps.
        3. **Optimization:** Generate cost-effective routes based on vehicle constraints and VRP logic.
        """)
        
        # --- THE FINAL CORRECTED NAVIGATION BUTTON ---
        if st.button("Launch Optimization Flow →", type="primary", use_container_width=True):
            # Matches your exact lowercase filename with number
            st.switch_page("pages/1_data_input.py")

    with col_img:
        st.markdown('<div class="hero-emoji">🚚</div>', unsafe_allow_html=True)

    st.divider()

    # --- CORE PROBLEM DEFINITION ---
    st.subheader("📝 Core Optimization Logic")
    st.markdown("""
    <div class="problem-card">
        <strong>The Mathematical Objective:</strong><br>
        This engine solves the <strong>Capacitated Vehicle Routing Problem (CVRP)</strong>. 
        The goal is to design an optimal set of routes for a fleet of vehicles to deliver goods to a specific set of customers.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("") 
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

# --- 6. LOGICAL FLOW CONTROL ---
if not st.session_state.get('logged_in', False):
    login_screen()
else:
    main_dashboard()