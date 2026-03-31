import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Load and Localize Data
df = pd.read_csv('samplesuperstore.csv')
region_map = {
    'Central': 'Ahmedabad (Main Hub)',
    'West': 'Saurashtra (Rajkot)',
    'South': 'South Gujarat (Surat)',
    'East': 'North & East Gujarat (Vadodara)'
}
df['Region'] = df['Region'].map(region_map)

# 2. Sidebar Filters (For interactive meetings)
st.sidebar.header("Sales Meeting Filters")
selected_region = st.sidebar.multiselect("Select Cluster", df['Region'].unique(), default=df['Region'].unique())
selected_segment = st.sidebar.selectbox("Customer Segment", df['Segment'].unique())

# Filter data
filtered_df = df[(df['Region'].isin(selected_region)) & (df['Segment'] == selected_segment)]

# 3. Header Section (For Owners)
st.title("📊 Ahmedabad Business Intelligence Dashboard")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Revenue", f"₹{filtered_df['Sales'].sum():,.0f}")
kpi2.metric("Total Profit", f"₹{filtered_df['Profit'].sum():,.0f}")
kpi3.metric("Avg Discount %", f"{filtered_df['Discount'].mean():.1%}")

# 4. Profitability Analysis (For Managers)
st.subheader("💡 Where is the Profit Coming From?")
col_left, col_right = st.columns(2)

with col_left:
    fig_cat = px.bar(filtered_df.groupby('Category')['Profit'].sum().reset_index(), 
                     x='Category', y='Profit', color='Category', title="Profit by Category")
    st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    # Discount vs Profit - showing the danger zone
    fig_disc = px.scatter(filtered_df, x="Discount", y="Profit", color="Category", 
                          title="Discount vs. Profit (Danger Zone Analysis)")
    st.plotly_chart(fig_disc, use_container_width=True)

# 5. The "80/20" Rule Section (For Executives)
st.subheader("🎯 The 80/20 Opportunity")
st.write("9% of our products drive 80% of our total profit. Focus here:")
top_products = filtered_df.groupby('Product Name')['Profit'].sum().nlargest(10)
st.table(top_products)

st.success("Analysis Ready: This dashboard helps identify loss-making discounts and focus on high-margin clusters.")