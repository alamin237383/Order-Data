import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob

# 1. Page Configuration & Professional Branding Theme
st.set_page_config(page_title="Multi-File Executive Dashboard", layout="wide", initial_sidebar_state="expanded")

# Inject Custom High-End Enterprise Styling (Matching your corporate visual layout)
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    h1 { color: #1E3A8A; font-weight: 800; font-size: 2.3rem; margin-bottom: 5px; }
    h3 { color: #334155; font-weight: 600; font-size: 1.25rem; border-bottom: 2px solid #E2E8F0; padding-bottom: 6px; margin-top: 15px; }
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #1D4ED8; }
    div[data-testid="stMetricLabel"] { font-size: 0.95rem; font-weight: 600; color: #475569; }
    .stMetric { background-color: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; border-top: 5px solid #2563EB; }
    .sidebar .sidebar-content { background-color: #F8FAFC; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Executive Sales & Distribution Performance System")
st.markdown("Automated batch file aggregation engine processing direct cross-sectional regional sales data streams.")
st.markdown("---")

# 2. Automated Multi-File Aggregation Engine (Folder Scanner)
@st.cache_data(ttl=300)  # Re-scans the directory automatically every 5 minutes
def load_and_merge_folder_data():
    folder_path = "data"
    
    # Auto-generate the folder if it does not exist yet to prevent crashes
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    # Pick up all CSV logs within the targeted 'data' folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    # Fallback Mechanism: If directory is empty, read the main root-level backup dump
    if not csv_files:
        root_backup = "SKU Wise Order Details Dump (44).csv"
        if os.path.exists(root_backup):
            df = pd.read_csv(root_backup)
            if 'OrderDate' in df.columns:
                df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
            return df
        return pd.DataFrame()
        
    # Merge and concatenate all localized CSV chunks into one master table
    compiled_list = []
    for file in csv_files:
        try:
            temp_df = pd.read_csv(file)
            compiled_list.append(temp_df)
        except Exception as e:
            st.sidebar.error(f"Error parsing file {os.path.basename(file)}: {e}")
            
    if compiled_list:
        master_df = pd.concat(compiled_list, ignore_index=True)
        if 'OrderDate' in master_df.columns:
            master_df['OrderDate'] = pd.to_datetime(master_df['OrderDate'], errors='coerce')
        return master_df
    return pd.DataFrame()

try:
    df = load_and_merge_folder_data()
    
    if df.empty:
        st.info("📂 **System Status:** No active records found inside the `data` directory. Please commit your daily CSV tables inside the 'data' folder.")
    else:
        # 3. Clean Vertical Sidebar Controllers (Hierarchical Selectboxes)
        st.sidebar.header("🎛️ Governance Filters")
        
        # A. Region Component
        if 'Region' in df.columns:
            region_options = ["All Regions"] + sorted(list(df['Region'].dropna().unique()))
            selected_region = st.sidebar.selectbox("1. Region Select", region_options)
            if selected_region != "All Regions":
                df = df[df['Region'] == selected_region]
                
        # B. Area Component
        if 'Area' in df.columns:
            area_options = ["All Areas"] + sorted(list(df['Area'].dropna().unique()))
            selected_area = st.sidebar.selectbox("2. Area Select", area_options)
            if selected_area != "All Areas":
                df = df[df['Area'] == selected_area]
                
        # C. Territory Component
        if 'Territory' in df.columns:
            territory_options = ["All Territories"] + sorted(list(df['Territory'].dropna().unique()))
            selected_territory = st.sidebar.selectbox("3. Territory Select", territory_options)
            if selected_territory != "All Territories":
                df = df[df['Territory'] == selected_territory]
                
        # D. Town Component
        if 'Town' in df.columns:
            town_options = ["All Towns"] + sorted(list(df['Town'].dropna().unique()))
            selected_town = st.sidebar.selectbox("4. Town Select", town_options)
            if selected_town != "All Towns":
                df = df[df['Town'] == selected_town]
                
        # E. Sales Force Dropdown Component (Requested Default Mode)
        if 'SO Name' in df.columns:
            so_options = ["All SOs"] + sorted(list(df['SO Name'].dropna().unique()))
            selected_so = st.sidebar.selectbox("5. Sales Officer (SO Name)", so_options)
            if selected_so != "All SOs":
                df = df[df['SO Name'] == selected_so]

        # 4. Premium Executive Summary Indicators (Top Scorecard KPI Cards)
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        with kpi_col1:
            st.metric(label="Total Lines Executed", value=f"{len(df):,}")
            
        with kpi_col2:
            # Complex group metric calculating productive physical memos cut
            if 'OrderDate' in df.columns and 'Outlet Code' in df.columns:
                memo_count = df.groupby(['OrderDate', 'Outlet Code']).ngroups
            elif 'Outlet Code' in df.columns:
                memo_count = df['Outlet Code'].nunique()
            else:
                memo_count = df.iloc[:, 0].nunique()
            st.metric(label="Productive Memos Saved", value=f"{memo_count:,}")
            
        with kpi_col3:
            active_sos = df['SO Name'].nunique() if 'SO Name' in df.columns else 0
            st.metric(label="Active Force Size (SO)", value=f"{active_sos:,}")
            
        with kpi_col4:
            brand_count = 0
            for col in df.columns:
                if 'brand' in col.lower():
                    brand_count = df[col].nunique()
                    break
            st.metric(label="Active Brand Lines", value=f"{brand_count if brand_count > 0 else 'N/A'}")

        st.markdown("<br>", unsafe_allow_html=True)

        # 5. Business Visualizations Matrices (Analytics Grids)
        chart_row_col1, chart_row_col2 = st.columns(2)
        
        with chart_row_col1:
            # Dynamically identify and compute brand performance metrics
            brand_col_name = None
            for col in df.columns:
                if 'brand' in col.lower():
                    brand_col_name = col
                    break
                    
            if brand_col_name:
                st.markdown("### 🏷️ Top Brands Portfolio Matrix")
                brand_agg = df[brand_col_name].value_counts().reset_index()
                brand_agg.columns = ['Brand Name', 'Volume Count']
                
                fig_brand_matrix = px.bar(brand_agg, x='Volume Count', y='Brand Name', orientation='h',
                                          color='Volume Count', color_continuous_scale='Turbo',
                                          labels={'Volume Count': 'Orders Logged'})
                fig_brand_matrix.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=15, b=10))
                st.plotly_chart(fig_brand_matrix, use_container_width=True)
            else:
                st.info("Brand column footprint not detected for advanced portfolio analysis charts.")

        with chart_row_col2:
            if 'SO Name' in df.columns:
                st.markdown("### 🏆 Top 10 High-Performing Officers")
                so_agg = df['SO Name'].value_counts().head(10).reset_index()
                so_agg.columns = ['Officer Name', 'Order Submissions']
                
                fig_so_matrix = px.bar(so_agg, x='Order Submissions', y='Officer Name', orientation='h',
                                       color='Order Submissions', color_continuous_scale='Viridis')
                fig_so_matrix.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=15, b=10))
                st.plotly_chart(fig_so_matrix, use_container_width=True)

        # 6. Operational Continuous Inflow Timeline Chart
        if 'OrderDate' in df.columns and not df['OrderDate'].isnull().all():
            st.markdown("### 📅 Operational Inflow Load Over Time")
            timeline_data = df.groupby(df['OrderDate'].dt.date).size().reset_index()
            timeline_data.columns = ['Date Timeline', 'Volume Generated']
            
            fig_timeline = px.area(timeline_data, x='Date Timeline', y='Volume Generated')
            fig_timeline.update_traces(line_color='#2563EB', fillcolor='rgba(37, 99, 235, 0.12)')
            fig_timeline.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=5, r=5, t=10, b=5))
            st.plotly_chart(fig_timeline, use_container_width=True)

        # 7. Enterprise Raw Data Explorer Hub & Direct Export Tool
        st.markdown("### 📋 Aggregated Raw Records Core Data Stream Explorer")
        st.dataframe(df, use_container_width=True)

        # Core Sidebar Extract Interface
        export_csv_stream = df.to_csv(index=False).encode('utf-8')
        st.sidebar.markdown("---")
        st.sidebar.download_button(
            label="📥 Export Compiled Data Stream",
            data=export_csv_stream,
            file_name="Master_Aggregated_Operational_Report.csv",
            mime="text/csv",
            use_container_width=True
        )

except Exception as e:
    st.error(f"Critical synchronization disruption: {e}")
