import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="University Application Tracker",
    page_icon="🎓",
    layout="wide"
)

# Function to save progress
def save_progress():
    progress_data = {
        'requirements_checked': st.session_state.requirements_checked,
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        # Create a progress folder if it doesn't exist
        if not os.path.exists('progress'):
            os.makedirs('progress')
            
        # Save the progress data
        with open('progress/application_progress.json', 'w') as f:
            json.dump(progress_data, f)
        st.success('Progress saved successfully! ✅')
    except Exception as e:
        st.error(f'Error saving progress: {str(e)}')

# Initialize session state and load saved progress if available
if 'requirements_checked' not in st.session_state:
    # Default initial state
    st.session_state.requirements_checked = {
        'GRE': False,
        'TOEFL': False,
        'Transcripts': False,
        'SOP': False,
        'Resume': False,
        'LORs': False,
        'University_Specific': {}  # For university-specific requirements
    }
    
    # Try to load saved progress
    try:
        if os.path.exists('progress/application_progress.json'):
            with open('progress/application_progress.json', 'r') as f:
                progress_data = json.load(f)
                st.session_state.requirements_checked = progress_data['requirements_checked']
                st.success(f'Progress loaded! Last saved: {progress_data["last_updated"]} ✅')
    except Exception as e:
        st.error(f'Error loading saved progress: {str(e)}')

def load_university_data():
    try:
        # Read the CSV file
        df = pd.read_csv('data.csv')
        
        # Ensure proper formatting of monetary values
        money_columns = ['Application_Fee', 'Tuition_Per_Year', 'Living_Costs_Yearly', 
                        'Total_Cost_2Years', 'Avg_Starting_Salary', 'ROI_5Year']
        for col in money_columns:
            df[col] = df[col].str.replace('$', '').str.replace(',', '')\
                            .astype(float).apply(lambda x: f"${x:,.0f}")
        
        # Ensure percentage formatting
        percentage_columns = ['Acceptance_Rate', 'Placement_Rate']
        for col in percentage_columns:
            df[col] = df[col].str.rstrip('%') + '%'
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame if there's an error


# Title and introduction
st.title('🎓 University Application Tracker')
st.write('Track your graduate school applications and requirements')

# Load data
df = load_university_data()

# Sidebar filters
st.sidebar.header('Filters')

# Category filter
selected_categories = st.sidebar.multiselect(
    'Select Application Category',
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Program filter
selected_programs = st.sidebar.multiselect(
    'Select Programs',
    options=df['Program'].unique(),
    default=df['Program'].unique()
)

# Filter the dataframe
filtered_df = df[
    df['Category'].isin(selected_categories) &
    df['Program'].isin(selected_programs)
]

# Progress Tracking Section
st.header('Application Progress')
col1, col2 = st.columns([2, 1])

with col1:
    # Requirements checklist
    st.subheader('Requirements Checklist')
    requirements_cols = st.columns(3)
    
    with requirements_cols[0]:
        st.session_state.requirements_checked['GRE'] = st.checkbox('GRE', st.session_state.requirements_checked['GRE'])
        st.session_state.requirements_checked['TOEFL'] = st.checkbox('TOEFL', st.session_state.requirements_checked['TOEFL'])
    
    with requirements_cols[1]:
        st.session_state.requirements_checked['Transcripts'] = st.checkbox('Transcripts', st.session_state.requirements_checked['Transcripts'])
        st.session_state.requirements_checked['SOP'] = st.checkbox('Statement of Purpose', st.session_state.requirements_checked['SOP'])
    
    with requirements_cols[2]:
        st.session_state.requirements_checked['Resume'] = st.checkbox('Resume', st.session_state.requirements_checked['Resume'])
        st.session_state.requirements_checked['LORs'] = st.checkbox('Letters of Recommendation', st.session_state.requirements_checked['LORs'])

    # Save and Load buttons
    save_col, load_col = st.columns(2)
    with save_col:
        if st.button('Save Progress 💾'):
            save_progress()

with col2:
    # Calculate progress
    general_reqs = sum(1 for key, val in st.session_state.requirements_checked.items() 
                      if key != 'University_Specific' and val)
    total_general_reqs = len(st.session_state.requirements_checked) - 1  # Subtract 1 for University_Specific
    progress = general_reqs / total_general_reqs
    
    st.subheader('Overall Progress')
    st.progress(progress)
    st.write(f'{progress * 100:.0f}% Complete')

# Main content
st.header('University Applications')

# Create a container for the scrollable table
with st.container():
    # Display the filtered dataframe with a link column
    st.dataframe(
        filtered_df,
        column_config={
            "University": st.column_config.TextColumn("University", width=200),
            "Requirements": st.column_config.TextColumn("Requirements", width=300),
            "Expected_Qualities": st.column_config.TextColumn("Expected Qualities", width=300),
            "Apply_Link": st.column_config.LinkColumn("Application Link", width=200),
            "Program_Fee": st.column_config.TextColumn("Program Fee", width=200),
            "Acceptance_Rate": st.column_config.TextColumn("Acceptance Rate", width=100),  # Add this line
            "Program": st.column_config.TextColumn("Program", width=200)
        },
        hide_index=True,
        use_container_width=True
    )
# University-specific requirements tracking
st.header('University-Specific Progress')
for idx, row in filtered_df.iterrows():
    university = row['University']
    if university not in st.session_state.requirements_checked['University_Specific']:
        st.session_state.requirements_checked['University_Specific'][university] = {
            'Application_Started': False,
            'Documents_Uploaded': False,
            'Application_Submitted': False,
            'Fee_Paid': False
        }
    
    univ_progress = st.session_state.requirements_checked['University_Specific'][university]
    
    with st.expander(f"{university} Progress"):
        cols = st.columns(4)
        with cols[0]:
            univ_progress['Application_Started'] = st.checkbox(
                'Application Started',
                univ_progress['Application_Started'],
                key=f'start_{university}'
            )
        with cols[1]:
            univ_progress['Documents_Uploaded'] = st.checkbox(
                'Documents Uploaded',
                univ_progress['Documents_Uploaded'],
                key=f'docs_{university}'
            )
        with cols[2]:
            univ_progress['Application_Submitted'] = st.checkbox(
                'Application Submitted',
                univ_progress['Application_Submitted'],
                key=f'submit_{university}'
            )
        with cols[3]:
            univ_progress['Fee_Paid'] = st.checkbox(
                'Fee Paid',
                univ_progress['Fee_Paid'],
                key=f'fee_{university}'
            )
        
        # Calculate university-specific progress
        univ_progress_value = sum(univ_progress.values()) / len(univ_progress)
        st.progress(univ_progress_value)
        st.write(f'Progress: {univ_progress_value * 100:.0f}%')

# Statistics
st.header('Application Statistics')
col1, col2 = st.columns(2)

with col1:
    st.metric("Total Universities", len(filtered_df))
    avg_fee = filtered_df['Application_Fee'].str.replace('$', '').astype(float).mean()
    st.metric("Average Application Fee", f"${avg_fee:.2f}")

with col2:
    st.metric("Self Apply Count", len(filtered_df[filtered_df['Category'] == 'Self Apply']))
    st.metric("IDP Consultancy Count", len(filtered_df[filtered_df['Category'] == 'IDP Consultancy']))

# Download section
st.header('Download Data')
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="Download as CSV",
    data=csv,
    file_name="university_applications.csv",
    mime="text/csv"
)

# Notes and tips
st.header('Important Notes')
st.info("""
- All deadlines are for Fall 2024 admission
- Requirements may change; always verify on university websites
- Application fees are subject to change
- GRE scores are generally valid for 5 years
- TOEFL scores are generally valid for 2 years
""")