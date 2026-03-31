import streamlit as st
import pandas as pd
import plotly.express as px

# --- DATA PREPARATION (Module 2 Skills) ---
@st.cache_data
def load_data():
    df = pd.read_csv('samplesuperstore.csv')
    # Localize Regions for Ahmedabad/Gujarat context
    region_map = {
        'Central': 'Ahmedabad Hub',
        'West': 'Rajkot/Saurashtra',
        'South': 'Surat/South Gujarat',
        'East': 'Vadodara/North Gujarat'
    }
    df['Region'] = df['Region'].map(region_map)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🎯 Meeting Controls")
region = st.sidebar.multiselect("Select Business Cluster", df['Region'].unique(), default=df['Region'].unique())
segment = st.sidebar.selectbox("Customer Segment", df['Segment'].unique())

filtered_df = df[(df['Region'].isin(region)) & (df['Segment'] == segment)]

# --- 1. IMPORTS (At the very top) ---
import streamlit as st
import pandas as pd
import google.generativeai as genai  # Add this

# --- 2. DATA LOADING & FILTERING ---
df = pd.read_csv('samplesuperstore.csv')
# ... (your existing filtering code) ...
filtered_df = df[df['Region'].isin(region)] # Example line

# ==========================================
# INSERT AI ARCHITECT LAYER HERE
# ==========================================

# Setup AI (using your secret key from Streamlit Cloud)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

def get_ai_insight(data_summary):
    prompt = f"""
    You are a Senior Strategic Data Architect with 15 years of BFSI experience. 
    Analyze these sales metrics for a Gujarat-based SME and provide 3 high-impact, 
    actionable business strategies to improve profit margins. 
    Metrics: {data_summary}
    Focus on: Discount control, Regional optimization, and Category management.
    """
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# END OF AI ARCHITECT LAYER
# ==========================================

# --- 3. UI TABS & VISUALS ---
tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "🔍 Deep Dive", "🧪 AI Consultant"])

with tab3:
    st.subheader("🤖 AI Strategic Consultant")
    if st.button("Generate AI Business Strategy"):
        # Create the summary for the AI to read
        summary = {
            "Total Sales": filtered_df['Sales'].sum(),
            "Total Profit": filtered_df['Profit'].sum(),
            "Avg Discount": filtered_df['Discount'].mean(),
            "Top Category": filtered_df.groupby('Category')['Profit'].sum().idxmax()
        }
        
        with st.spinner("Architecting your strategy..."):
            advice = get_ai_insight(summary)
            st.markdown("### Executive Recommendations")
            st.write(advice)

# --- MAIN INTERFACE ---
st.title("🚀 Gujarat Retail Intelligence Portal")
st.markdown(f"**Target Audience:** Sales Meetings for {segment} Segment")

# TABS FOR DIFFERENT USERS
tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "🔍 Manager's Deep Dive", "🧪 What-If Simulator"])

with tab1:
    st.subheader("High-Level Performance (Owner's View)")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Sales", f"₹{filtered_df['Sales'].sum():,.0f}")
    kpi2.metric("Net Profit", f"₹{filtered_df['Profit'].sum():,.0f}", delta=f"{filtered_df['Profit'].sum()/filtered_df['Sales'].sum():.1%} Margin")
    kpi3.metric("Orders", len(filtered_df))
    
    fig_sales = px.line(filtered_df.groupby('Order Date')['Sales'].sum().reset_index(), 
                        x='Order Date', y='Sales', title="Revenue Trend (Gujarat Clusters)")
    st.plotly_chart(fig_sales, use_container_width=True)

with tab2:
    st.subheader("Operational Analytics (Manager's View)")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Top Loss-Making Products")
        loss_df = filtered_df[filtered_df['Profit'] < 0].groupby('Product Name')['Profit'].sum().nsmallest(5).reset_index()
        st.dataframe(loss_df)
    with col2:
        fig_pie = px.pie(filtered_df, values='Sales', names='Category', title="Sales Distribution")
        st.plotly_chart(fig_pie)

with tab3:
    st.subheader("Profit Optimizer (Strategic View)")
    st.write("Simulate: What if we reduce the average discount by 5%?")
    current_profit = filtered_df['Profit'].sum()
    # Simple simulation logic
    sim_discount_reduction = st.slider("Reduction in Discount %", 0, 20, 5)
    simulated_profit = current_profit + (filtered_df['Sales'].sum() * (sim_discount_reduction/100))
    
    st.warning(f"Projected Profit Increase: ₹{simulated_profit - current_profit:,.0f}")
    st.info(f"New Potential Profit: ₹{simulated_profit:,.0f}")