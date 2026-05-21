import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Settings & Layout Configuration
st.set_page_config(page_title="Sales Performance Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom Professional Theme CSS (Matching the reference dark/blue high-end tone)
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    h1 { color: #0F172A; font-weight: 800; font-size: 2.2rem; margin-bottom: 0px; }
    h3 { color: #334155; font-weight: 600; font-size: 1.2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #1E40AF; }
    div[data-testid="stMetricLabel"] { font-size: 0.9rem; font-weight: 500; color: #64748B; }
    .stMetric { background-color: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; border-top: 5px solid #2563EB; }
    </style>
""", unsafe_allow_html=True)

# Top Header
st.title("📊 Executive Sales Performance Dashboard")
st.markdown("Enterprise-grade business intelligence and order tracking analytics built dynamically from your source data.")
st.markdown("---")

# 2. Data Sourcing with Cache
@st.cache_data
def load_data():
    file_name = "SKU Wise Order Details Dump (44).csv"
    df = pd.read_csv(file_name)
    if 'OrderDate' in df.columns:
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
    return df

try:
    df = load_data()
    
    # 3. Interactive Sidebar Filters
    st.sidebar.header("⚙️ Dashboard Controls")
    
    # Region Selector
    if 'Region' in df.columns:
        all_regions = ["All Regions"] + list(df['Region'].unique())
        selected_region = st.sidebar.selectbox("Filter by Region:", all_regions)
        if selected_region != "All Regions":
            filtered_df = df[df['Region'] == selected_region]
        else:
            filtered_df = df.copy()
    else:
        filtered_df = df.copy()
        
    # Area Selector (Dynamic based on selected Region)
    if 'Area' in filtered_df.columns:
        all_areas = ["All Areas"] + list(filtered_df['Area'].unique())
        selected_area = st.sidebar.selectbox("Filter by Area:", all_areas)
        if selected_area != "All Areas":
            filtered_df = filtered_df[filtered_df['Area'] == selected_area]

    # Search Bar for Sales Officer
    if 'SO Name' in filtered_df.columns:
        search_so = st.sidebar.text_input("🔍 Search Sales Officer (SO):", placeholder="Type name...")
        if search_so:
            filtered_df = filtered_df[filtered_df['SO Name'].str.contains(search_so, case=False, na=False)]

    # 4. Top KPI Summary Row (Matching reference style metrics)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_orders = len(filtered_df)
        st.metric(label="Total Orders Logged", value=f"{total_orders:,}")
        
    with col2:
        unique_skus = filtered_df.iloc[:, 0].nunique()
        for col in filtered_df.columns:
            if 'sku' in col.lower():
                unique_skus = filtered_df[col].nunique()
                break
        st.metric(label="Unique SKUs Distributed", value=f"{unique_skus}")
        
    with col3:
        unique_so = filtered_df['SO Name'].nunique() if 'SO Name' in filtered_df.columns else 0
        st.metric(label="Active Sales Force (SO)", value=f"{unique_so}")
        
    with col4:
        unique_outlets = filtered_df['Outlet Name'].nunique() if 'Outlet Name' in filtered_df.columns else 0
        st.metric(label="Outlets Retiled", value=f"{unique_outlets}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Visualizations Grid (Charts)
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        if 'SO Name' in filtered_df.columns:
            st.markdown("### 🏆 Top 10 Sales Officers Performance")
            top_so = filtered_df['SO Name'].value_counts().head(10).reset_index()
            top_so.columns = ['SO Name', 'Orders']
            
            fig_so = px.bar(top_so, x='Orders', y='SO Name', orientation='h',
                            color='Orders', color_continuous_scale='Blues',
                            labels={'Orders': 'Total Orders Taken', 'SO Name': 'Officer Name'})
            fig_so.update_layout(yaxis={'categoryorder':'total ascending'}, 
                                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_so, use_container_width=True)

    with chart_col2:
        if 'Area' in filtered_df.columns:
            st.markdown("### 📍 Geographic Share by Area")
            area_counts = filtered_df['Area'].value_counts().head(10).reset_index()
            area_counts.columns = ['Area', 'Orders']
            
            fig_area = px.pie(area_counts, values='Orders', names='Area', hole=0.5,
                              color_discrete_sequence=px.colors.sequential.Plotly3)
            fig_area.update_layout(margin=dict(l=10, r=10, t=10, b=10),
                                  legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_area, use_container_width=True)

    # 6. Timeline Continuous Trend Chart
    if 'OrderDate' in filtered_df.columns and not filtered_df['OrderDate'].isnull().all():
        st.markdown("---")
        st.markdown("### 📅 Order Load Timeline Trend")
        trend_df = filtered_df.groupby(filtered_df['OrderDate'].dt.date).size().reset_index()
        trend_df.columns = ['Date', 'Orders Count']
        
        fig_trend = px.area(trend_df, x='Date', y='Orders Count', 
                            labels={'Date': 'Timeline', 'Orders Count': 'Daily Inflow Count'})
        fig_trend.update_traces(line_color='#1D4ED8', fillcolor='rgba(37, 99, 235, 0.15)')
        fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_trend, use_container_width=True)

    # 7. Clean Data Grid & Export Hub
    st.markdown("---")
    st.markdown("### 📋 Filtered Data Grid Explorer")
    st.dataframe(filtered_df, use_container_width=True)

    # Export Facility
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Export Current View to CSV",
        data=csv_data,
        file_name="Master_Sales_Report.csv",
        mime="text/csv",
        use_container_width=True
    )

except Exception as e:
    st.error(f"Data stream syncing error: {e}")
