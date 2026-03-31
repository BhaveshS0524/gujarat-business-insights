import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from langchain_experimental.agents import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from sklearn.linear_model import LinearRegression
import numpy as np

# --- 1. CONFIGURATION & ARCHITECT SETUP ---
st.set_page_config(page_title="Gujarat Business Insights", layout="wide")

# Setup AI Architect Layers (Gemini 1.5 Flash for speed and reliability)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# LangChain LLM for Agentic AI (Phase 2)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=st.secrets["GEMINI_API_KEY"]
)

def get_ai_insight(data_summary):
    prompt = f"""
    You are a Senior Strategic Data Architect with 15 years of BFSI experience. 
    Analyze these sales metrics for a Gujarat-based SME and provide 3 high-impact, 
    actionable business strategies to improve profit margins. 
    Metrics: {data_summary}
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

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("🎯 Strategic Controls")
region_selection = st.sidebar.multiselect("Select Business Cluster", df['Region'].unique(), default=df['Region'].unique())
segment_selection = st.sidebar.selectbox("Customer Segment", df['Segment'].unique())

filtered_df = df[(df['Region'].isin(region_selection)) & (df['Segment'] == segment_selection)]

# --- 4. MAIN INTERFACE ---
st.title("🚀 Gujarat Retail Intelligence Portal")
st.markdown(f"**Target Audience:** Strategic Analysis for {segment_selection} Segment")

# Unified Tab Architecture
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Owner's Overview", 
    "🔍 Manager's Desk", 
    "🧪 Profit Optimizer", 
    "🤖 Phase 1: AI Consultant",
    "🕵️ Phase 2: Agentic AI",
    "📈 Phase 3: AI Forecaster"
])

with tab1:
    st.subheader("📈 Owner's Strategic KPIs")
    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    monthly_target = 500000  # Set as a benchmark
    sq_ft = 2000  # Baseline for Ahmedabad showrooms
    
    o_col1, o_col2, o_col3 = st.columns(3)
    
    # KPI: Net Profit (Target vs Achieved)
    o_col1.metric("Net Profit vs Target", f"₹{total_profit:,.0f}", 
                  delta=f"{((total_profit/monthly_target)*100)-100:.1f}% vs Target" if monthly_target > 0 else "0%")
    
    # KPI: Sales per Square Foot (SSPD)
    o_col2.metric("Sales per Sq. Ft. (SSPD)", f"₹{total_sales/sq_ft:,.2f}", help="Based on 2,000 Sq. Ft.")
    
    # KPI: Budget vs Profit (Using 15% op-ex baseline)
    op_budget = total_sales * 0.15
    o_col3.metric("Profit vs Op-Ex Budget", f"₹{total_profit:,.0f}", delta=f"Budget: ₹{op_budget:,.0f}", delta_color="normal")
    
    fig_sales = px.line(filtered_df.groupby('Order Date')['Sales'].sum().reset_index(), 
                        x='Order Date', y='Sales', title="Revenue Trend (Gujarat Clusters)")
    st.plotly_chart(fig_sales, use_container_width=True)

with tab2:
    st.subheader("⚙️ Manager's Operational Metrics")
    total_orders = filtered_df['Order ID'].nunique()
    total_units = filtered_df['Quantity'].sum()
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    # KPI: Average Bill Value (ABV)
    abv = total_sales / total_orders if total_orders > 0 else 0
    m_col1.metric("Avg Bill Value (ABV)", f"₹{abv:,.2f}")
    
    # KPI: Average Sale Price (ASP)
    asp = total_sales / total_units if total_units > 0 else 0
    m_col2.metric("Avg Sale Price (ASP)", f"₹{asp:,.2f}")
    
    # KPI: Unit Per Transaction (UPT)
    upt = total_units / total_orders if total_orders > 0 else 0
    m_col3.metric("Units Per Txn (UPT)", f"{upt:.2f}")
    
    # KPI: Conversion (Simulated monthly baseline)
    footfall = 5000 
    conversion = (total_orders / footfall) * 100 if footfall > 0 else 0
    m_col4.metric("Conversion Rate", f"{conversion:.1f}%")

    st.write("---")
    st.write("**Product Risk Analysis**")
    loss_df = filtered_df[filtered_df['Profit'] < 0].groupby('Product Name')['Profit'].sum().nsmallest(5).reset_index()
    st.dataframe(loss_df, use_container_width=True)

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
    if st.button("Generate Executive Strategy"):
        summary = {
            "Total Sales": total_sales,
            "Total Profit": total_profit,
            "Avg Discount": filtered_df['Discount'].mean(),
            "ABV": total_sales / total_orders if total_orders > 0 else 0
        }
        with st.spinner("Architecting strategy..."):
            advice = get_ai_insight(summary)
            st.markdown(advice)

with tab5:
    st.subheader("Phase 2: Agentic AI Strategist")
    st.info("Ask ad-hoc questions (e.g., 'Which city in Gujarat has the highest shipping cost?')")
    agent = create_csv_agent(llm, 'samplesuperstore.csv', verbose=True, allow_dangerous_code=True)
    user_query = st.text_input("Enter your business question:")
    if user_query:
        with st.spinner("Agent exploring data architecture..."):
            response = agent.run(user_query)
            st.write(response)

with tab6:
    st.subheader("Phase 3: AI Sales Forecaster")
    forecast_df = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
    forecast_df['Day_Ordinal'] = forecast_df['Order Date'].map(pd.Timestamp.toordinal)
    
    if len(forecast_df) > 5:
        X = forecast_df[['Day_Ordinal']].values
        y = forecast_df['Sales'].values
        model_lr = LinearRegression().fit(X, y)
        
        future_days = np.array([X[-1][0] + i for i in range(1, 31)]).reshape(-1, 1)
        predictions = model_lr.predict(future_days)
        
        st.success(f"Projected Revenue (Next 30 Days): ₹{predictions.sum():,.0f}")
        fig_forecast = px.line(x=range(1, 31), y=predictions, labels={'x': 'Days Ahead', 'y': 'Sales'}, title="30-Day Forward Forecast")
        st.plotly_chart(fig_forecast, use_container_width=True)
    else:
        st.warning("Insufficient data for a reliable forecast.")

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💼 Bhavesh Suryavanshi")
st.sidebar.markdown("*AI Solutions Architect | Data Strategist*")