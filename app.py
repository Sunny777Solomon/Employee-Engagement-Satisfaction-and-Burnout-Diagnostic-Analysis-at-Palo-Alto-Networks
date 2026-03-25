import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Palo Alto Networks HR Dashboard", layout="wide")

st.title("🛡️ Palo Alto Networks - Employee Engagement & Burnout Diagnostic")
st.markdown("**Preventive HR Analytics | Early-Warning Signals for Burnout & Attrition**")

# ====================== LOAD DATA FROM GITHUB ======================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Sunny777Solomon/Employee-Engagement-Satisfaction-and-Burnout-Diagnostic-Analysis-at-Palo-Alto-Networks/main/Palo%20Alto%20Networks.csv"
    df = pd.read_csv(url)
    
    engagement_cols = ['JobInvolvement', 'JobSatisfaction', 'EnvironmentSatisfaction', 'RelationshipSatisfaction']
    df['EngagementIndex'] = df[engagement_cols].mean(axis=1)
    
    df['BurnoutHighRisk'] = ((df['OverTime'] == 'Yes') & (df['WorkLifeBalance'] <= 2)).astype(int)
    conditions = [
        (df['OverTime'] == 'Yes') & (df['WorkLifeBalance'] <= 2),
        (df['OverTime'] == 'Yes') | (df['WorkLifeBalance'] <= 2)
    ]
    df['BurnoutRiskLevel'] = pd.Series(np.select(conditions, ['High', 'Medium'], default='Low'))
    
    return df

df = load_data()

# ====================== SIDEBAR FILTERS ======================
st.sidebar.header("🔍 Filters")

department = st.sidebar.multiselect("Department", options=df['Department'].unique(), default=df['Department'].unique())
jobrole = st.sidebar.multiselect("Job Role", options=df['JobRole'].unique(), default=df['JobRole'].unique())
overtime = st.sidebar.radio("Overtime", ["All", "Yes", "No"])
engagement_threshold = st.sidebar.slider("Minimum Engagement Index", 1.0, 4.0, 2.0, 0.1)
tenure_range = st.sidebar.slider("Years at Company", 0, int(df['YearsAtCompany'].max()), (0, 40))

# Apply filters
filtered_df = df[
    (df['Department'].isin(department)) &
    (df['JobRole'].isin(jobrole)) &
    (df['YearsAtCompany'].between(tenure_range[0], tenure_range[1])) &
    (df['EngagementIndex'] >= engagement_threshold)
]

if overtime != "All":
    filtered_df = filtered_df[filtered_df['OverTime'] == overtime]

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Engagement Health Overview", 
    "🔥 Burnout Risk Dashboard", 
    "📈 Role & Career Stage Analysis", 
    "🚨 Manager Action Panel"
])

with tab1:
    st.header("Engagement Health Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Engagement Index", f"{filtered_df['EngagementIndex'].mean():.2f}")
    with col2:
        st.metric("Total Employees", len(filtered_df))
    with col3:
        st.metric("Attrition Rate (%)", f"{filtered_df['Attrition'].mean()*100:.1f}")
    
    col4, col5 = st.columns(2)
    with col4:
        fig = px.histogram(filtered_df, x='EngagementIndex', nbins=20, title="Satisfaction Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col5:
        st.image("https://raw.githubusercontent.com/Sunny777Solomon/Employee-Engagement-Satisfaction-and-Burnout-Diagnostic-Analysis-at-Palo-Alto-Networks/main/engagement_distribution.png", 
                 caption="Engagement Index Distribution")

with tab2:
    st.header("Burnout Risk Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(filtered_df['BurnoutRiskLevel'].value_counts().reset_index(), 
                     x='index', y='BurnoutRiskLevel', color='index', title="High-Risk Employee Segments")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.image("https://raw.githubusercontent.com/Sunny777Solomon/Employee-Engagement-Satisfaction-and-Burnout-Diagnostic-Analysis-at-Palo-Alto-Networks/main/burnout_risk.png", 
                 caption="Overtime & Work-Life Imbalance")
    
    st.subheader("High Risk Employees")
    high_risk = filtered_df[filtered_df['BurnoutRiskLevel'] == 'High']
    st.dataframe(high_risk[['JobRole', 'Department', 'EngagementIndex', 'Attrition']])

with tab3:
    st.header("Role & Career Stage Analysis")
    st.image("https://raw.githubusercontent.com/Sunny777Solomon/Employee-Engagement-Satisfaction-and-Burnout-Diagnostic-Analysis-at-Palo-Alto-Networks/main/step4_combined_workload_visuals.png", 
             caption="Engagement by Job Role and Level")
    st.image("https://raw.githubusercontent.com/Sunny777Solomon/Employee-Engagement-Satisfaction-and-Burnout-Diagnostic-Analysis-at-Palo-Alto-Networks/main/career_stagnation.png", 
             caption="Tenure vs Engagement Trends")

with tab4:
    st.header("🚨 Manager Action Panel")
    low_eng = filtered_df[filtered_df['EngagementIndex'] < 2.5]
    st.subheader(f"Low Engagement Alerts ({len(low_eng)} employees)")
    st.dataframe(low_eng[['JobRole', 'Department', 'EngagementIndex', 'BurnoutRiskLevel', 'OverTime']])
    
    st.warning("**Recommended Priority Interventions:**")
    st.markdown("""
    - Schedule 1:1 meetings with High Burnout Risk employees  
    - Review workload for frequent travelers and long-commute staff  
    - Career rotation for mid-level employees (6–15 years tenure)  
    """)

st.caption("Palo Alto Networks | Preventive Employee Experience Diagnostics")
