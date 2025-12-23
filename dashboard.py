import streamlit as st
import pandas as pd
import analytics_logic # Import our backend logic
import retrieve_nodes # Import our data fetcher
import time

st.set_page_config(
    page_title="Xandeum Node Sniper",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for that "Sniper" Aesthetic
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .metric-card {
        background-color: #1E2130;
        border: 1px solid #303642;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    h1, h2, h3 {
        color: #FF4B4B; /* Xandeum/Solana Red-ish accent */
    }
</style>
""", unsafe_allow_html=True)

st.title("📡 Xandeum Network Intelligence")
st.markdown(f"**Target:** `devnet` | **Status:** `Live Monitoring`")

# Sidebar
with st.sidebar:
    st.header("Control Panel")
    
    # Initialize session state for network status
    if 'network_status' not in st.session_state:
        st.session_state.network_status = "Unknown"

    # Status Indicator
    if st.session_state.network_status == "Live":
        st.success("🟢 **Status: Live Network**")
    elif st.session_state.network_status == "Simulation":
        st.warning("🟡 **Status: Simulation Mode**\n\n(Network Unreachable)")
    
    if st.button("Refresh Data", type="primary"):
        with st.spinner("Accessing Gossip Protocol..."):
            # 1. Fetch
            success = retrieve_nodes.get_nodes()
            if success:
                st.session_state.network_status = "Live"
            else:
                retrieve_nodes.create_mock_data()
                st.session_state.network_status = "Simulation"
            
            # 2. Process
            raw_data = analytics_logic.load_data()
            if raw_data:
                df = analytics_logic.enrich_data(raw_data)
                df.to_csv("processed_nodes.csv", index=False)
                st.toast("Analytic Model Updated.")
                time.sleep(1)
                st.rerun()

# Load Data
try:
    df = pd.read_csv("processed_nodes.csv")
except FileNotFoundError:
    st.error("No data found. Click 'Refresh Data'.")
    st.stop()

# Operations: stats
total_nodes = len(df)
active_nodes = len(df[df['status'] == 'Active'])
storage_capacity = f"{total_nodes * 10} TB" # Mock capacity calculation

# KPI Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total pNodes", total_nodes)
col2.metric("Active Nodes", active_nodes, delta=f"{active_nodes/total_nodes*100:.0f}% Health")
col3.metric("Est. Storage", storage_capacity)
col4.metric("Network Version", df['version'].mode()[0] if not df.empty else "N/A")

# Main Charts
st.divider()

col_map, col_charts = st.columns([2, 1])

with col_map:
    st.subheader("🌍 pNode Geographic Distribution")
    # Streamlit map requires 'lat' and 'lon' columns to be non-null
    map_data = df.dropna(subset=['lat', 'lon'])
    st.map(map_data, size=200, color="#FF0000")

with col_charts:
    st.subheader("Network Health")
    status_counts = df['status'].value_counts()
    st.bar_chart(status_counts, color="#FF0000")
    
    st.subheader("Version Dominance")
    st.dataframe(df['version'].value_counts(), use_container_width=True)

# Data Table
st.divider()
st.subheader("📋 Node Telemetry")

# Style the table
def highlight_status(val):
    color = '#00FF00' if val == 'Active' else '#FF0000'
    return f'color: {color}; font-weight: bold'

st.dataframe(
    df,
    column_config={
        "pubkey": "Node Identity",
        "ip": "IP Address",
        "lat": None, # Hide lat/lon
        "lon": None,
        "status": st.column_config.TextColumn(
            "Status",
            help="Current gossip status",
        ),
    },
    use_container_width=True,
    hide_index=True,
)
