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
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_orders = len(df)
        st.metric(label="Total Lines/Orders Ordered", value=f"{total_orders:,}")
        
    with col2:
        if 'OrderDate' in df.columns and 'Outlet Code' in df.columns:
            total_memos = df.groupby(['OrderDate', 'Outlet Code']).ngroups
        elif 'Outlet Code' in df.columns:
            total_memos = df['Outlet Code'].nunique()
        else:
            total_memos = df.iloc[:, 0].nunique()
        st.metric(label="Total Memos Cut (Productive Memos)", value=f"{total_memos:,}")
        
    with col3:
        unique_so = df['SO Name'].nunique() if 'SO Name' in df.columns else 0
        st.metric(label="Active Sales Officers (SO)", value=f"{unique_so}")
        
    with col4:
        unique_brands = 0
        for col in df.columns:
            if 'brand' in col.lower():
                unique_brands = df[col].nunique()
                break
        st.metric(label="Total Brands Distributed", value=f"{unique_brands if unique_brands > 0 else 'N/A'}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Graphical Panels (Brand-wise Analysis & Top Performers)
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        brand_column = None
        for col in df.columns:
            if 'brand' in col.lower():
                brand_column = col
                break
                
        if brand_column:
            st.markdown(f"### 🏷️ Brand Wise Order Distribution")
            brand_data = df[brand_column].value_counts().reset_index()
            brand_data.columns = ['Brand', 'Total Orders']
            
            fig_brand = px.bar(brand_data, x='Total Orders', y='Brand', orientation='h',
                               color='Total Orders', color_continuous_scale='Agsunset',
                               labels={'Total Orders': 'Order Counts'})
            fig_brand.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_brand, use_container_width=True)
        else:
            st.info("💡 Note: To display Brand chart, ensure your dataset contains a column named 'Brand' or 'Brand Name'.")

    with chart_col2:
        if 'SO Name' in df.columns:
            st.markdown("### 🏆 Top 10 Sales Officers (By Order Count)")
            top_so = df['SO Name'].value_counts().head(10).reset_index()
            top_so.columns = ['SO Name', 'Count']
            
            fig_so = px.bar(top_so, x='Count', y='SO Name', orientation='h',
                            color='Count', color_continuous_scale='Blues')
            fig_so.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_so, use_container_width=True)

    # 6. Order Timeline Flow Analytics
    if 'OrderDate' in df.columns and not df['OrderDate'].isnull().all():
        st.markdown("---")
        st.markdown("### 📅 Continuous Order Load Timeline")
        trend_df = df.groupby(df['OrderDate'].dt.date).size().reset_index()
        trend_df.columns = ['Date', 'Orders']
        
        fig_trend = px.area(trend_df, x='Date', y='Orders')
        fig_trend.update_traces(line_color='#2563EB', fillcolor='rgba(37, 99, 235, 0.1)')
        fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_trend, use_container_width=True)

    # 7. Raw Dataset Explorer Grid & Export Command
    st.markdown("---")
    st.markdown("### 📋 Filtered Dataset Explorer")
    st.dataframe(df, use_container_width=True)

    # Sidebar data download export utility
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Download Active Report (CSV)",
        data=csv_data,
        file_name="Filtered_Sales_Execution_Report.csv",
        mime="text/csv",
        use_container_width=True
    )

except Exception as e:
    st.error(f"Operational breakdown: {e}")
