import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import math
from statsmodels.formula.api import ols
import statsmodels.api as sm

# ------------------------------
# Streamlit page setup
# ------------------------------
st.set_page_config(
    page_title="Customer Insights Dashboard",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Customer Insights Dashboard")
st.markdown("""
Interactive dashboard for exploring **CustomerDB** data.  
Analyze univariate, bivariate, and multivariate relationships with filters and interactive visuals.
""")

# ------------------------------
# Load Data
# ------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("CustomerDB_clean.csv")

    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    df['EnrollmentDateOpening'] = pd.to_datetime(df['EnrollmentDateOpening'], errors='coerce')
    df['CancellationDate'] = pd.to_datetime(df['CancellationDate'], errors='coerce')
    return df

df = load_data()

numeric_cols = df.select_dtypes(include='number').columns.tolist()
categorical_cols = df.select_dtypes(include='object').columns.tolist()

sns.set_style('whitegrid')
sns.set_palette('Set2')

# ------------------------------
# Overview
# ------------------------------
st.subheader("📄 Customer Data Table")
st.write(f"Showing {len(df)} rows after applied filters")
st.dataframe(df, use_container_width=True)

# ------------------------------
# KPIs
# ------------------------------
st.subheader("📊 Overview Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Customers", len(df))
col2.metric("Active Provinces/States", df["Province or State"].nunique())
col3.metric("Average Income", f"${df['Income'].mean():,.0f}")
col4.metric("Avg. Customer Lifetime Value", f"${df['Customer Lifetime Value'].mean():,.0f}")
col5.metric("Total Cancellations", df['CancellationDate'].notna().sum())

# ------------------------------
# Descriptive Statistics
# ------------------------------
st.subheader("📈 Descriptive Statistics")

# Mostrar resumo estatístico completo (todas as variáveis)
desc_all = df.describe(include='all').T

st.dataframe(
    desc_all.style.format(precision=2),
    use_container_width=True
)

# ------------------------------
# Univariate Analysis
# ------------------------------
st.subheader("1️⃣ Univariate Analysis")
uni_feature = st.selectbox("Select a variable", df.columns.tolist(), key="uni_feature")

if uni_feature in numeric_cols:
    col1, col2 = st.columns(2)
    with col1:
        fig_hist = px.histogram(
            df, x=uni_feature, nbins=30, opacity=0.8,
            color_discrete_sequence=['#1f77b4'],
            title=f"Histogram of {uni_feature}"
        )
        fig_hist.update_layout(bargap=0.2, template="plotly_white")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        fig_box = px.box(
            df, x=uni_feature, points="outliers",
            color_discrete_sequence=['#1f77b4'],
            title=f"Boxplot of {uni_feature} (with Outliers)"
        )
        fig_box.update_layout(template="plotly_white")
        st.plotly_chart(fig_box, use_container_width=True)
else:
    fig_cat = px.histogram(
        df, x=uni_feature, color_discrete_sequence=['#1f77b4'],
        title=f"Countplot of {uni_feature}"
    )
    fig_cat.update_layout(template="plotly_white")
    st.plotly_chart(fig_cat, use_container_width=True)

# ------------------------------
# Bivariate Analysis
# ------------------------------
st.subheader("2️⃣ Bivariate Analysis")
bivar_feature_x = st.selectbox("Select X feature", df.columns.tolist(), key="bivar_x")
bivar_feature_y = st.selectbox("Select Y feature", df.columns.tolist(), key="bivar_y")

is_x_numeric = bivar_feature_x in numeric_cols
is_y_numeric = bivar_feature_y in numeric_cols
is_x_cat = bivar_feature_x in categorical_cols
is_y_cat = bivar_feature_y in categorical_cols

# Numeric vs Numeric → Scatterplot
if is_x_numeric and is_y_numeric:
    fig = px.scatter(
        df,
        x=bivar_feature_x,
        y=bivar_feature_y,
        trendline="ols",
        opacity=0.7,
        title=f"{bivar_feature_x} vs {bivar_feature_y} (Scatterplot)",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig.update_layout(
        xaxis_title=bivar_feature_x,
        yaxis_title=bivar_feature_y,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# Categorical vs Categorical → Countplot Grid
elif is_x_cat and is_y_cat:
    st.write(f"### 📊 Countplot Grid for {bivar_feature_x} and {bivar_feature_y}")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes = axes.flatten()

    for i, (cat1, cat2) in enumerate([(bivar_feature_x, bivar_feature_y), (bivar_feature_y, bivar_feature_x)]):
        sns.countplot(data=df, x=cat1, hue=cat2, palette='Set2', ax=axes[i])
        axes[i].set_title(f"{cat1} vs {cat2}")
        axes[i].tick_params(axis='x', rotation=30)
        axes[i].legend(title=cat2, fontsize=8, title_fontsize=9)

    plt.tight_layout()
    st.pyplot(fig)

# Mixed (Numeric vs Categorical) → Violin Plot
else:
    num_cols = [col for col in [bivar_feature_x, bivar_feature_y] if col in numeric_cols]
    cat_cols = [col for col in [bivar_feature_x, bivar_feature_y] if col in categorical_cols]

    if len(num_cols) == 0 or len(cat_cols) == 0:
        st.warning("Please select one numeric and one categorical variable.")
    else:
        fig, ax = plt.subplots(figsize=(6, 3.5))
        sns.violinplot(
            data=df,
            x=num_cols[0],
            y=cat_cols[0],
            palette="muted",
            orient="h",
            inner="quartile",
            cut=0,
            linewidth=1.1,
            scale="width"
        )
        ax.set_title(f"{num_cols[0]} by {cat_cols[0]}", fontsize=12)
        st.pyplot(fig)

# ------------------------------
# Multivariate Analysis
# ------------------------------
st.subheader("3️⃣ Multivariate Analysis")
st.markdown("""
Select multiple features (numeric and/or categorical) to explore their multivariate relationships:
- **Numeric only →** Correlation Heatmap  
- **Categorical only →** Stacked Bar Chart  
- **Mixed →** MANOVA test
""")

multi_features = st.multiselect(
    "Select features for multivariate analysis",
    df.columns.tolist(),
    default=numeric_cols[:2] + categorical_cols[:1] if len(numeric_cols) >= 2 and len(categorical_cols) >= 1 else df.columns[:3]
)

if len(multi_features) < 2:
    st.info("Please select at least two features.")
else:
    selected_numeric = [col for col in multi_features if col in numeric_cols]
    selected_categorical = [col for col in multi_features if col in categorical_cols]

    # Numeric only → Correlation Heatmap
    if len(selected_numeric) >= 2 and len(selected_categorical) == 0:
        corr_matrix = df[selected_numeric].corr()
        fig_corr = px.imshow(
            corr_matrix, text_auto=True, color_continuous_scale='Blues',
            title="Correlation Heatmap (Numeric Features)"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # Categorical only → Stacked Bar Chart
    elif len(selected_categorical) >= 2 and len(selected_numeric) == 0:
        st.write("### Stacked Bar Chart (Categorical Features)")
        freq = df.value_counts(selected_categorical).reset_index(name='Count')
        fig = px.bar(
            freq,
            x=selected_categorical[0],
            y="Count",
            color=selected_categorical[1],
            barmode="stack",
            title=f"{selected_categorical[0]} vs {selected_categorical[1]}",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)

            # Mixed → ANOVA (com 2 numéricas + 1 categórica ou 2 categóricas + 1 numérica)
    elif len(selected_numeric) > 0 and len(selected_categorical) > 0:
        st.write("### 🔹 Multivariate ANOVA Analysis")

        df_sel = df[selected_numeric + selected_categorical].dropna()

        if len(selected_numeric) == 2 and len(selected_categorical) == 1:
            # Caso 1: duas numéricas + uma categórica
            num1, num2 = selected_numeric
            cat = selected_categorical[0]

            st.markdown(f"**Two numeric variables vs one categorical factor** — {num1}, {num2} by {cat}")

            # Gráfico: scatter plot colorido pela categoria
            fig = px.scatter(
                df_sel, x=num1, y=num2, color=cat,
                title=f"{num1} vs {num2} by {cat}",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)

            # MANOVA (multivariate ANOVA)
            from statsmodels.multivariate.manova import MANOVA
            safe_cat = cat.replace(" ", "_").replace("-", "_")
            df_sel = df_sel.rename(columns={cat: safe_cat})
            formula = f"{num1} + {num2} ~ C({safe_cat})"
            try:
                manova = MANOVA.from_formula(formula, data=df_sel)
                st.text("Multivariate ANOVA (Wilks' Lambda):")
                st.text(manova.mv_test().summary)
            except Exception as e:
                st.error(f"MANOVA failed: {e}")

        elif len(selected_numeric) == 1 and len(selected_categorical) == 2:
            # Caso 2: uma numérica + duas categóricas
            num = selected_numeric[0]
            cat1, cat2 = selected_categorical

            st.markdown(f"**Two categorical factors vs one numeric dependent variable** — {num} by {cat1} and {cat2}")

            # ANOVA de dois fatores com interação
            safe_cat1 = cat1.replace(" ", "_").replace("-", "_")
            safe_cat2 = cat2.replace(" ", "_").replace("-", "_")
            safe_num = num.replace(" ", "_").replace("-", "_")

            df_sel = df_sel.rename(columns={cat1: safe_cat1, cat2: safe_cat2, num: safe_num})

            try:
                model = ols(f"{safe_num} ~ C({safe_cat1}) * C({safe_cat2})", data=df_sel).fit()
                anova_table = sm.stats.anova_lm(model, typ=2)
                st.dataframe(anova_table.style.format(precision=4), use_container_width=True)

                # Gráfico: boxplot duplo
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.boxplot(data=df_sel, x=safe_cat1, y=safe_num, hue=safe_cat2, palette="Set2")
                ax.set_title(f"{num} by {cat1} and {cat2}")
                ax.set_xlabel(cat1)
                ax.set_ylabel(num)
                ax.legend(title=cat2, fontsize=9, title_fontsize=10, bbox_to_anchor=(1.02, 1), loc='upper left')
                plt.tight_layout()
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Two-way ANOVA failed: {e}")

        else:
            st.warning("For multivariate ANOVA, please select exactly:\n- 2 numeric + 1 categorical, or\n- 1 numeric + 2 categorical variables.")
