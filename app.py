import streamlit as st
import pandas as pd

# Dashboard configuration
st.set_page_config(page_title="Order Dashboard", layout="wide")
st.title("📦 SKU Wise Order Details Dashboard")

# Load data based on your uploaded file name
@st.cache_data
def load_data():
    file_name = "SKU Wise Order Details Dump (44).csv"
    df = pd.read_csv(file_name)
    return df

try:
    df = load_data()
    st.success("Data successfully loaded!")

    # Summary Metrics (KPI)
    st.subheader("📊 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", len(df))
    col2.metric("Unique SKUs", df.iloc[:, 0].nunique()) 
    col3.metric("Status", "Active")

    # Data Table Preview
    st.subheader("📄 Data Table (Preview)")
    st.dataframe(df.head(50)) # Shows first 50 rows

    # Graphical View
    st.subheader("📈 Graphical View")
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty:
        st.line_chart(numeric_df.iloc[:, 0])
    else:
        st.write("No numeric columns found to plot a chart.")

except Exception as e:
    st.error(f"Error loading data. Please ensure the file name matches exactly. Error: {e}")
