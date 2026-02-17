import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Page config
st.set_page_config(
    page_title="AI E-Commerce Analytics Platform",
    page_icon="📊",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv("data.csv", encoding='ISO-8859-1')
    data = data.dropna()
    data['TotalPrice'] = data['Quantity'] * data['UnitPrice']
    data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
    return data

data = load_data()

# Sidebar navigation
st.sidebar.title("📊 Analytics Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Product Analytics",
        "Customer Analytics",
        "AI Sales Prediction",
        "Project Details"
    ]
)

# Sidebar filter
st.sidebar.header("🔎 Filter")

countries = st.sidebar.multiselect(
    "Select Country",
    options=data['Country'].unique(),
    default=data['Country'].unique()
)

filtered_data = data[data['Country'].isin(countries)]

# ================= DASHBOARD =================

if page == "Dashboard":

    st.title("📊 Executive Dashboard")

    total_revenue = filtered_data['TotalPrice'].sum()
    total_orders = filtered_data['InvoiceNo'].nunique()
    total_customers = filtered_data['CustomerID'].nunique()

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Revenue", f"${total_revenue:,.2f}")
    col2.metric("📦 Orders", total_orders)
    col3.metric("👥 Customers", total_customers)

    st.divider()

    st.subheader("📈 Revenue Trend")

    sales_trend = (
        filtered_data.groupby(filtered_data['InvoiceDate'].dt.date)['TotalPrice']
        .sum()
        .reset_index()
    )

    fig = px.line(
        sales_trend,
        x='InvoiceDate',
        y='TotalPrice',
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= PRODUCT ANALYTICS =================

elif page == "Product Analytics":

    st.title("📦 Product Performance")

    top_products = (
        filtered_data.groupby('Description')['TotalPrice']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        top_products,
        x='TotalPrice',
        y='Description',
        orientation='h',
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= CUSTOMER ANALYTICS =================
# ================= CUSTOMER ANALYTICS =================

elif page == "Customer Analytics":

    st.title("👥 Customer Analytics")

    if filtered_data.empty:
        st.warning("No data available for selected filter.")
    else:

        # Clean data properly
        clean_data = filtered_data.copy()

        # Ensure valid numeric values
        clean_data = clean_data[
            (clean_data['TotalPrice'] > 0) &
            (clean_data['CustomerID'].notnull())
        ]

        # Convert CustomerID to string (important fix)
        clean_data['CustomerID'] = clean_data['CustomerID'].astype(str)

        # Aggregate spending per customer (CORPORATE METHOD)
        customer_spending = (
            clean_data.groupby('CustomerID')['TotalPrice']
            .sum()
            .reset_index()
        )

        # ================= TOP CUSTOMERS =================

        st.subheader("🏆 Top 10 Customers")

        top_customers = (
            customer_spending
            .sort_values(by='TotalPrice', ascending=False)
            .head(10)
        )

        fig = px.bar(
            top_customers,
            x='CustomerID',
            y='TotalPrice',
            title="Top Customers by Revenue",
            template="plotly_dark",
            text_auto=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # ================= SPENDING DISTRIBUTION =================

        # ================= SPENDING DISTRIBUTION =================

        st.subheader("📊 Customer Spending Distribution")

        # Aggregate spending per customer
        customer_spending = (
            clean_data.groupby('CustomerID')['TotalPrice']
            .sum()
            .reset_index()
        )

        # Sort values
        customer_spending = customer_spending.sort_values(by="TotalPrice")

        # Take top 50 customers for clear visualization
        top50_spending = customer_spending.tail(50)

        # Bar chart (more reliable than histogram)
        fig2 = px.bar(
            top50_spending,
            x='CustomerID',
            y='TotalPrice',
            title="Top 50 Customer Spending Distribution",
            template="plotly_dark"
        )

        st.plotly_chart(fig2, use_container_width=True)


        # ================= ADDITIONAL CORPORATE METRICS =================

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Customers",
            len(customer_spending)
        )

        col2.metric(
            "Average Customer Spend",
            f"${customer_spending['TotalPrice'].mean():,.2f}"
        )

        col3.metric(
            "Highest Customer Spend",
            f"${customer_spending['TotalPrice'].max():,.2f}"
        )

        st.success("✅ Customer analytics loaded successfully")

# ================= AI PREDICTION =================

elif page == "AI Sales Prediction":

    st.title("🤖 AI Sales Forecast")

    daily_sales = (
        filtered_data.groupby(filtered_data['InvoiceDate'].dt.date)['TotalPrice']
        .sum()
        .reset_index()
    )

    daily_sales['Days'] = np.arange(len(daily_sales))

    X = daily_sales[['Days']]
    y = daily_sales['TotalPrice']

    model = LinearRegression()
    model.fit(X, y)

    future_days = np.arange(len(daily_sales), len(daily_sales)+30).reshape(-1, 1)

    predictions = model.predict(future_days)

    future_dates = pd.date_range(
        start=daily_sales['InvoiceDate'].iloc[-1],
        periods=30
    )

    future_df = pd.DataFrame({
        'Date': future_dates,
        'Sales': predictions
    })

    st.metric(
        "Next Day Predicted Revenue",
        f"${predictions[0]:,.2f}"
    )

    actual_df = daily_sales[['InvoiceDate', 'TotalPrice']]
    actual_df.columns = ['Date', 'Sales']
    actual_df['Type'] = "Actual"

    future_df['Type'] = "Predicted"

    combined = pd.concat([actual_df, future_df])

    fig = px.line(
        combined,
        x='Date',
        y='Sales',
        color='Type',
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)


# ======================================================
# 5️⃣ PROJECT DETAILS SECTION
# ======================================================
elif page == "Project Details":
    st.header("📌 Project Information")

    st.markdown("""
    ### 🚗 Colorado Motor Vehicle Sales Analysis & Forecasting
    
    **Developed By:** Pranuth Manjunath  
    **Domain:** Finance Analytics / Data Science  
    **Tools Used:** Python, Pandas, Seaborn, ARIMA, Streamlit  
    """)

    st.markdown("### 📂 Download Files")

    # Download CSV
    with open("data.csv", "rb") as file:
        st.download_button(
            label="Download Dataset (CSV)",
            data=file,
            file_name="data.csv"
        )

    # Download Notebook
    st.markdown("### 📓 Download Jupyter File")
    try:
        with open("main.ipynb", "rb") as f:
            st.download_button(
                label="📓 Download Jupyter Notebook (main.ipynb)",
                data=f,
                file_name="main.ipynb",
                mime="application/octet-stream"
        )
    except:
        st.info("Notebook file not found. Add project_notebook.ipynb in folder.")

    st.markdown("### 🔗 GitHub Repository")
    if st.button("🔗 Visit GitHub Project"):
        st.write("Opening GitHub...")
        st.markdown("https://github.com/PranuthHM/ai-ecommerce-analytics-platform")


    st.success("Thank you for reviewing this project!")


# Footer
st.sidebar.info("AI E-Commerce Analytics Platform\nDeveloped by Pranuth")
