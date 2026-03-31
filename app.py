import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from langchain_experimental.agents import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# --- 1. CONFIGURATION & ARCHITECT SETUP ---
st.set_page_config(page_title="Gujarat Business Insights", layout="wide")

# Setup AI Architect Layers (Phase 1 & 2)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel('gemini-pro')

# LangChain Agent for Phase 2
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=st.secrets["GEMINI_API_KEY"])

def get_ai_insight(data_summary):
    prompt = f"""
    You are a Senior Strategic Data Architect with 15 years of BFSI experience. 
    Analyze these sales metrics for a Gujarat-based SME and provide 3 high-impact, 
    actionable business strategies to improve profit margins. 
    Metrics: {data_summary}
    Focus on: Discount control, Regional optimization, and Category management.
    """
    response = gemini_model.generate_content(prompt)
    return response.text

# --- 2. DATA PREPARATION (Module 2 Skills) ---
@st.cache_data
def load_data():
    df = pd.read_csv('samplesuperstore.csv')
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

# --- 3. SIDEBAR FILTERS ---
st.sidebar.header("🎯 Strategic Controls")
region_selection = st.sidebar.multiselect("Select Business Cluster", df['Region'].unique(), default=df['Region'].unique())
segment_selection = st.sidebar.selectbox("Customer Segment", df['Segment'].unique())

filtered_df = df[(df['Region'].isin(region_selection)) & (df['Segment'] == segment_selection)]

# --- 4. MAIN INTERFACE ---
st.title("🚀 Gujarat Retail Intelligence Portal")
st.markdown(f"**Strategic Analysis for:** {segment_selection} Segment")

# Unified Tab Architecture
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Summary", 
    "🔍 Operational Deep Dive", 
    "🧪 Profit Optimizer", 
    "🤖 Phase 1: AI Consultant",
    "🕵️ Phase 2: Agentic AI Strategist"
])

with tab1:
    st.subheader("High-Level Performance (Owner's View)")
    kpi1, kpi2, kpi3 = st.columns(3)
    sales_val = filtered_df['Sales'].sum()
    profit_val = filtered_df['Profit'].sum()
    
    kpi1.metric("Total Sales", f"₹{sales_val:,.0f}")
    kpi2.metric("Net Profit", f"₹{profit_val:,.0f}", delta=f"{(profit_val/sales_val)*100:.1f}% Margin" if sales_val != 0 else "0%")
    kpi3.metric("Orders", len(filtered_df))
    
    fig_sales = px.line(filtered_df.groupby('Order Date')['Sales'].sum().reset_index(), 
                        x='Order Date', y='Sales', title="Revenue Trend (Gujarat Clusters)")
    st.plotly_chart(fig_sales, use_container_width=True)

with tab2:
    st.subheader("Manager's View (Operational Risk)")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Top Loss-Making Products**")
        loss_df = filtered_df[filtered_df['Profit'] < 0].groupby('Product Name')['Profit'].sum().nsmallest(5).reset_index()
        st.dataframe(loss_df)
    with col2:
        fig_pie = px.pie(filtered_df, values='Sales', names='Category', title="Sales Distribution")
        st.plotly_chart(fig_pie)

with tab3:
    st.subheader("Profit Optimizer (Strategic View)")
    st.write("Simulate: What if we reduce the average discount by X%?")
    current_profit = filtered_df['Profit'].sum()
    sim_discount_reduction = st.slider("Reduction in Discount %", 0, 20, 5)
    simulated_profit = current_profit + (filtered_df['Sales'].sum() * (sim_discount_reduction/100))
    
    st.warning(f"Projected Profit Increase: ₹{simulated_profit - current_profit:,.0f}")
    st.info(f"New Potential Profit: ₹{simulated_profit:,.0f}")

with tab4:
    st.subheader("Phase 1: AI Strategic Consultant")
    st.write("Automated high-level strategy based on current filters.")
    if st.button("Generate Executive Strategy"):
        summary = {
            "Total Sales": filtered_df['Sales'].sum(),
            "Total Profit": filtered_df['Profit'].sum(),
            "Avg Discount": filtered_df['Discount'].mean(),
            "Top Category": filtered_df.groupby('Category')['Profit'].sum().idxmax()
        }
        with st.spinner("Architecting strategy..."):
            advice = get_ai_insight(summary)
            st.markdown(advice)

with tab5:
    st.subheader("Phase 2: Agentic AI Strategist")
    st.info("Ask ad-hoc questions (e.g., 'Which city has the highest shipping cost per order?')")
    
    # Initialize Agent for CSV
    agent = create_csv_agent(llm, 'samplesuperstore.csv', verbose=True, allow_dangerous_code=True)
    
    user_query = st.text_input("Enter your business question:")
    if user_query:
        with st.spinner("Agent is exploring data architecture..."):
            response = agent.run(user_query)
            st.write(response)

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💼 Bhavesh Suryavanshi")
st.sidebar.markdown("*AI Solutions Architect | Data Strategist*")