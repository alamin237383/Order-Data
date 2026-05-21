import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration & Theme Setup
st.set_page_config(page_title="SKU Wise Order Analytics", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for modern look
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #1E3A8A; font-weight: 700; }
    h2, h3 { color: #1F2937; }
    .stMetric { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #3B82F6; }
    </style>
""", unsafe_allow_html=True)

st.title("📦 SKU Wise Order Advanced Dashboard")
st.markdown("Real-time graphs, filters, and sales analytics based on your uploaded data.")

# 2. Data Loading Function
@st.cache_data
def load_data():
    file_name = "SKU Wise Order Details Dump (44).csv"
    df = pd.read_csv(file_name)
    if 'OrderDate' in df.columns:
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
    return df

try:
    df = load_data()
    
    # 3. Sidebar Filters
    st.sidebar.header("🔍 Filter Options")
    
    # Region Filter
    if 'Region' in df.columns:
        selected_region = st.sidebar.multiselect("Select Region:", options=df['Region'].unique(), default=df['Region'].unique())
        filtered_df = df[df['Region'].isin(selected_region)]
    else:
        filtered_df = df.copy()
        
    # Area Filter
    if 'Area' in filtered_df.columns:
        selected_area = st.sidebar.multiselect("Select Area:", options=filtered_df['Area'].unique(), default=filtered_df['Area'].unique())
        filtered_df = filtered_df[filtered_df['Area'].isin(selected_area)]

    # SO Name Search Filter
    if 'SO Name' in filtered_df.columns:
        search_so = st.sidebar.text_input("Search Sales Officer (SO Name):")
        if search_so:
            filtered_df = filtered_df[filtered_df['SO Name'].str.contains(search_so, case=False, na=False)]

    # 4. KPI Metrics Cards
    st.subheader("📊 Key Metrics")
    m1, m2, m3, m4 = st.columns(4)
    
    total_orders = len(filtered_df)
    m1.metric("Total Orders", f"{total_orders:,}")
    
    unique_skus = filtered_df.iloc[:, 0].nunique()
    for col in filtered_df.columns:
        if 'sku' in col.lower():
            unique_skus = filtered_df[col].nunique()
            break
            
    m2.metric("Unique SKUs", f"{unique_skus}")
    
    unique_so = filtered_df['SO Name'].nunique() if 'SO Name' in filtered_df.columns else 0
    m3.metric("Active SOs", f"{unique_so}")
    
    unique_outlets = filtered_df['Outlet Name'].nunique() if 'Outlet Name' in filtered_df.columns else 0
    m4.metric("Total Outlets", f"{unique_outlets}")

    st.markdown("---")

    # 5. Charts & Visualizations
    st.subheader("📈 Performance & Sales Charts")
    c1, c2 = st.columns(2)
    
    with c1:
        # Top 10 Sales Officers Chart
        if 'SO Name' in filtered_df.columns:
            st.markdown("### 🏆 Top 10 Sales Officers (by Orders)")
            top_so = filtered_df['SO Name'].value_counts().head(10).reset_index()
            top_so.columns = ['SO Name', 'Order Count']
            fig_so = px.bar(top_so, x='Order Count', y='SO Name', orientation='h', 
                            color='Order Count', color_continuous_scale='Blugrn',
                            labels={'Order Count': 'Number of Orders', 'SO Name': 'SO Name'})
            fig_so.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_so, use_container_width=True)

    with c2:
        # Area wise order share
        if 'Area' in filtered_df.columns:
            st.markdown("### 📍 Order Share by Area")
            area_counts = filtered_df['Area'].value_counts().head(10).reset_index()
            area_counts.columns = ['Area', 'Orders']
            fig_area = px.pie(area_counts, values='Orders', names='Area', hole=0.4,
                              color_discrete_sequence=px.colors.sequential.RdBu)
            fig_area.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_area, use_container_width=True)

    # 6. Timeline Trend Chart
    if 'OrderDate' in filtered_df.columns and not filtered_df['OrderDate'].isnull().all():
        st.markdown("### 📅 Order Trend Over Time")
        trend_df = filtered_df.groupby(filtered_df['OrderDate'].dt.date).size().reset_index()
        trend_df.columns = ['Date', 'Order Count']
        fig_trend = px.line(trend_df, x='Date', y='Order Count', markers=True,
                            labels={'Date': 'Date', 'Order Count': 'Number of Orders'})
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # 7. Data Table Preview & Download
    st.subheader("📋 Detailed Filtered Data Table")
    st.markdown(f"Showing **{len(filtered_df):,}** rows based on your current filters.")
    st.dataframe(filtered_df, use_container_width=True)

    # CSV Download Button
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name="Filtered_Order_Data.csv",
        mime="text/csv",
    )

except Exception as e:
    st.error(f"Error loading or processing data. Error Details: {e}")
