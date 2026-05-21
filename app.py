import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Layout Setup
st.set_page_config(page_title="Advanced Sales & Memo Analytics", layout="wide", initial_sidebar_state="expanded")

# Custom Dashboard Styling
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    h1 { color: #0F172A; font-weight: 800; font-size: 2.2rem; }
    h3 { color: #334155; font-weight: 600; font-size: 1.2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #1E40AF; }
    .stMetric { background-color: #FFFFFF; padding: 18px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; border-top: 5px solid #2563EB; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Order & Memo Execution Dashboard")
st.markdown("Real-time sales force metrics, operational memo tracking, and brand contribution analysis.")
st.markdown("---")

# 2. Optimized Data Ingestion
@st.cache_data
def load_data():
    file_name = "SKU Wise Order Details Dump (44).csv"
    df = pd.read_csv(file_name)
    
    # Standardize OrderDate column if present
    if 'OrderDate' in df.columns:
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
    return df

try:
    df = load_data()
    
    # 3. Sidebar Vertical Filter Controls (All Selectboxes)
    st.sidebar.header("⚙️ Filter Options")
    
    # A. Region Filter
    if 'Region' in df.columns:
        region_list = ["All Regions"] + list(df['Region'].dropna().unique())
        sel_region = st.sidebar.selectbox("1. Select Region:", region_list)
        if sel_region != "All Regions":
            df = df[df['Region'] == sel_region]
            
    # B. Area Filter
    if 'Area' in df.columns:
        area_list = ["All Areas"] + list(df['Area'].dropna().unique())
        sel_area = st.sidebar.selectbox("2. Select Area:", area_list)
        if sel_area != "All Areas":
            df = df[df['Area'] == sel_area]
            
    # D. Territory Filter
    if 'Territory' in df.columns:
        territory_list = ["All Territories"] + list(df['Territory'].dropna().unique())
        sel_territory = st.sidebar.selectbox("3. Select Territory:", territory_list)
        if sel_territory != "All Territories":
            df = df[df['Territory'] == sel_territory]
            
    # E. Town Filter
    if 'Town' in df.columns:
        town_list = ["All Towns"] + list(df['Town'].dropna().unique())
        sel_town = st.sidebar.selectbox("4. Select Town:", town_list)
        if sel_town != "All Towns":
            df = df[df['Town'] == sel_town]
            
    # F. SO Name Filter (Default dropdown selectbox instead of search)
    if 'SO Name' in df.columns:
        so_list = ["All SOs"] + list(df['SO Name'].dropna().unique())
        sel_so = st.sidebar.selectbox("5. Select SO Name:", so_list)
        if sel_so != "All Stars" and sel_so != "All SOs":
            df = df[df['SO Name'] == sel_so]

    # 4. Top KPI Executive Scorecard
    col1,
