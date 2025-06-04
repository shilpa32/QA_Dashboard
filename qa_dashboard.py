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
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("📊 QA Metrics Dashboard")
st.markdown("### QA Report for R&D Team")

# Load data from qa_data_template.csv
try:
    df = pd.read_csv('qa_data_template.csv')
    
    # Convert list columns
    list_columns = ['Test Type', 'Bug Titles', 'Test Cases']
    for col in list_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Calculate total issues
df['Total Open Issues'] = df['P0 issues Open'] + df['P1 Issues Open'] + df['Rest Issues Open']
df['Total Closed Issues'] = df['P0 issues closed'] + df['P1 Issues Closed'] + df['Rest Issues Closed']
df['Total Issues'] = df['Total Open Issues'] + df['Total Closed Issues']

# Sidebar filters
st.sidebar.title("Filters")

# Test Type Filter
all_test_types = list(set([test for tests in df['Test Type'] for test in tests]))
selected_test_types = st.sidebar.multiselect(
    "Select Test Types",
    all_test_types,
    default=all_test_types
)

# Module Filter
selected_modules = st.sidebar.multiselect(
    "Select Modules",
    df['Module'].unique(),
    default=df['Module'].unique()
)

# Filter data based on selections
filtered_df = df[df['Module'].isin(selected_modules)]

# Create three columns for key metrics
col1, col2, col3 = st.columns(3)

with col1:
    total_open = filtered_df['Total Open Issues'].sum()
    st.metric("Total Open Issues", total_open)

with col2:
    total_closed = filtered_df['Total Closed Issues'].sum()
    st.metric("Total Closed Issues", total_closed)

with col3:
    resolution_rate = (total_closed / (total_open + total_closed)) * 100
    st.metric("Issue Resolution Rate", f"{resolution_rate:.1f}%")

# Create tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Priority Analysis", "Module Performance", "Test Types", "Bug Details"])

with tab1:
    # Overview tab content
    st.subheader("Module-wise Issue Distribution")
    
    # Create a stacked bar chart for open vs closed issues
    fig = px.bar(filtered_df, 
                 x='Module', 
                 y=['Total Open Issues', 'Total Closed Issues'],
                 title="Open vs Closed Issues by Module",
                 barmode='group',
                 color_discrete_sequence=['#ff9999', '#66b3ff'])
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Priority Analysis tab content
    st.subheader("Priority-wise Issue Distribution")
    
    # Create a stacked bar chart for priority levels
    priority_data = pd.melt(filtered_df, 
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
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Module Performance tab content
    st.subheader("Module Performance Metrics")
    
    # Create a heatmap for module performance
    performance_data = filtered_df[['Module', 'P0 issues Open', 'P0 issues closed', 
                          'P1 Issues Open', 'P1 Issues Closed']]
    
    fig = px.imshow(performance_data.set_index('Module'),
                    title="Module Performance Heatmap",
                    color_continuous_scale='RdYlGn_r')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    # Test Types Analysis
    st.subheader("Test Type Distribution")
    
    # Create a pie chart for test types
    test_type_counts = {}
    for test_types in filtered_df['Test Type']:
        for test_type in test_types:
            if test_type in selected_test_types:
                test_type_counts[test_type] = test_type_counts.get(test_type, 0) + 1
    
    if test_type_counts:
        fig = px.pie(values=list(test_type_counts.values()),
                     names=list(test_type_counts.keys()),
                     title="Distribution of Test Types")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No test types selected or available for the selected modules.")

with tab5:
    # Bug Details tab
    st.subheader("Bug Details by Module")
    
    # Create expandable sections for each module
    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['Module']} - {row['Total Open Issues']} Open, {row['Total Closed Issues']} Closed Issues"):
            # Display Test Types
            st.markdown("### Test Types")
            st.markdown(", ".join(row['Test Type']))
            
            # Create columns for bug counts with clickable metrics
            st.markdown("### Issue Distribution")
            col1, col2 = st.columns(2)
            
            # Store test cases in session state to persist between button clicks
            if 'test_cases' not in st.session_state:
                st.session_state.test_cases = {}
            
            # Define test case mappings for each module
            test_case_mappings = {
                'Inbox': {
                    'P0': ['TC_001', 'TC_002'],
                    'P1': ['TC_003', 'TC_004'],
                    'Other': ['TC_005', 'TC_006']
                },
                'Builder - NLP': {
                    'P0': ['TC_007', 'TC_008'],
                    'P1': ['TC_009'],
                    'Other': ['TC_010']
                },
                'Builder - gen ai': {
                    'P0': ['TC_011', 'TC_012'],
                    'P1': ['TC_013', 'TC_014'],
                    'Other': ['TC_015']
                },
                'Unifield KB': {
                    'P0': ['TC_016', 'TC_017'],
                    'P1': ['TC_018', 'TC_019'],
                    'Other': ['TC_020']
                },
                'Engage': {
                    'P0': ['TC_021'],
                    'P1': ['TC_022'],
                    'Other': ['TC_023']
                },
                'Integrations': {
                    'P0': ['TC_024', 'TC_025'],
                    'P1': ['TC_026'],
                    'Other': ['TC_027']
                },
                'Voice': {
                    'P0': ['TC_028', 'TC_029'],
                    'P1': ['TC_030', 'TC_031'],
                    'Other': ['TC_032']
                },
                'Channels': {
                    'P0': ['TC_033'],
                    'P1': ['TC_034'],
                    'Other': ['TC_035']
                },
                'Analyze': {
                    'P0': ['TC_036', 'TC_037'],
                    'P1': ['TC_038'],
                    'Other': ['TC_039']
                },
                'Analytics(DA+UDP+CDP)': {
                    'P0': ['TC_040', 'TC_041'],
                    'P1': ['TC_042', 'TC_043'],
                    'Other': ['TC_044', 'TC_045']
                }
            }
            
            with col1:
                if st.button(f"View Open Issues ({row['Total Open Issues']})", key=f"open_{row['Module']}"):
                    st.session_state.test_cases[f"open_{row['Module']}"] = True
                    st.session_state.test_cases[f"closed_{row['Module']}"] = False
            
            with col2:
                if st.button(f"View Closed Issues ({row['Total Closed Issues']})", key=f"closed_{row['Module']}"):
                    st.session_state.test_cases[f"closed_{row['Module']}"] = True
                    st.session_state.test_cases[f"open_{row['Module']}"] = False
            
            # Display Bug Details
            st.markdown("### Bug Details")
            
            # Create a table for bug details
            bug_data = []
            for bug_title in row['Bug Titles']:
                # Find associated test cases based on priority
                p0_tests = []
                p1_tests = []
                other_tests = []
                
                module_tests = test_case_mappings.get(row['Module'], {})
                
                for test_case in row['Test Cases']:
                    if any(tc in test_case for tc in module_tests.get('P0', [])):
                        p0_tests.append(test_case)
                    elif any(tc in test_case for tc in module_tests.get('P1', [])):
                        p1_tests.append(test_case)
                    elif any(tc in test_case for tc in module_tests.get('Other', [])):
                        other_tests.append(test_case)
                
                # Determine bug status based on keywords and associated test cases
                status = 'Open'
                if any(keyword in bug_title.lower() for keyword in ['resolved', 'fixed', 'completed', 'closed', 'done']):
                    status = 'Closed'
                elif any(keyword in bug_title.lower() for keyword in ['failure', 'error', 'delay', 'issues', 'open', 'pending']):
                    status = 'Open'
                
                # Determine priority based on test cases
                priority = 'Other'
                if p0_tests:
                    priority = 'P0'
                elif p1_tests:
                    priority = 'P1'
                
                bug_data.append({
                    'Bug Title': bug_title,
                    'Status': status,
                    'Priority': priority,
                    'P0 Test Cases': ', '.join(p0_tests) if p0_tests else 'None',
                    'P1 Test Cases': ', '.join(p1_tests) if p1_tests else 'None',
                    'Other Test Cases': ', '.join(other_tests) if other_tests else 'None'
                })
            
            if bug_data:
                bug_df = pd.DataFrame(bug_data)
                
                # Filter based on selected view
                if st.session_state.get(f"open_{row['Module']}", False):
                    bug_df = bug_df[bug_df['Status'] == 'Open']
                    st.markdown("#### Open Issues")
                elif st.session_state.get(f"closed_{row['Module']}", False):
                    bug_df = bug_df[bug_df['Status'] == 'Closed']
                    st.markdown("#### Closed Issues")
                
                if not bug_df.empty:
                    # Sort by Priority
                    bug_df = bug_df.sort_values('Priority', ascending=True)
                    st.dataframe(bug_df, use_container_width=True)
                    
                    # Add summary of issues
                    p0_count = len(bug_df[bug_df['Priority'] == 'P0'])
                    p1_count = len(bug_df[bug_df['Priority'] == 'P1'])
                    other_count = len(bug_df[bug_df['Priority'] == 'Other'])
                    st.markdown(f"**Summary:** P0: {p0_count}, P1: {p1_count}, Other: {other_count}")
                else:
                    st.info("No issues found for the selected status.")
            else:
                st.info("No bug details available for this module.")
            
            # Add a download button for module-specific data
            module_data = pd.DataFrame([{
                'Module': row['Module'],
                'Test Types': ', '.join(row['Test Type']),
                'P0 Open': row['P0 issues Open'],
                'P0 Closed': row['P0 issues closed'],
                'P1 Open': row['P1 Issues Open'],
                'P1 Closed': row['P1 Issues Closed'],
                'Other Open': row['Rest Issues Open'],
                'Other Closed': row['Rest Issues Closed'],
                'Bug Titles': ', '.join(row['Bug Titles']),
                'Test Cases': ', '.join(row['Test Cases'])
            }])
            
            st.download_button(
                label=f"Download {row['Module']} Details",
                data=module_data.to_csv(index=False).encode('utf-8'),
                file_name=f"{row['Module'].lower().replace(' ', '_')}_details.csv",
                mime='text/csv',
                key=f"download_{row['Module']}"
            )

# Add a summary section at the bottom
st.markdown("---")
st.subheader("Key Insights")

# Calculate and display key insights
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Top Modules by Open Issues**")
    top_open = filtered_df.nlargest(3, 'Total Open Issues')[['Module', 'Total Open Issues']]
    st.dataframe(top_open, hide_index=True)

with col2:
    st.markdown("**Top Modules by Resolution Rate**")
    filtered_df['Resolution Rate'] = (filtered_df['Total Closed Issues'] / filtered_df['Total Issues'] * 100)
    top_resolution = filtered_df.nlargest(3, 'Resolution Rate')[['Module', 'Resolution Rate']]
    st.dataframe(top_resolution, hide_index=True)

with col3:
    st.markdown("**Critical Issues (P0)**")
    critical_issues = filtered_df[['Module', 'P0 issues Open']].sort_values('P0 issues Open', ascending=False)
    st.dataframe(critical_issues, hide_index=True)

# Add download button for the raw data
st.markdown("---")
st.download_button(
    label="Download Raw Data",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='qa_metrics.csv',
    mime='text/csv'
) 