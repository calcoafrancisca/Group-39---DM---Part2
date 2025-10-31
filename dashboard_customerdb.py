# dashboard_customerdb_complete.py

import streamlit as st
import pandas as pd
import plotly.express as px
import math

# ------------------------------
# 1️⃣ LOAD DATA
# ------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\calco\OneDrive\Documentos\GitHub\DM_project\CustomerDB.csv")
    return df

df = load_data()

# ------------------------------
# 2️⃣ DASHBOARD TITLE
# ------------------------------
st.title("✈️ Customer Insights Dashboard")
st.markdown("Explore demographic and loyalty program characteristics interactively.")

# ------------------------------
# 3️⃣ SIDEBAR FILTERS
# ------------------------------
st.sidebar.header("🔍 Filters")

selected_status = st.sidebar.multiselect(
    "Loyalty Status:",
    options=df["LoyaltyStatus"].dropna().unique(),
    default=df["LoyaltyStatus"].dropna().unique()
)

selected_province = st.sidebar.multiselect(
    "Province/State:",
    options=df["Province or State"].dropna().unique(),
    default=df["Province or State"].dropna().unique()
)

income_range = st.sidebar.slider(
    "Select Income Range:",
    int(df["Income"].min()),
    int(df["Income"].max()),
    (int(df["Income"].min()), int(df["Income"].max()))
)

selected_gender = st.sidebar.multiselect(
    "Selected Gender:",
    options=df["Gender"].dropna().unique(),
    default=df["Gender"].dropna().unique()
)

selected_education = st.sidebar.multiselect(
    "Selected Education:",
    options=df["Education"].dropna().unique(),
    default=df["Education"].dropna().unique()
)

filtered_df = df[
    (df["LoyaltyStatus"].isin(selected_status)) &
    (df["Province or State"].isin(selected_province)) &
    (df["Income"] >= income_range[0]) &
    (df["Income"] <= income_range[1])
]

# ------------------------------
# 4️⃣ RAW DATA PREVIEW
# ------------------------------
st.markdown("### Raw Data Preview")
st.dataframe(filtered_df)

# ------------------------------
# 5️⃣ KPIs / OVERVIEW
# ------------------------------
st.subheader("📊 Overview Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", len(filtered_df))
col2.metric("Active Provinces", filtered_df["Province or State"].nunique())
col3.metric("Average Income", f"${filtered_df['Income'].mean():,.0f}")
col4.metric("Average Customer Lifetime Value", f"${filtered_df['Customer Lifetime Value'].mean():,.0f}")

# ------------------------------
# 6️⃣ DESCRIPTIVE STATISTICS
# ------------------------------
st.subheader("📋 Descriptive Statistics for All Variables")

# Compute descriptive statistics for all types
desc_all = filtered_df.describe(include='all').transpose()

# Optional: clean up visuals (replace NaNs for readability)
desc_all = desc_all.fillna("—")

# Display in Streamlit
st.dataframe(desc_all, use_container_width=True)

# ------------------------------
# Univariate Analysis 

categorical_columns_customer = filtered_df.select_dtypes(include='object').columns.tolist()
exclude_cols = ['First Name', 'Last Name', 'Customer Name', 'Postal Code', 'City', 'Province or State', 'EnrollmentDateOpening', 'CancellationDate']
categorical_cols_filtered = [col for col in categorical_columns_customer if col not in exclude_cols]

cols_per_row = 3
num_rows = math.ceil(len(categorical_cols_filtered) / cols_per_row)

# Organize plots row by row
for i in range(num_rows):
    cols = st.columns(cols_per_row)
    for j in range(cols_per_row):
        idx = i * cols_per_row + j
        if idx < len(categorical_cols_filtered):
            col_name = categorical_cols_filtered[idx]
            fig = px.histogram(filtered_df, x=col_name, color=col_name,
                               title=col_name, text_auto=True)
            cols[j].plotly_chart(fig, use_container_width=True)

# ------------------------------
# 7️⃣ VISUALIZATIONS LADO A LADO
# ------------------------------

# Loyalty Tier + Gender Distribution
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Loyalty Tier Distribution")
    fig1 = px.histogram(filtered_df, x="LoyaltyStatus", color="LoyaltyStatus",
                        title="Distribution of Loyalty Status",
                        color_discrete_sequence=["#4A90E2"])
    st.plotly_chart(fig1, width='stretch')
with col2:
    st.markdown("### Gender Distribution")
    fig2 = px.histogram(filtered_df, x="Gender", color="LoyaltyStatus",
                        barmode="group", title="Gender Distribution across Loyalty Tiers")
    st.plotly_chart(fig2, width='stretch')

# Income vs CLV + CLV by Education
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Income vs Customer Lifetime Value")
    fig3 = px.scatter(filtered_df, x="Income", y="Customer Lifetime Value", color="LoyaltyStatus",
                      hover_data=["Education", "Marital Status"], title="Income vs CLV")
    st.plotly_chart(fig3, width='stretch')
with col2:
    st.markdown("### CLV by Education Level")
    fig4 = px.box(filtered_df, x="Education", y="Customer Lifetime Value", color="LoyaltyStatus",
                  title="CLV by Education Level")
    st.plotly_chart(fig4, width='stretch')

# Income by Education + Enrollment Trends
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Income by Education Level")
    fig5 = px.box(filtered_df, x="Education", y="Income", color="LoyaltyStatus",
                  title="Income Distribution by Education Level")
    st.plotly_chart(fig5, width='stretch')
with col2:
    filtered_df["EnrollmentYear"] = pd.to_datetime(filtered_df["EnrollmentDateOpening"]).dt.year
    st.markdown("### Enrollment Trends by Loyalty Status")
    fig6 = px.histogram(filtered_df, x="EnrollmentYear", color="LoyaltyStatus",
                        title="Enrollment Trends")
    st.plotly_chart(fig6, width='stretch')


# ------------------------------
# 8️⃣ SCATTER MATRIX
# ------------------------------
st.markdown("### Scatter Matrix of Numeric Variables")
num_cols = ['Income', 'Customer Lifetime Value']
fig8 = px.scatter_matrix(filtered_df, dimensions=num_cols, color='LoyaltyStatus', title="Scatter Matrix")
st.plotly_chart(fig8, width='stretch')

# ------------------------------
# 9️⃣ CORRELATION MATRIX
# ------------------------------
st.markdown("### Correlation Matrix")
numeric_cols = filtered_df.select_dtypes(include='number').columns
corr_matrix = filtered_df[numeric_cols].corr()

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Heatmap")
    fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='Blues',
                         title="Correlation Heatmap")
    st.plotly_chart(fig_corr, width='stretch')

