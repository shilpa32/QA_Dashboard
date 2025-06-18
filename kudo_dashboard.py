import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="QA Kudo Dashboard",
    page_icon="🏆",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .kudo-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .bug-metrics {
        background-color: #fff3f3;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🏆 QA Kudo Dashboard")
st.markdown("### Recognition and Feedback for QA Engineers")

# Load data
@st.cache_data
def load_data():
    kudo_df = pd.read_csv('kudo_data.csv')
    qa_df = pd.read_csv('qa_data_template.csv')
    return kudo_df, qa_df

try:
    kudo_df, qa_df = load_data()
    
    # Calculate bug metrics
    qa_df['Total Open Issues'] = qa_df['P0 issues Open'] + qa_df['P1 Issues Open'] + qa_df['Rest Issues Open']
    qa_df['Total Closed Issues'] = qa_df['P0 issues closed'] + qa_df['P1 Issues Closed'] + qa_df['Rest Issues Closed']
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Module filter
    selected_module = st.sidebar.multiselect(
        "Select Module",
        options=kudo_df['Module'].unique(),
        default=kudo_df['Module'].unique()
    )
    
    # EM filter
    selected_em = st.sidebar.multiselect(
        "Select Engineering Manager",
        options=kudo_df['EM_Name'].unique(),
        default=kudo_df['EM_Name'].unique()
    )
    
    # Filter data
    filtered_kudo_df = kudo_df[
        (kudo_df['Module'].isin(selected_module)) &
        (kudo_df['EM_Name'].isin(selected_em))
    ]
    
    filtered_qa_df = qa_df[qa_df['Module'].isin(selected_module)]
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Module-wise QA Scores")
        fig = px.box(filtered_kudo_df, x='Module', y='QA_Score', color='Module',
                    title='QA Score Distribution by Module')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("EM-wise QA Scores")
        fig = px.box(filtered_kudo_df, x='EM_Name', y='QA_Score', color='EM_Name',
                    title='QA Score Distribution by Engineering Manager')
        st.plotly_chart(fig, use_container_width=True)
    
    # Bug Metrics Section
    st.subheader("🐛 Bug Metrics by Module")
    
    # Create a new row for bug metrics
    bug_col1, bug_col2 = st.columns(2)
    
    with bug_col1:
        # Open Issues by Module
        fig = px.bar(filtered_qa_df, 
                    x='Module', 
                    y='Total Open Issues',
                    title='Open Issues by Module',
                    color='Total Open Issues',
                    color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    with bug_col2:
        # Closed Issues by Module
        fig = px.bar(filtered_qa_df, 
                    x='Module', 
                    y='Total Closed Issues',
                    title='Closed Issues by Module',
                    color='Total Closed Issues',
                    color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True)
    
    # Top Performers with Bug Metrics
    st.subheader("🏅 Top Performers")
    top_performers = filtered_kudo_df.nlargest(3, 'QA_Score')
    
    for _, row in top_performers.iterrows():
        module_bugs = filtered_qa_df[filtered_qa_df['Module'] == row['Module']]
        open_issues = module_bugs['Total Open Issues'].sum() if not module_bugs.empty else 0
        closed_issues = module_bugs['Total Closed Issues'].sum() if not module_bugs.empty else 0
        
        st.markdown(f"""
        <div class="kudo-card">
            <h3>{row['QA_Name']} - {row['Module']}</h3>
            <p><strong>Score:</strong> {row['QA_Score']}/100</p>
            <p><strong>Feedback:</strong> {row['QA_Feedback']}</p>
            <p><strong>EM:</strong> {row['EM_Name']}</p>
            <div class="bug-metrics">
                <p><strong>Bug Metrics:</strong></p>
                <p>Open Issues: {open_issues}</p>
                <p>Closed Issues: {closed_issues}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed Feedback Table with Bug Metrics
    st.subheader("📊 Detailed Feedback")
    
    # Merge kudo and QA data
    detailed_df = pd.merge(
        filtered_kudo_df,
        filtered_qa_df[['Module', 'Total Open Issues', 'Total Closed Issues']],
        on='Module',
        how='left'
    )
    
    st.dataframe(
        detailed_df[['Module', 'EM_Name', 'QA_Name', 'QA_Score', 'QA_Feedback', 
                    'Total Open Issues', 'Total Closed Issues', 'Date']],
        use_container_width=True
    )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please make sure both kudo_data.csv and qa_data_template.csv files exist in the same directory.") 