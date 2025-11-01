import streamlit as st
import pandas as pd
import plotly.express as px

###### ver que graficos meter em cada uma das analises e colocar o boxplot a mostrar os outliers #####


st.set_page_config(
    page_title="Customer Insights Dashboard",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Customer Insights Dashboard")
st.markdown("""
Interactive dashboard for exploring CustomerDB data.
Analyze univariate, bivariate, and multivariate relationships with filters and interactive visuals.
""")


# ------------------------------
# 1️⃣ Load Data
# ------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("CustomerDB_clean.csv")

    # Drop the unwanted column if it exists
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    df['EnrollmentDateOpening'] = pd.to_datetime(df['EnrollmentDateOpening'], errors='coerce')
    df['CancellationDate'] = pd.to_datetime(df['CancellationDate'], errors='coerce')
    return df

df = load_data()

numeric_cols = df.select_dtypes(include='number').columns.tolist()
categorical_cols = df.select_dtypes(include='object').columns.tolist()

st.subheader("📄 Customer Data Table")
st.write(f"Showing {len(df)} rows after applied filters")
st.dataframe(df, use_container_width=True)

# ------------------------------
# 0️⃣ KPIs / Overview
# ------------------------------

st.subheader("📊 Overview Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Customers", len(df))
col2.metric("Active Provinces/States", df["Province or State"].nunique())
col3.metric("Average Income", f"${df['Income'].mean():,.0f}")
col4.metric("Average Customer Lifetime Value", f"${df['Customer Lifetime Value'].mean():,.0f}")
col5.metric("Total Cancellations", df['CancellationDate'].notna().sum())

# ------------------------------
# 4️⃣ Univariate Analysis
# ------------------------------
st.subheader("1️⃣ Univariate Analysis")
uni_feature = st.selectbox("Select a variable", df.columns.tolist(), key="uni_feature")

if uni_feature in numeric_cols:
    # Layout horizontal com 2 colunas
    col1, col2 = st.columns(2)
    
    # Histograma
    with col1:
        fig_hist = px.histogram(
            df,
            x=uni_feature,
            nbins=30,
            opacity=0.8,
            color_discrete_sequence=['#1f77b4'],
            title=f"Histogram of {uni_feature}"
        )
        fig_hist.update_layout(
            bargap=0.2,
            xaxis_title=uni_feature,
            yaxis_title="Count",
            template="plotly_white"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        fig_box = px.box(
            df,
            x=uni_feature,  # horizontal
            points=False,   # remove todos os pontos
            color_discrete_sequence=['#1f77b4'],  # mesma cor do histograma
            title=f"Boxplot of {uni_feature}"
        )
        fig_box.update_layout(
            yaxis=dict(showticklabels=False),  # remove eixo vertical desnecessário
            template="plotly_white"
        )
        st.plotly_chart(fig_box, use_container_width=True)

else:
    # Para variáveis categóricas, apenas histograma
    fig_cat = px.histogram(
        df,
        x=uni_feature,
        opacity=0.8,
        color_discrete_sequence=['#1f77b4'],
        title=f"Histogram of {uni_feature}"
    )
    fig_cat.update_layout(
        xaxis_title=uni_feature,
        yaxis_title="Count",
        template="plotly_white"
    )
    st.plotly_chart(fig_cat, use_container_width=True)


# ------------------------------
# 5️⃣ Bivariate Analysis
# ------------------------------
st.subheader("2️⃣ Bivariate Analysis")
bivar_feature_x = st.selectbox("Select X feature", df.columns.tolist(), key="bivar_x")
bivar_feature_y = st.selectbox("Select Y feature", df.columns.tolist(), key="bivar_y")

# Determine types
is_x_numeric = bivar_feature_x in numeric_cols
is_y_numeric = bivar_feature_y in numeric_cols
is_x_cat = bivar_feature_x in categorical_cols
is_y_cat = bivar_feature_y in categorical_cols

col1, col2 = st.columns(2)

with col1:
    if is_x_numeric and is_y_numeric:
        fig = px.scatter(
            df,
            x=bivar_feature_x,
            y=bivar_feature_y,
            color='LoyaltyStatus',
            trendline="ols",
            hover_data=df.columns,
            title=f"{bivar_feature_x} vs {bivar_feature_y} (Numeric vs Numeric)",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            opacity=0.7
        )
    elif is_x_cat and is_y_cat:
        cross_tab = pd.crosstab(df[bivar_feature_x], df[bivar_feature_y])
        fig = px.imshow(
            cross_tab,
            text_auto=True,
            color_continuous_scale="Blues",
            title=f"{bivar_feature_x} vs {bivar_feature_y} (Categorical vs Categorical)"
        )
    else:
        # Mixed types → box plot
        if is_x_numeric and is_y_cat:
            fig = px.box(
                df,
                x=bivar_feature_y,
                y=bivar_feature_x,
                color=bivar_feature_y,
                points="all",
                title=f"{bivar_feature_x} (Numeric) by {bivar_feature_y} (Categorical)",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
        else:
            fig = px.box(
                df,
                x=bivar_feature_x,
                y=bivar_feature_y,
                color=bivar_feature_x,
                points="all",
                title=f"{bivar_feature_y} (Numeric) by {bivar_feature_x} (Categorical)",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
    st.plotly_chart(fig, use_container_width=True)


# ------------------------------
# 6️⃣ Multivariate Analysis
# ------------------------------
st.subheader("3️⃣ Multivariate Analysis")
multi_features = st.multiselect(
    "Select numeric features for correlation / scatter matrix",
    numeric_cols,
    default=numeric_cols[:4],
    key="multi_features"
)

if len(multi_features) >= 2:
    col1, col2 = st.columns(2)
    with col1:
        corr_matrix = df[multi_features].corr()
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale='Blues',
            title="Correlation Heatmap"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    with col2:
        fig_matrix = px.scatter_matrix(
            df,
            dimensions=multi_features,
            color='LoyaltyStatus',
            title="Scatter Matrix of Selected Features",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        st.plotly_chart(fig_matrix, use_container_width=True)
else:
    st.write("Select at least 2 numeric features for multivariate analysis")

