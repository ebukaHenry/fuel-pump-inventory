import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import random

st.set_page_config(page_title="FuelFlow", page_icon="⛽", layout="wide")

# Custom Styling
st.markdown("""
<style>
    .main {background-color: #f8fafc;}
    .stButton>button {background-color: #6B21A8; color: white; border-radius: 12px; height: 3em;}
</style>
""", unsafe_allow_html=True)

# Initialize Data
if 'sales_data' not in st.session_state:
    dates = pd.date_range(start='2026-04-20', periods=15).tolist()
    st.session_state.sales_data = pd.DataFrame({
        'Date': dates * 4,
        'Staff': ['Adebayo', 'Chioma', 'Tunde', 'Funke'] * 15,
        'Fuel_Type': ['Petrol', 'Diesel', 'Gas', 'Kerosene'] * 15,
        'Quantity': [random.uniform(20, 180) for _ in range(60)],
        'Amount': [random.randint(5000, 45000) for _ in range(60)]
    })

st.title("⛽ FuelFlow - Fuel Inventory & Sales")
st.caption("Professional Fuel Station Management System")

tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Record Sale", "Sales History", "Inventory"])

with tab1:
    st.subheader("Today's Performance")
    today = date.today()
    today_sales = st.session_state.sales_data[st.session_state.sales_data['Date'].dt.date == today]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"₦{today_sales['Amount'].sum():,}")
    c2.metric("Litres Sold", f"{today_sales[today_sales['Fuel_Type'] != 'Gas']['Quantity'].sum():.1f} L")
    c3.metric("Gas Sold", f"{today_sales[today_sales['Fuel_Type'] == 'Gas']['Quantity'].sum():.1f} KG")
    c4.metric("Transactions", len(today_sales))

    # Sales Trend
    st.subheader("Sales Trend")
    trend = st.session_state.sales_data.groupby('Date')['Amount'].sum().reset_index()
    fig = px.line(trend, x='Date', y='Amount', markers=True, line_color='#6B21A8')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Record New Sale")
    with st.form("sale_form", clear_on_submit=True):
        fuel = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Gas", "Kerosene"])
        qty = st.number_input("Quantity", min_value=0.1, value=45.0, step=0.5)
        amount = st.number_input("Amount (₦)", min_value=1000, value=8000, step=500)
        
        if st.form_submit_button("Save Sale"):
            new_sale = pd.DataFrame([{
                'Date': pd.Timestamp.now(),
                'Staff': "Demo Staff",
                'Fuel_Type': fuel,
                'Quantity': qty,
                'Amount': amount
            }])
            st.session_state.sales_data = pd.concat([st.session_state.sales_data, new_sale], ignore_index=True)
            st.success("✅ Sale Recorded Successfully!")

with tab3:
    st.subheader("Sales History")
    df = st.session_state.sales_data.copy()
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M')
    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

with tab4:
    st.subheader("Current Stock Levels")
    stocks = {"Petrol": 12400, "Diesel": 8750, "Gas": 1850, "Kerosene": 2450}
    for fuel, stock in stocks.items():
        st.write(f"**{fuel}**")
        st.progress(stock/20000, text=f"{stock:,} Litres / 20,000")

st.sidebar.success("App is Live!")