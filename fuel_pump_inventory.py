import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import random

# ====================== CONFIG ======================
st.set_page_config(
    page_title="FuelFlow - Inventory",
    page_icon="⛽",
    layout="wide"
)

# Custom CSS - Purple, White, Red theme
st.markdown("""
<style>
    .main {background-color: #f8fafc;}
    .stButton>button {background-color: #6B21A8; color: white; border-radius: 12px;}
    .stButton>button:hover {background-color: #581c87;}
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid #e9d5ff;
    }
</style>
""", unsafe_allow_html=True)

# ====================== DATA ======================
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame({
        'Date': pd.date_range(start='2026-04-26', periods=8).tolist() * 3,
        'Staff': ['Adebayo', 'Chioma', 'Tunde'] * 8,
        'Fuel_Type': ['Petrol', 'Diesel', 'Gas', 'Kerosene'] * 6,
        'Quantity': [random.randint(40, 180) for _ in range(24)],
        'Amount': [random.randint(8000, 45000) for _ in range(24)]
    })
    # Fix Gas unit
    st.session_state.sales_data.loc[st.session_state.sales_data['Fuel_Type'] == 'Gas', 'Quantity'] = \
        st.session_state.sales_data.loc[st.session_state.sales_data['Fuel_Type'] == 'Gas', 'Quantity'] // 2

# ====================== SIDEBAR ======================
st.sidebar.image("https://img.icons8.com/fluency/96/gas-station.png", width=80)
st.sidebar.title("FuelFlow")
st.sidebar.markdown("**Inventory & Sales**")

role = st.sidebar.radio("Select Role", ["Staff", "Admin"], horizontal=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Date Filter")
filter_date = st.sidebar.date_input("Select Date", value=date.today())

# ====================== LOGIN SIMULATION ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

if not st.session_state.logged_in:
    st.title("🔐 FuelFlow Login")
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", value="adebayo" if role == "Staff" else "admin")
    with col2:
        password = st.text_input("Password", type="password", value="1234")
    
    if st.button("Login", type="primary"):
        st.session_state.logged_in = True
        st.session_state.current_user = username.capitalize()
        st.success(f"Welcome, {st.session_state.current_user}!")
        st.rerun()
    st.stop()

# ====================== MAIN APP ======================
st.title(f"⛽ FuelFlow - {role} Dashboard")
st.caption(f"Logged in as: **{st.session_state.current_user}** | Today: {datetime.now().strftime('%B %d, %Y')}")

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🛢️ Record Sale", "📜 Sales History", "📦 Inventory"])

with tab1:
    st.subheader("Today's Overview")
    
    today_sales = st.session_state.sales_data[st.session_state.sales_data['Date'].dt.date == filter_date]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sales", f"₦{today_sales['Amount'].sum():,}", "↑ 12%")
    with col2:
        st.metric("Litres Sold", f"{today_sales[today_sales['Fuel_Type'] != 'Gas']['Quantity'].sum():,} L")
    with col3:
        st.metric("Gas Sold", f"{today_sales[today_sales['Fuel_Type'] == 'Gas']['Quantity'].sum():,} KG")
    with col4:
        st.metric("Transactions", len(today_sales))

    # Sales Trend Graph
    st.subheader("Sales Trend (Last 7 Days)")
    trend = st.session_state.sales_data.groupby('Date')['Amount'].sum().reset_index()
    fig = px.line(trend, x='Date', y='Amount', markers=True,
                  color_discrete_sequence=['#6B21A8'])
    fig.update_layout(height=400, template="simple_white")
    st.plotly_chart(fig, use_container_width=True)

    # Item Breakdown
    st.subheader("Sales by Fuel Type")
    breakdown = today_sales.groupby('Fuel_Type').agg({'Quantity': 'sum', 'Amount': 'sum'}).reset_index()
    fig2 = px.bar(breakdown, x='Fuel_Type', y='Amount', color='Fuel_Type',
                  color_discrete_sequence=['#6B21A8', '#DC2626', '#7C3AED', '#F59E0B'])
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Record New Sale")
    
    with st.form("sale_form"):
        fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Gas", "Kerosene"])
        col_a, col_b = st.columns(2)
        with col_a:
            quantity = st.number_input("Quantity", min_value=0.1, value=45.0, step=0.5)
        with col_b:
            unit = "KG" if fuel_type == "Gas" else "Litres"
            st.write(f"**Unit:** {unit}")
        
        amount = st.number_input("Amount (₦)", min_value=1000, value=6750, step=100)
        
        submitted = st.form_submit_button("✅ Save Sale")
        if submitted:
            new_row = pd.DataFrame({
                'Date': [pd.Timestamp.now()],
                'Staff': [st.session_state.current_user],
                'Fuel_Type': [fuel_type],
                'Quantity': [quantity],
                'Amount': [amount]
            })
            st.session_state.sales_data = pd.concat([st.session_state.sales_data, new_row], ignore_index=True)
            st.success(f"Sale recorded successfully by **{st.session_state.current_user}**!")
            st.balloons()

with tab3:
    st.subheader("Sales History")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=date(2026, 4, 26))
    with col2:
        end_date = st.date_input("To", value=date.today())
    
    filtered = st.session_state.sales_data[
        (st.session_state.sales_data['Date'].dt.date >= start_date) &
        (st.session_state.sales_data['Date'].dt.date <= end_date)
    ].copy()
    
    filtered['Date'] = filtered['Date'].dt.strftime('%Y-%m-%d %H:%M')
    
    st.dataframe(
        filtered.sort_values('Date', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn(format="₦%,d"),
            "Quantity": st.column_config.NumberColumn(format="%.1f")
        }
    )
    
    if not filtered.empty:
        csv = filtered.to_csv(index=False)
        st.download_button("📥 Download History", csv, "fuel_sales_history.csv", "text/csv")

with tab4:
    st.subheader("Current Inventory Levels")
    inventory = {
        "Petrol": {"stock": 8420, "capacity": 15000, "color": "#6B21A8"},
        "Diesel": {"stock": 6350, "capacity": 12000, "color": "#DC2626"},
        "Gas": {"stock": 1240, "capacity": 3000, "color": "#7C3AED"},
        "Kerosene": {"stock": 980, "capacity": 8000, "color": "#F59E0B"}
    }
    
    for fuel, data in inventory.items():
        percent = (data['stock'] / data['capacity']) * 100
        st.write(f"**{fuel}**")
        st.progress(percent/100, text=f"{data['stock']:,} / {data['capacity']:,} ({percent:.1f}%)")
        if percent < 30:
            st.warning("Low Stock Alert!", icon="⚠️")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("FuelFlow Demo v1.0 • Built with Streamlit")
