import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set page config
st.set_page_config(
    page_title="QA Metrics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for active tab
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Recognition"

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
    }
    .stMetric:hover {
        background-color: #e6e9ef;
    }
    .bug-title {
        font-size: 0.9em;
        color: #666;
    }
    .test-case {
        padding: 0.5rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        border-radius: 0.3rem;
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
    .recognition-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #1f77b4 0%, #2c3e50 100%);
        color: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .recognition-header h2 {
        font-size: 2.5em;
        margin: 0;
        padding: 1rem;
    }
    .award-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem auto;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid #e0e0e0;
        width: 100%;
        height: 100%;
        min-height: 500px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease-in-out;
    }
    .award-card:hover {
        transform: translateY(-5px);
    }
    .award-card h2 {
        color: #1f77b4;
        font-size: 1.4em;
        margin-bottom: 1.5rem;
        text-align: center;
        border-bottom: 2px solid #f0f2f6;
        padding-bottom: 1rem;
    }
    .award-card h1 {
        color: #2c3e50;
        font-size: 1.8em;
        margin: 1rem 0;
        text-align: center;
    }
    .award-card p {
        font-size: 1.1em;
        margin: 1rem 0;
        text-align: center;
        line-height: 1.5;
    }
    .award-card .quote {
        font-style: italic;
        color: #666;
        font-size: 1em;
        margin: 1.5rem 0;
        padding: 1rem 1.5rem;
        border-left: 3px solid #1f77b4;
        background-color: #f8f9fa;
        border-radius: 0 8px 8px 0;
    }
    .award-card .emoji {
        font-size: 1.8em;
        margin: 1rem 0;
        text-align: center;
    }
    .award-content {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        padding: 1rem;
    }
    .award-metrics {
        margin: 1.5rem 0;
    }
    .award-metrics p {
        margin: 0.8rem 0;
        font-size: 1.1em;
    }
    .spacer {
        height: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("📊 QA Metrics Dashboard")
st.markdown("### QA Report for R&D Team")

# Load data
@st.cache_data
def load_data():
    qa_df = pd.read_csv('qa_data_template.csv')
    kudo_df = pd.read_csv('kudo_data.csv')
    return qa_df, kudo_df

try:
    qa_df, kudo_df = load_data()
    
    # Convert list columns
    list_columns = ['Test Type', 'Bug Titles', 'Test Cases']
    for col in list_columns:
        if col in qa_df.columns:
            qa_df[col] = qa_df[col].apply(lambda x: x.split(',') if isinstance(x, str) else [])

    # Calculate total issues
    qa_df['Total Open Issues'] = qa_df['P0 issues Open'] + qa_df['P1 Issues Open'] + qa_df['Rest Issues Open']
    qa_df['Total Closed Issues'] = qa_df['P0 issues closed'] + qa_df['P1 Issues Closed'] + qa_df['Rest Issues Closed']
    qa_df['Total Issues'] = qa_df['Total Open Issues'] + qa_df['Total Closed Issues']

    # Create a copy of the original dataframes for reset functionality
    original_qa_df = qa_df.copy()
    original_kudo_df = kudo_df.copy()
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Sidebar filters
st.sidebar.title("Filters")

# Test Type Filter
all_test_types = list(set([test for tests in qa_df['Test Type'] for test in tests]))
selected_test_types = st.sidebar.multiselect(
    "Select Test Types",
    all_test_types,
    default=all_test_types,
    key="test_types_filter"
)

# Module Filter
selected_modules = st.sidebar.multiselect(
    "Select Modules",
    qa_df['Module'].unique(),
    default=qa_df['Module'].unique()
)
    
# EM Filter
selected_ems = st.sidebar.multiselect(
    "Select Engineering Managers",
    kudo_df['EM_Name'].unique(),
    default=kudo_df['EM_Name'].unique(),
    key="em_filter"
)

# Filter data based on selections
filtered_qa_df = qa_df[qa_df['Module'].isin(selected_modules)]
filtered_kudo_df = kudo_df[
    (kudo_df['Module'].isin(selected_modules)) &
    (kudo_df['EM_Name'].isin(selected_ems))
]

# Create three columns for key metrics
col1, col2, col3 = st.columns(3)

with col1:
    total_open = filtered_qa_df['Total Open Issues'].sum()
    st.metric("Total Open Issues", total_open)

with col2:
    total_closed = filtered_qa_df['Total Closed Issues'].sum()
    st.metric("Total Closed Issues", total_closed)

with col3:
    resolution_rate = (total_closed / (total_open + total_closed)) * 100 if (total_open + total_closed) > 0 else 0
    st.metric("Issue Resolution Rate", f"{resolution_rate:.1f}%")

# Determine which tab to show based on filter changes
if 'previous_test_types' not in st.session_state:
    st.session_state.previous_test_types = selected_test_types
if 'previous_ems' not in st.session_state:
    st.session_state.previous_ems = selected_ems

# Check if filters have changed
test_types_changed = set(st.session_state.previous_test_types) != set(selected_test_types)
ems_changed = set(st.session_state.previous_ems) != set(selected_ems)

# Update previous values
st.session_state.previous_test_types = selected_test_types
st.session_state.previous_ems = selected_ems

# Create tabs for different views
tab_names = ["Recognition", "Overview", "Priority Analysis", "Module Performance", "Test Types", "Bug Details"]
tabs = st.tabs(tab_names)

# Determine which tab to show
if test_types_changed:
    st.session_state.active_tab = "Test Types"
elif ems_changed:
    st.session_state.active_tab = "Recognition"

# Get the index of the active tab
active_tab_index = tab_names.index(st.session_state.active_tab)

# Create the tabs with the active one selected
for i, tab in enumerate(tabs):
    with tab:
        if tab_names[i] == "Recognition":
            # Recognition tab
            st.markdown("""
                <div class="recognition-header">
                    <h2>🏆 Recognition and Performance</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # Calculate EM Performance
            em_performance = filtered_kudo_df.groupby('EM_Name').agg({
                'QA_Score': 'mean',
                'Module': lambda x: list(set(x))  # Get unique modules per EM
            }).reset_index()
            
            # Calculate bug metrics per EM by aggregating their modules' bugs
            em_bug_metrics = []
            for _, row in em_performance.iterrows():
                em_modules = row['Module']
                # Sum up all bugs from all modules managed by this EM
                em_bugs = filtered_qa_df[filtered_qa_df['Module'].isin(em_modules)].agg({
                    'P0 issues Open': 'sum',
                    'P0 issues closed': 'sum',
                    'P1 Issues Open': 'sum',
                    'P1 Issues Closed': 'sum',
                    'Rest Issues Open': 'sum',
                    'Rest Issues Closed': 'sum'
                })
                
                # Get all QAs under this EM
                em_qas = filtered_kudo_df[filtered_kudo_df['EM_Name'] == row['EM_Name']]['QA_Name'].unique()
                
                # Calculate total bugs for all QAs under this EM
                total_open = (em_bugs['P0 issues Open'] + em_bugs['P1 Issues Open'] + em_bugs['Rest Issues Open']) * len(em_qas)
                total_closed = (em_bugs['P0 issues closed'] + em_bugs['P1 Issues Closed'] + em_bugs['Rest Issues Closed']) * len(em_qas)
                
                em_bug_metrics.append({
                    'EM_Name': row['EM_Name'],
                    'Total Open Issues': total_open,
                    'Total Closed Issues': total_closed,
                    'QA_Count': len(em_qas)
                })
            
            em_bug_metrics_df = pd.DataFrame(em_bug_metrics)
            
            # Merge EM performance with bug metrics
            em_performance = pd.merge(
                em_performance,
                em_bug_metrics_df,
                on='EM_Name',
                how='left'
            )
            
            # Calculate bug efficiency score (higher closed issues and lower open issues is better)
            em_performance['Bug Efficiency'] = (
                em_performance['Total Closed Issues'] / 
                (em_performance['Total Open Issues'] + em_performance['Total Closed Issues'])
            ).fillna(0) * 100
            
            # Sort by bug efficiency and QA score
            em_performance = em_performance.sort_values(['Bug Efficiency', 'QA_Score'], ascending=[False, False])
            
            # Get top EM
            top_em = em_performance.iloc[0]
            
            # Calculate QA Performance
            qa_performance = filtered_kudo_df.copy()
            
            # Get bug metrics for each QA based on their EM's modules
            qa_bug_metrics = []
            for _, row in qa_performance.iterrows():
                # Get all modules managed by this QA's EM
                em_modules = em_performance[em_performance['EM_Name'] == row['EM_Name']]['Module'].iloc[0]
                
                # Sum up all bugs from all modules managed by this EM
                em_bugs = filtered_qa_df[filtered_qa_df['Module'].isin(em_modules)].agg({
                    'P0 issues Open': 'sum',
                    'P0 issues closed': 'sum',
                    'P1 Issues Open': 'sum',
                    'P1 Issues Closed': 'sum',
                    'Rest Issues Open': 'sum',
                    'Rest Issues Closed': 'sum'
                })
                
                # Calculate P0 metrics
                p0_open = em_bugs['P0 issues Open']
                p0_closed = em_bugs['P0 issues closed']
                
                # Calculate total metrics
                total_open = (em_bugs['P0 issues Open'] + em_bugs['P1 Issues Open'] + em_bugs['Rest Issues Open'])
                total_closed = (em_bugs['P0 issues closed'] + em_bugs['P1 Issues Closed'] + em_bugs['Rest Issues Closed'])
                
                qa_bug_metrics.append({
                    'QA_Name': row['QA_Name'],
                    'Module': row['Module'],
                    'EM_Name': row['EM_Name'],
                    'P0 Open Issues': p0_open,
                    'P0 Closed Issues': p0_closed,
                    'Total Open Issues': total_open,
                    'Total Closed Issues': total_closed
                })
            
            qa_bug_metrics_df = pd.DataFrame(qa_bug_metrics)
            
            # Merge QA performance with bug metrics
            qa_performance = pd.merge(
                qa_performance,
                qa_bug_metrics_df,
                on=['QA_Name', 'Module', 'EM_Name'],
                how='left'
            )
            
            # Calculate individual QA P0 bug efficiency
            qa_performance.loc[:, 'P0 Bug Efficiency'] = (
                qa_performance['P0 Closed Issues'] / 
                (qa_performance['P0 Open Issues'] + qa_performance['P0 Closed Issues'])
            ).fillna(0) * 100
            
            # Calculate total bug efficiency
            qa_performance.loc[:, 'Total Bug Efficiency'] = (
                qa_performance['Total Closed Issues'] / 
                (qa_performance['Total Open Issues'] + qa_performance['Total Closed Issues'])
            ).fillna(0) * 100
            
            # Sort by QA score and P0 bug efficiency
            qa_performance = qa_performance.sort_values(['QA_Score', 'P0 Bug Efficiency'], ascending=[False, False])
            
            # Get top QA
            top_qa = qa_performance.iloc[0]
            
            # Display awards side by side
            award_col1, award_col2 = st.columns(2)
            
            with award_col1:
                st.markdown("""
                <div class="award-card">
                    <h2>🏆 Best QA Engineer Award</h2>
                    <div class="award-content">
                        <div>
                            <h2 style='color: #1f77b4; font-size: 1.3em; margin: 1rem 0;'>🎉 Congratulations! 🎉</h2>
                            <h1 style='color: #2c3e50; margin: 1rem 0;'>{}</h1>
                            <div class="award-metrics">
                                <p>P0 Issues Raised: {}</p>
                                <p>Total Bugs Raised: {}</p>
                                <p>Total Bugs Resolved: {}</p>
                            </div>
                        </div>
                        <div>
                            <p class="quote">"Quality is not an act, it is a habit. Keep up the excellent work!"</p>
                            <div class="emoji">👏 🎊 🎈</div>
                        </div>
                    </div>
                </div>
                """.format(
                    top_qa['QA_Name'],
                    top_qa['P0 Open Issues'] + top_qa['P0 Closed Issues'],
                    top_qa['Total Open Issues'] + top_qa['Total Closed Issues'],
                    top_qa['Total Closed Issues']
                ), unsafe_allow_html=True)
            
            with award_col2:
                st.markdown("""
                <div class="award-card">
                    <h2>🏅 Best Engineering Manager Award</h2>
                    <div class="award-content">
                        <div>
                            <h2 style='color: #1f77b4; font-size: 1.3em; margin: 1rem 0;'>🎉 Congratulations! 🎉</h2>
                            <h1 style='color: #2c3e50; margin: 1rem 0;'>{}</h1>
                            <div class="award-metrics">
                                <p>Total Open Issues: {}</p>
                                <p>Total Closed Issues: {}</p>
                                <p>Resolution Rate: {:.1f}%</p>
                            </div>
                        </div>
                        <div>
                            <p class="quote">"Leadership is about making others better as a result of your presence."</p>
                            <div class="emoji">👏 🎊 🎈</div>
                        </div>
                    </div>
                </div>
                """.format(
                    top_em['EM_Name'],
                    top_em['Total Open Issues'],
                    top_em['Total Closed Issues'],
                    top_em['Bug Efficiency']
                ), unsafe_allow_html=True)
            
            # Add expandable bug list section
            with st.expander("📋 View All QA Bug Lists", expanded=False):
                st.markdown("### 🐛 Bug List by Priority")
                
                # Create tabs for different priority levels
                p0_tab, p1_tab, rest_tab = st.tabs(["P0 Issues", "P1 Issues", "Other Issues"])
                
                # Get all QAs and their assigned modules
                qa_module_map = filtered_kudo_df.groupby('QA_Name')['Module'].apply(list).to_dict()
                
                # P0 Issues Tab
                with p0_tab:
                    st.markdown("#### Critical Issues (P0)")
                    p0_issues = []
                    
                    # Process each QA's assigned modules
                    for qa_name, assigned_modules in qa_module_map.items():
                        # Get bugs for this QA's modules
                        qa_bugs = filtered_qa_df[filtered_qa_df['Module'].isin(assigned_modules)]
                        
                        for _, row in qa_bugs.iterrows():
                            if isinstance(row['Bug Titles'], list):
                                # Get P0 issues for this module
                                p0_open_count = row['P0 issues Open']
                                p0_closed_count = row['P0 issues closed']
                                
                                # Add open P0 issues
                                for i in range(p0_open_count):
                                    if i < len(row['Bug Titles']):
                                        p0_issues.append({
                                            'Module': row['Module'],
                                            'Bug Title': row['Bug Titles'][i],
                                            'QA Name': qa_name,
                                            'Status': 'Open'
                                        })
                                
                                # Add closed P0 issues
                                for i in range(p0_closed_count):
                                    if (p0_open_count + i) < len(row['Bug Titles']):
                                        p0_issues.append({
                                            'Module': row['Module'],
                                            'Bug Title': row['Bug Titles'][p0_open_count + i],
                                            'QA Name': qa_name,
                                            'Status': 'Closed'
                                        })
                    
                    if p0_issues:
                        p0_df = pd.DataFrame(p0_issues)
                        # Group by module
                        for module in sorted(p0_df['Module'].unique()):
                            module_bugs = p0_df[p0_df['Module'] == module]
                            st.markdown(f"#### 📁 {module} - {len(module_bugs)} P0 Issues")
                            st.dataframe(
                                module_bugs,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Module": st.column_config.TextColumn("Module", width="medium"),
                                    "Bug Title": st.column_config.TextColumn("Bug Title", width="large"),
                                    "QA Name": st.column_config.TextColumn("QA Name", width="medium"),
                                    "Status": st.column_config.TextColumn("Status", width="small")
                                }
                            )
                            
                            # Display metrics
                            col1, col2 = st.columns(2)
                            with col1:
                                open_issues = len(module_bugs[module_bugs['Status'] == 'Open'])
                                st.metric("Open P0 Issues", open_issues)
                            with col2:
                                closed_issues = len(module_bugs[module_bugs['Status'] == 'Closed'])
                                st.metric("Closed P0 Issues", closed_issues)
                            st.markdown("---")
                    else:
                        st.info("No P0 issues found.")
                
                # P1 Issues Tab
                with p1_tab:
                    st.markdown("#### High Priority Issues (P1)")
                    p1_issues = []
                    
                    # Process each QA's assigned modules
                    for qa_name, assigned_modules in qa_module_map.items():
                        # Get bugs for this QA's modules
                        qa_bugs = filtered_qa_df[filtered_qa_df['Module'].isin(assigned_modules)]
                        
                        for _, row in qa_bugs.iterrows():
                            if isinstance(row['Bug Titles'], list):
                                # Get P1 issues for this module
                                p1_open_count = row['P1 Issues Open']
                                p1_closed_count = row['P1 Issues Closed']
                                
                                # Add open P1 issues
                                for i in range(p1_open_count):
                                    if i < len(row['Bug Titles']):
                                        p1_issues.append({
                                            'Module': row['Module'],
                                            'Bug Title': row['Bug Titles'][i],
                                            'QA Name': qa_name,
                                            'Status': 'Open'
                                        })
                                
                                # Add closed P1 issues
                                for i in range(p1_closed_count):
                                    if (p1_open_count + i) < len(row['Bug Titles']):
                                        p1_issues.append({
                                            'Module': row['Module'],
                                            'Bug Title': row['Bug Titles'][p1_open_count + i],
                                            'QA Name': qa_name,
                                            'Status': 'Closed'
                                        })
                    
                    if p1_issues:
                        p1_df = pd.DataFrame(p1_issues)
                        # Group by module
                        for module in sorted(p1_df['Module'].unique()):
                            module_bugs = p1_df[p1_df['Module'] == module]
                            st.markdown(f"#### 📁 {module} - {len(module_bugs)} P1 Issues")
                            st.dataframe(
                                module_bugs,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Module": st.column_config.TextColumn("Module", width="medium"),
                                    "Bug Title": st.column_config.TextColumn("Bug Title", width="large"),
                                    "QA Name": st.column_config.TextColumn("QA Name", width="medium"),
                                    "Status": st.column_config.TextColumn("Status", width="small")
                                }
                            )
                            
                            # Display metrics
                            col1, col2 = st.columns(2)
                            with col1:
                                open_issues = len(module_bugs[module_bugs['Status'] == 'Open'])
                                st.metric("Open P1 Issues", open_issues)
                            with col2:
                                closed_issues = len(module_bugs[module_bugs['Status'] == 'Closed'])
                                st.metric("Closed P1 Issues", closed_issues)
                            st.markdown("---")
                    else:
                        st.info("No P1 issues found.")
                
                # Other Issues Tab
                with rest_tab:
                    st.markdown("#### Other Issues")
                    rest_issues = []
                    
                    # Process each QA's assigned modules
                    for qa_name, assigned_modules in qa_module_map.items():
                        # Get bugs for this QA's modules
                        qa_bugs = filtered_qa_df[filtered_qa_df['Module'].isin(assigned_modules)]
                        
                        for _, row in qa_bugs.iterrows():
                            if isinstance(row['Bug Titles'], list):
                                # Get other issues for this module
                                rest_open_count = row['Rest Issues Open']
                                rest_closed_count = row['Rest Issues Closed']
                                
                                # Add open other issues
                                for i in range(rest_open_count):
                                    if i < len(row['Bug Titles']):
                                        rest_issues.append({
                                            'Module': row['Module'],
                                            'Bug Title': row['Bug Titles'][i],
                                            'QA Name': qa_name,
                                            'Status': 'Open'
                                        })
                                
                                # Add closed other issues
                                for i in range(rest_closed_count):
                                    if (rest_open_count + i) < len(row['Bug Titles']):
                                        rest_issues.append({
                                            'Module': row['Module'],
                                            'Bug Title': row['Bug Titles'][rest_open_count + i],
                                            'QA Name': qa_name,
                                            'Status': 'Closed'
                                        })
                    
                    if rest_issues:
                        rest_df = pd.DataFrame(rest_issues)
                        # Group by module
                        for module in sorted(rest_df['Module'].unique()):
                            module_bugs = rest_df[rest_df['Module'] == module]
                            st.markdown(f"#### 📁 {module} - {len(module_bugs)} Other Issues")
                            st.dataframe(
                                module_bugs,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Module": st.column_config.TextColumn("Module", width="medium"),
                                    "Bug Title": st.column_config.TextColumn("Bug Title", width="large"),
                                    "QA Name": st.column_config.TextColumn("QA Name", width="medium"),
                                    "Status": st.column_config.TextColumn("Status", width="small")
                                }
                            )
                            
                            # Display metrics
                            col1, col2 = st.columns(2)
                            with col1:
                                open_issues = len(module_bugs[module_bugs['Status'] == 'Open'])
                                st.metric("Open Issues", open_issues)
                            with col2:
                                closed_issues = len(module_bugs[module_bugs['Status'] == 'Closed'])
                                st.metric("Closed Issues", closed_issues)
                            st.markdown("---")
                    else:
                        st.info("No other issues found.")

            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
            
            # Display Top EMs
            st.markdown("### 🏅 Top Engineering Managers")
            st.markdown("Based on Bug Efficiency and Team Performance")
            
            # Format the EM performance table
            em_display = em_performance[['EM_Name', 'Bug Efficiency', 'QA_Score', 'Total Closed Issues', 'Total Open Issues', 'QA_Count']].copy()
            em_display.columns = ['Engineering Manager', 'Bug Efficiency (%)', 'Average QA Score', 'Closed Issues', 'Open Issues', 'QA Team Size']
            em_display.loc[:, 'Bug Efficiency (%)'] = em_display['Bug Efficiency (%)'].round(1)
            em_display.loc[:, 'Average QA Score'] = em_display['Average QA Score'].round(1)
            
            st.dataframe(
                em_display,
                use_container_width=True,
                hide_index=True
            )
            
            # Display Top QAs
            st.markdown("### 🏆 Top QA Engineers")
            st.markdown("Based on Performance Score and P0 Issue Resolution")
            
            # Format the QA performance table
            qa_display = qa_performance[['QA_Name', 'Module', 'EM_Name', 'QA_Score', 'P0 Bug Efficiency', 'P0 Closed Issues', 'P0 Open Issues', 'Total Closed Issues', 'Total Open Issues']].copy()
            qa_display.columns = ['QA Engineer', 'Module', 'Engineering Manager', 'Performance Score', 'P0 Bug Efficiency (%)', 'P0 Closed Issues', 'P0 Open Issues', 'Total Closed Issues', 'Total Open Issues']
            qa_display.loc[:, 'P0 Bug Efficiency (%)'] = qa_display['P0 Bug Efficiency (%)'].round(1)
            qa_display.loc[:, 'Performance Score'] = qa_display['Performance Score'].round(1)
            
            st.dataframe(
                qa_display,
                use_container_width=True,
                hide_index=True
            )

            # --- QA & EM Scoring Section ---
            try:
                qa_scores = pd.read_csv('qa_scores.csv')
                em_scores = pd.read_csv('em_scores.csv')

                qa_totals = qa_scores.groupby('QA_Name')['Points'].sum().reset_index()
                qa_totals = qa_totals.sort_values(by='Points', ascending=False)

                em_totals = em_scores.groupby('EM_Name')['Points'].sum().reset_index()
                em_totals = em_totals.sort_values(by='Points', ascending=False)

                st.markdown("### 🏆 Best QA Engineer (Scoring System)")
                if not qa_totals.empty:
                    st.write(f"**{qa_totals.iloc[0]['QA_Name']}** with {qa_totals.iloc[0]['Points']} points")
                    st.dataframe(qa_totals, hide_index=True)
                else:
                    st.write("No QA scores available.")

                st.markdown("### 🏅 Best Engineering Manager (Scoring System)")
                if not em_totals.empty:
                    st.write(f"**{em_totals.iloc[0]['EM_Name']}** with {em_totals.iloc[0]['Points']} points")
                    st.dataframe(em_totals, hide_index=True)
                else:
                    st.write("No EM scores available.")
            except Exception as e:
                st.warning(f"Could not load QA/EM scores: {e}")
        elif tab_names[i] == "Overview":
            # Overview tab content
            st.subheader("Module-wise Issue Distribution")
            # Create a stacked bar chart for open vs closed issues
            fig = px.bar(filtered_qa_df, 
                 x='Module', 
                 y=['Total Open Issues', 'Total Closed Issues'],
                 title="Open vs Closed Issues by Module",
                 barmode='group',
                 color_discrete_sequence=['#ff9999', '#66b3ff'])
            fig.update_layout(
                height=500,
                xaxis_title="Module",
                yaxis_title="Number of Issues",
                legend_title="Issue Status",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        elif tab_names[i] == "Priority Analysis":
            # Priority Analysis tab content
            st.subheader("Priority-wise Issue Distribution")
            # Create a stacked bar chart for priority levels
            priority_data = pd.melt(filtered_qa_df, 
                           id_vars=['Module'],
                           value_vars=['P0 issues Open', 'P1 Issues Open', 'Rest Issues Open'],
                           var_name='Priority',
                           value_name='Count')
            fig = px.bar(priority_data,
                 x='Module',
                 y='Count',
                 color='Priority',
                 title="Open Issues by Priority Level",
                 color_discrete_sequence=['#ff9999', '#66b3ff', '#99ff99'])
            fig.update_layout(
                height=500,
                xaxis_title="Module",
                yaxis_title="Number of Issues",
                legend_title="Priority Level",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        elif tab_names[i] == "Module Performance":
            # Module Performance tab content
            st.subheader("Module Performance Metrics")
            # Create a heatmap for module performance
            performance_data = filtered_qa_df[['Module', 'P0 issues Open', 'P0 issues closed', 
                          'P1 Issues Open', 'P1 Issues Closed']]
            fig = px.imshow(performance_data.set_index('Module'),
                        title="Module Performance Heatmap",
                        color_continuous_scale='RdYlGn_r')
            fig.update_layout(
                height=500,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        elif tab_names[i] == "Test Types":
            st.subheader("Test Type Distribution")
            test_type_counts = {}
            for test_types in filtered_qa_df['Test Type']:
                for test_type in test_types:
                    if test_type in selected_test_types:
                        test_type_counts[test_type] = test_type_counts.get(test_type, 0) + 1
            if test_type_counts:
                fig = px.pie(values=list(test_type_counts.values()),
                             names=list(test_type_counts.keys()),
                             title="Distribution of Test Types")
                fig.update_layout(height=500, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No test types selected or available for the selected modules.")
        elif tab_names[i] == "Bug Details":
            # Bug Details tab
            st.subheader("Bug Details by Module")
            # Create expandable sections for each module
            for _, row in filtered_qa_df.iterrows():
                with st.expander(f"{row['Module']} - {row['Total Open Issues']} Open, {row['Total Closed Issues']} Closed Issues"):
                    # Display Test Types
                    st.markdown("### Test Types")
                    st.markdown(", ".join(row['Test Type']))
                    # Create columns for bug counts with clickable metrics
                    st.markdown("### Issue Distribution")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Open Issues", row['Total Open Issues'])
                    with col2:
                        st.metric("Closed Issues", row['Total Closed Issues'])

# Add a summary section at the bottom
st.markdown("---")
st.subheader("Key Insights")

# Calculate and display key insights
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Top Modules by Open Issues**")
    top_open = filtered_qa_df.nlargest(3, 'Total Open Issues')[['Module', 'Total Open Issues']]
    st.dataframe(top_open, hide_index=True)

with col2:
    st.markdown("**Top Modules by Resolution Rate**")
    filtered_qa_df['Resolution Rate'] = (filtered_qa_df['Total Closed Issues'] / filtered_qa_df['Total Issues'] * 100)
    top_resolution = filtered_qa_df.nlargest(3, 'Resolution Rate')[['Module', 'Resolution Rate']]
    st.dataframe(top_resolution, hide_index=True)

with col3:
    st.markdown("**Critical Issues (P0)**")
    critical_issues = filtered_qa_df[['Module', 'P0 issues Open']].sort_values('P0 issues Open', ascending=False)
    st.dataframe(critical_issues, hide_index=True)

# Add download button for the raw data
st.markdown("---")
st.download_button(
    label="Download Raw Data",
    data=filtered_qa_df.to_csv(index=False).encode('utf-8'),
    file_name='qa_metrics.csv',
    mime='text/csv'
) 