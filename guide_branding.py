import streamlit as st

def add_signature():
    # Sidebar signature
    st.sidebar.divider()
    st.sidebar.caption("🛠️ **Created by kainoger | Dang Le Anh Son**")
    
    # Bottom of page signature
    st.markdown("<br><hr><center><p style='color:grey;'>Created by kainoger | Dang Le Anh Son</p></center>", unsafe_allow_html=True)