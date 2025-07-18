import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib.parse
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import webbrowser



# Configure Streamlit page
st.set_page_config(
    page_title="Clinical Trial Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown('''
<link href="https://fonts.googleapis.com/css2?family=Albert+Sans&family=Rubik:wght@300&display=swap" rel="stylesheet">

<style>
    body {
        font-family: 'Albert Sans', sans-serif;
        background-color: #F4F2F1;
    }
    .stApp {
        background-color: #F4F2F1;
    }
    h1, h2, h3, h4, h5 {
        font-family: 'Rubik', sans-serif;
        color: #121335;
    }
    .stButton>button {
        background-color: #AB4D9C;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #294B9D;
    }
    .metric-container {
        background-color: #4CC5DD;
        color: #121335;
        border-radius: 10px;
        padding: 1rem;
        font-family: 'Albert Sans', sans-serif;
    }
    .highlight-card {
        background: #F89823;
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
    }
</style>
''', unsafe_allow_html=True)
# Custom CSS for purple theme
# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'patients' not in st.session_state:
    st.session_state.patients = None
if 'show_new_patient_form' not in st.session_state:
    st.session_state.show_new_patient_form = False

# Mock data for Western Australian patients
@st.cache_data
def load_patient_data():
    patients_data = [
        {
            'patient_id': 'PT001',
            'name': 'Sarah Mitchell',
            'account_number': '123456789',
            'bsb': '036-012',
            'address': '45 Stirling Highway, Nedlands WA 6009',
            'study_id': 'CARDIO-2024-001',
            'study_name': 'Cardiac Prevention Study',
            'age': 34,
            'phone': '(08) 9123-4567',
            'email': 'sarah.mitchell@email.com',
            'upcoming_visit': datetime.now() + timedelta(days=2),
            'visit_duration': 4,
            'hospital': 'Royal Perth Hospital',
            'hospital_address': '197 Wellington Street, Perth WA 6000',
            'transport_method': 'car',
            'distance': 12,
            'status': 'upcoming',
            'receipts': ['parking-receipt-001.pdf', 'meal-receipt-001.pdf']
        },
        {
            'patient_id': 'PT002',
            'name': 'James Wilson',
            'account_number': '987654321',
            'bsb': '066-102',
            'address': '78 Hay Street, Subiaco WA 6008',
            'study_id': 'NEURO-2024-003',
            'study_name': 'Neurological Assessment Trial',
            'age': 42,
            'phone': '(08) 9234-5678',
            'email': 'james.wilson@email.com',
            'upcoming_visit': datetime.now() + timedelta(days=7),
            'visit_duration': 2,
            'hospital': 'Sir Charles Gairdner Hospital',
            'hospital_address': 'Hospital Avenue, Nedlands WA 6009',
            'transport_method': 'public',
            'distance': 0,
            'status': 'completed',
            'receipts': []
        },
        {
            'patient_id': 'PT003',
            'name': 'Emma Thompson',
            'account_number': '456789123',
            'bsb': '016-789',
            'address': '23 Ocean Drive, Cottesloe WA 6011',
            'study_id': 'ONCOLOGY-2024-007',
            'study_name': 'Cancer Treatment Efficacy Study',
            'age': 56,
            'phone': '(08) 9345-6789',
            'email': 'emma.thompson@email.com',
            'upcoming_visit': datetime.now() + timedelta(days=1),
            'visit_duration': 5,
            'hospital': 'Fiona Stanley Hospital',
            'hospital_address': '11 Robin Warren Drive, Murdoch WA 6150',
            'transport_method': 'car',
            'distance': 28,
            'status': 'upcoming',
            'receipts': ['parking-receipt-003.pdf', 'meal-receipt-003.pdf']
        },
        {
            'patient_id': 'PT004',
            'name': 'Michael Brown',
            'account_number': '789123456',
            'bsb': '086-023',
            'address': '156 Great Eastern Highway, Belmont WA 6104',
            'study_id': 'DIABETES-2024-012',
            'study_name': 'Diabetes Management Protocol',
            'age': 48,
            'phone': '(08) 9456-7890',
            'email': 'michael.brown@email.com',
            'upcoming_visit': datetime.now() + timedelta(days=4),
            'visit_duration': 3,
            'hospital': 'Royal Perth Hospital',
            'hospital_address': '197 Wellington Street, Perth WA 6000',
            'transport_method': 'taxi',
            'distance': 22,
            'status': 'completed',
            'receipts': ['taxi-receipt-004.pdf']
        },
        {
            'patient_id': 'PT005',
            'name': 'Lisa Anderson',
            'account_number': '321654987',
            'bsb': '036-089',
            'address': '89 Canning Highway, South Perth WA 6151',
            'study_id': 'RESPIRATORY-2024-005',
            'study_name': 'Respiratory Function Analysis',
            'age': 39,
            'phone': '(08) 9567-8901',
            'email': 'lisa.anderson@email.com',
            'upcoming_visit': datetime.now() + timedelta(days=10),
            'visit_duration': 6,
            'hospital': 'Sir Charles Gairdner Hospital',
            'hospital_address': 'Hospital Avenue, Nedlands WA 6009',
            'transport_method': 'car',
            'distance': 18,
            'status': 'approved',
            'receipts': ['parking-receipt-005.pdf', 'meal-receipt-005.pdf']
        }
    ]
    return pd.DataFrame(patients_data)

# Helper functions
def calculate_reimbursement(transport_method, distance, duration):
    if transport_method == 'public':
        return 0
    km_reimbursement = distance * 0.44
    meal_allowance = 25 if duration > 3 else 0
    return km_reimbursement + meal_allowance

def get_google_maps_link(from_address, to_address):
    encoded_from = urllib.parse.quote(from_address)
    encoded_to = urllib.parse.quote(to_address)
    return f"https://www.google.com/maps/dir/{encoded_from}/{encoded_to}"

def generate_invoice_pdf(patient_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.purple,
        alignment=1
    )
    story.append(Paragraph("CLINICAL TRIAL REIMBURSEMENT INVOICE", title_style))
    story.append(Spacer(1, 12))
    
    # Patient details
    patient_info = [
        ['Patient ID:', patient_data['patient_id']],
        ['Patient Name:', patient_data['name']],
        ['Study:', patient_data['study_name']],
        ['Visit Date:', patient_data['upcoming_visit'].strftime('%Y-%m-%d')],
        ['Transport Method:', patient_data['transport_method'].title()],
        ['Distance:', f"{patient_data['distance']}km"],
        ['Duration:', f"{patient_data['visit_duration']} hours"]
    ]
    
    patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 12))
    
    # Reimbursement calculation
    km_reimbursement = patient_data['distance'] * 0.44
    meal_allowance = 25 if patient_data['visit_duration'] > 3 else 0
    total_reimbursement = km_reimbursement + meal_allowance
    
    reimbursement_info = [
        ['KM Reimbursement (44¢/km):', f"${km_reimbursement:.2f}"],
        ['Meal Allowance (>3hrs):', f"${meal_allowance:.2f}"],
        ['TOTAL REIMBURSEMENT:', f"${total_reimbursement:.2f}"]
    ]
    
    reimbursement_table = Table(reimbursement_info, colWidths=[3*inch, 2*inch])
    reimbursement_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.purple),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(reimbursement_table)
    story.append(Spacer(1, 12))
    
    # Banking details
    story.append(Paragraph("BANKING DETAILS", styles['Heading2']))
    banking_info = [
        ['BSB:', patient_data['bsb']],
        ['Account Number:', patient_data['account_number']],
        ['Account Name:', patient_data['name']]
    ]
    
    banking_table = Table(banking_info, colWidths=[2*inch, 4*inch])
    banking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12)
    ]))
    
    story.append(banking_table)
    
    # Receipts section
    story.append(Spacer(1, 12))
    story.append(Paragraph("ATTACHED RECEIPTS", styles['Heading2']))
    if patient_data['receipts']:
        for receipt in patient_data['receipts']:
            story.append(Paragraph(f"• {receipt}", styles['Normal']))
    else:
        story.append(Paragraph("No receipts attached", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def show_new_patient_form():
    """Display the new patient form"""
    st.markdown("""
    <div class="new-patient-form">
        <h3 style="color: #4a148c; text-align: center;">Enter New Patient Information</h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("new_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Information")
            name = st.text_input("Full Name*", placeholder="Enter patient's full name")
            age = st.number_input("Age*", min_value=18, max_value=100, value=30)
            phone = st.text_input("Phone Number*", placeholder="(08) 9XXX-XXXX")
            email = st.text_input("Email Address*", placeholder="patient@email.com")
            address = st.text_area("Address*", placeholder="Street address, Suburb WA Postcode")
            
        with col2:
            st.subheader("Study & Banking Information")
            study_id = st.text_input("Study ID*", placeholder="e.g., CARDIO-2024-001")
            study_name = st.text_input("Study Name*", placeholder="Enter study name")
            hospital = st.selectbox("Hospital*", [
                "Royal Perth Hospital",
                "Sir Charles Gairdner Hospital", 
                "Fiona Stanley Hospital",
                "Fremantle Hospital",
                "Princess Margaret Hospital"
            ])
            bsb = st.text_input("BSB*", placeholder="XXX-XXX")
            account_number = st.text_input("Account Number*", placeholder="Account number")
            
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Visit Details")
            visit_date = st.date_input("Next Visit Date*", min_value=datetime.now().date())
            visit_duration = st.number_input("Visit Duration (hours)*", min_value=1, max_value=8, value=3)
            
        with col4:
            st.subheader("Transport Information")
            transport_method = st.selectbox("Transport Method*", ["car", "taxi", "public"])
            if transport_method != "public":
                distance = st.number_input("Distance (km)*", min_value=1, max_value=200, value=10)
            else:
                distance = 0
                st.info("Public transport is not eligible for KM reimbursement")
        
        # Submit button
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submitted = st.form_submit_button("Add Patient", use_container_width=True)
        
        with col_cancel:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not all([name, age, phone, email, address, study_id, study_name, hospital, bsb, account_number]):
                st.error("Please fill in all required fields marked with *")
            else:
                # Generate new patient ID
                existing_patients = load_patient_data()
                patient_count = len(existing_patients) + 1
                new_patient_id = f"PT{patient_count:03d}"
                
                # Hospital addresses mapping
                hospital_addresses = {
                    "Royal Perth Hospital": "197 Wellington Street, Perth WA 6000",
                    "Sir Charles Gairdner Hospital": "Hospital Avenue, Nedlands WA 6009",
                    "Fiona Stanley Hospital": "11 Robin Warren Drive, Murdoch WA 6150",
                    "Fremantle Hospital": "Alma Street, Fremantle WA 6160",
                    "Princess Margaret Hospital": "Roberts Road, Subiaco WA 6008"
                }
                
                # Create new patient data
                new_patient = {
                    'patient_id': new_patient_id,
                    'name': name,
                    'account_number': account_number,
                    'bsb': bsb,
                    'address': address,
                    'study_id': study_id,
                    'study_name': study_name,
                    'age': age,
                    'phone': phone,
                    'email': email,
                    'upcoming_visit': datetime.combine(visit_date, datetime.min.time()),
                    'visit_duration': visit_duration,
                    'hospital': hospital,
                    'hospital_address': hospital_addresses[hospital],
                    'transport_method': transport_method,
                    'distance': distance,
                    'status': 'upcoming',
                    'receipts': []
                }
                
                st.success(f"Patient {name} added successfully with ID: {new_patient_id}")
                st.session_state.show_new_patient_form = False
                st.rerun()
        
        if cancelled:
            st.session_state.show_new_patient_form = False
            st.rerun()

# Login interface
def show_login():
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="color: #4a148c; font-size: 3rem; margin-bottom: 1rem;">🏥</h1>
        <h1 style="color: #4a148c;">Clinical Trial Management System</h1>
        <p style="font-size: 1.2rem; color: #666;">Patient Management & Reimbursement Portal</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Demo Login Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Login as Participant", use_container_width=True):
            st.session_state.current_user = 'participant'
            st.rerun()
    
    with col2:
        if st.button("Login as Coordinator", use_container_width=True):
            st.session_state.current_user = 'coordinator'
            st.rerun()
    
    with col3:
        if st.button("Login as Admin/Finance", use_container_width=True):
            st.session_state.current_user = 'admin'
            st.rerun()
    
    with st.expander("Sample Credentials"):
        st.markdown("""
        - **Participant**: participant@demo.com / demo123
        - **Coordinator**: coordinator@demo.com / demo123  
        - **Admin**: admin@demo.com / demo123
        """)

# Participant dashboard
def show_participant_dashboard(df):
    st.title("Participant Portal")
    
    # Top-right button for new patient info
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Enter New Patient Info", type="primary", use_container_width=True):
            st.session_state.show_new_patient_form = True
            st.rerun()
    
    # Show new patient form if requested
    if st.session_state.show_new_patient_form:
        show_new_patient_form()
        return
    
    # Next upcoming visit card
    upcoming_patients = df[df['status'] == 'upcoming'].sort_values('upcoming_visit')
    if not upcoming_patients.empty:
        next_patient = upcoming_patients.iloc[0]
        
        st.markdown(f"""
        <div class="highlight-card">
            <h3>Next Upcoming Visit</h3>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4>{next_patient['name']}</h4>
                    <p>{next_patient['study_name']}</p>
                </div>
                <div>
                    <p><strong> {next_patient['upcoming_visit'].strftime('%B %d, %Y')}</strong></p>
                    <p> {next_patient['hospital']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("###  Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(" Submit Claims", use_container_width=True):
            st.success("Claims submission interface opened!")
    
    with col2:
        if st.button(" View Claims", use_container_width=True):
            st.info("Displaying your submitted claims...")
    
    with col3:
        if st.button(" Check Status", use_container_width=True):
            st.info("Checking claim status...")
    
    with col4:
        if st.button(" Contact Support", use_container_width=True):
            st.info("Support contact: (08) 9000-0000")
    
    # Patient table
    st.markdown("###  All Registered Patients")
    
    # Display patient data in a more readable format
    for _, patient in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="patient-card">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                    <div>
                        <strong>{patient['name']}</strong><br>
                        ID: {patient['patient_id']}<br>
                        Age: {patient['age']}<br>
                        📍 {patient['address']}
                    </div>
                    <div>
                        <strong>{patient['study_name']}</strong><br>
                        Study ID: {patient['study_id']}<br>
                         {patient['phone']}<br>
                         {patient['email']}
                    </div>
                    <div>
                        <strong>Next Visit:</strong><br>
                        {patient['upcoming_visit'].strftime('%Y-%m-%d')}<br>
                        {patient['hospital']}<br>
                        BSB: {patient['bsb']} | Acc: {patient['account_number']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Coordinator dashboard
def show_coordinator_dashboard(df):
    st.title(" Study Coordinator Portal")
    
    # Summary metrics
    completed_patients = df[df['status'] == 'completed']
    eligible_patients = completed_patients[completed_patients['transport_method'] != 'public']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3>{len(eligible_patients)}</h3>
            <p>Eligible Patients</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_km = eligible_patients['distance'].sum() if not eligible_patients.empty else 0
        st.markdown(f"""
        <div class="metric-container">
            <h3>{total_km}</h3>
            <p>Total KM</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_reimbursement = sum(calculate_reimbursement(row['transport_method'], row['distance'], row['visit_duration']) 
                                for _, row in eligible_patients.iterrows()) if not eligible_patients.empty else 0
        st.markdown(f"""
        <div class="metric-container">
            <h3>${total_reimbursement:.2f}</h3>
            <p>Total Reimbursement</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Post-visit claim management
    st.markdown("###  Post-Visit Claim Management")
    
    if completed_patients.empty:
        st.info("No completed visits pending approval.")
    else:
        for _, patient in completed_patients.iterrows():
            reimbursement = calculate_reimbursement(patient['transport_method'], patient['distance'], patient['visit_duration'])
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.write(f"**{patient['name']}**")
                    st.write(f"{patient['study_name']}")
                
                with col2:
                    transport_emoji = {"car": "🚗", "taxi": "🚕", "public": "🚌"}
                    st.write(f"{transport_emoji.get(patient['transport_method'], '🚗')} {patient['transport_method'].title()}")
                    st.write(f"📏 {patient['distance']}km")
                
                with col3:
                    st.write(f" {patient['visit_duration']}h")
                    if patient['transport_method'] == 'public':
                        st.error("Not Eligible")
                    else:
                        st.success(f"${reimbursement:.2f}")
                
                with col4:
                    col_approve, col_reject = st.columns(2)
                    with col_approve:
                        if st.button(f"Approve", key=f"approve_{patient['patient_id']}", 
                                   disabled=patient['transport_method'] == 'public'):
                            st.success(f"Approved claim for {patient['name']}")
                    
                    with col_reject:
                        if st.button(f" Reject", key=f"reject_{patient['patient_id']}"):
                            st.error(f"Rejected claim for {patient['name']}")
                
                st.divider()

# Admin dashboard
def show_admin_dashboard(df):
    st.title(" Admin/Finance Portal")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Patient Management", "Reimbursement Management", "Analytics", "Banking"])
    
    with tab1:
        st.markdown("### 👥 Patient Management")
        
        # Search functionality
        search_term = st.text_input(" Search patients...", placeholder="Enter name, ID, or study name")
        
        filtered_df = df
        if search_term:
            filtered_df = df[
                df['name'].str.contains(search_term, case=False) |
                df['patient_id'].str.contains(search_term, case=False) |
                df['study_name'].str.contains(search_term, case=False)
            ]
        
        # Display patient table
        st.dataframe(
            filtered_df[['patient_id', 'name', 'age', 'study_name', 'phone', 'email', 'status']],
            use_container_width=True
        )
    
    with tab2:
        st.markdown("###  Reimbursement Management")
        
        # Summary metrics
        approved_patients = df[df['status'] == 'approved']
        completed_patients = df[df['status'] == 'completed']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <h3>{len(approved_patients)}</h3>
                <p>Approved Claims</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pending_amount = sum(calculate_reimbursement(row['transport_method'], row['distance'], row['visit_duration']) 
                               for _, row in approved_patients.iterrows()) if not approved_patients.empty else 0
            st.markdown(f"""
            <div class="metric-container">
                <h3>${pending_amount:.2f}</h3>
                <p>Pending Payments</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_completed = sum(calculate_reimbursement(row['transport_method'], row['distance'], row['visit_duration']) 
                                for _, row in completed_patients.iterrows()) if not completed_patients.empty else 0
            st.markdown(f"""
            <div class="metric-container">
                <h3>${total_completed:.2f}</h3>
                <p>Total Completed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_claim = (pending_amount / len(approved_patients)) if len(approved_patients) > 0 else 0
            st.markdown(f"""
            <div class="metric-container">
                <h3>${avg_claim:.2f}</h3>
                <p>Average Claim</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced reimbursement table with Google Maps and Invoice functionality
        st.markdown("###  Payment Processing")
        
        if approved_patients.empty:
            st.info("No approved claims pending payment.")
        else:
            # Create enhanced dataframe for display
            payment_data = []
            for _, patient in approved_patients.iterrows():
                reimbursement = calculate_reimbursement(patient['transport_method'], patient['distance'], patient['visit_duration'])
                km_cost = patient['distance'] * 0.44 if patient['transport_method'] != 'public' else 0
                meal_allowance = 25 if patient['visit_duration'] > 3 else 0
                
                payment_data.append({
                    'Patient ID': patient['patient_id'],
                    'Name': patient['name'],
                    'Study': patient['study_name'],
                    'Transport': patient['transport_method'].title(),
                    'Distance (km)': patient['distance'],
                    'Duration (hrs)': patient['visit_duration'],
                    'KM Cost': f"${km_cost:.2f}",
                    'Meal Allowance': f"${meal_allowance:.2f}",
                    'Total Reimbursement': f"${reimbursement:.2f}",
                    'BSB': patient['bsb'],
                    'Account': patient['account_number'],
                    'Hospital': patient['hospital'],
                    'Patient Address': patient['address'],
                    'Hospital Address': patient['hospital_address'],
                    'Receipts': len(patient['receipts'])
                })
            
            payment_df = pd.DataFrame(payment_data)
            
            # Display each payment with enhanced functionality
            for i, (_, patient) in enumerate(approved_patients.iterrows()):
                reimbursement = calculate_reimbursement(patient['transport_method'], patient['distance'], patient['visit_duration'])
                
                with st.expander(f" {patient['name']} - ${reimbursement:.2f}", expanded=False):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write("**Patient Details:**")
                        st.write(f"• ID: {patient['patient_id']}")
                        st.write(f"• Study: {patient['study_name']}")
                        st.write(f"• Address: {patient['address']}")
                        st.write(f"• Phone: {patient['phone']}")
                        st.write(f"• Email: {patient['email']}")
                    
                    with col2:
                        st.write("**Banking Details:**")
                        st.write(f"• BSB: {patient['bsb']}")
                        st.write(f"• Account: {patient['account_number']}")
                        st.write(f"• Account Name: {patient['name']}")
                        st.write("**Visit Details:**")
                        st.write(f"• Hospital: {patient['hospital']}")
                        st.write(f"• Transport: {patient['transport_method'].title()}")
                        st.write(f"• Distance: {patient['distance']}km")
                        st.write(f"• Duration: {patient['visit_duration']} hours")
                    
                    with col3:
                        st.write("**Actions:**")
                        
                        # Google Maps link
                        maps_link = get_google_maps_link(patient['address'], patient['hospital_address'])
                        st.markdown(f"""
                        <a href="{maps_link}" target="_blank" class="maps-link">
                             View Route
                        </a>
                        """, unsafe_allow_html=True)
                        
                        # Download invoice button
                        if st.button(f" Generate Invoice", key=f"invoice_{patient['patient_id']}"):
                            pdf_buffer = generate_invoice_pdf(patient)
                            
                            # Create download button
                            st.download_button(
                                label=" Download Invoice PDF",
                                data=pdf_buffer.getvalue(),
                                file_name=f"invoice_{patient['patient_id']}_{patient['name'].replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                key=f"download_{patient['patient_id']}"
                            )
                        
                        # View receipts
                        if patient['receipts']:
                            st.write(f"📎 {len(patient['receipts'])} Receipt(s)")
                            for receipt in patient['receipts']:
                                st.write(f"• {receipt}")
                        else:
                            st.write("📎 No receipts")
                        
                        # Payment status
                        if st.button(f" Mark as Paid", key=f"paid_{patient['patient_id']}"):
                            st.success(f"Payment processed for {patient['name']}")
            
            # Bulk export functionality
            st.markdown("### Bulk Export Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(" Export Payment Data", use_container_width=True):
                    csv_buffer = io.StringIO()
                    payment_df.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label=" Download CSV",
                        data=csv_buffer.getvalue(),
                        file_name=f"payment_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button(" Banking Summary", use_container_width=True):
                    banking_summary = payment_df[['Name', 'BSB', 'Account', 'Total Reimbursement']].copy()
                    st.dataframe(banking_summary, use_container_width=True)
            
            with col3:
                if st.button(" All Routes", use_container_width=True):
                    st.markdown("**Google Maps Links for All Patients:**")
                    for _, patient in approved_patients.iterrows():
                        maps_link = get_google_maps_link(patient['address'], patient['hospital_address'])
                        st.markdown(f"• [{patient['name']}]({maps_link}) - {patient['hospital']}")
    
    with tab3:
        st.markdown("###  Analytics Dashboard")
        
        # Transport method distribution
        col1, col2 = st.columns(2)
        
        with col1:
            transport_counts = df['transport_method'].value_counts()
            fig_transport = px.pie(
                values=transport_counts.values,
                names=transport_counts.index,
                title="Transport Method Distribution",
                color_discrete_sequence=['#667eea', '#764ba2', '#8e24aa']
            )
            st.plotly_chart(fig_transport, use_container_width=True)
        
        with col2:
            # Eligibility chart
            eligible_count = len(df[df['transport_method'] != 'public'])
            ineligible_count = len(df[df['transport_method'] == 'public'])
            
            fig_eligibility = px.bar(
                x=['Eligible', 'Not Eligible'],
                y=[eligible_count, ineligible_count],
                title="Reimbursement Eligibility",
                color=['Eligible', 'Not Eligible'],
                color_discrete_map={'Eligible': '#4CAF50', 'Not Eligible': '#f44336'}
            )
            st.plotly_chart(fig_eligibility, use_container_width=True)
        
        # Distance distribution
        eligible_df = df[df['transport_method'] != 'public']
        if not eligible_df.empty:
            fig_distance = px.histogram(
                eligible_df,
                x='distance',
                title="Distance Distribution (Eligible Patients)",
                nbins=20,
                color_discrete_sequence=['#764ba2']
            )
            fig_distance.update_layout(
                xaxis_title="Distance (km)",
                yaxis_title="Number of Patients"
            )
            st.plotly_chart(fig_distance, use_container_width=True)
        
        # Study participation
        study_counts = df['study_name'].value_counts()
        fig_studies = px.bar(
            x=study_counts.index,
            y=study_counts.values,
            title="Patients per Study",
            color_discrete_sequence=['#8e24aa']
        )
        fig_studies.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_studies, use_container_width=True)
    
    with tab4:
        st.markdown("###  Banking & Payment Details")
        
        # Banking summary table
        banking_data = []
        for _, patient in df.iterrows():
            if patient['status'] in ['approved', 'completed']:
                reimbursement = calculate_reimbursement(patient['transport_method'], patient['distance'], patient['visit_duration'])
                
                banking_data.append({
                    'Patient ID': patient['patient_id'],
                    'Patient Name': patient['name'],
                    'BSB': patient['bsb'],
                    'Account Number': patient['account_number'],
                    'Amount': reimbursement,
                    'Status': patient['status'].title(),
                    'Study': patient['study_name'],
                    'Hospital': patient['hospital'],
                    'Route': get_google_maps_link(patient['address'], patient['hospital_address']),
                    'From Address': patient['address'],
                    'To Address': patient['hospital_address'],
                    'Distance': patient['distance'],
                    'Transport': patient['transport_method'],
                    'Receipts': len(patient['receipts'])
                })
        
        if banking_data:
            banking_df = pd.DataFrame(banking_data)
            
            # Enhanced banking table with clickable links
            st.markdown("**Payment-Ready Accounts:**")
            
            for _, row in banking_df.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{row['Patient Name']}** ({row['Patient ID']})")
                        st.write(f"Study: {row['Study']}")
                        st.write(f"Status: {row['Status']}")
                    
                    with col2:
                        st.write(f"**Banking:** {row['BSB']} | {row['Account Number']}")
                        st.write(f"**Amount:** ${row['Amount']:.2f}")
                        st.write(f"**Hospital:** {row['Hospital']}")
                    
                    with col3:
                        st.markdown(f"""
                        <a href="{row['Route']}" target="_blank" class="maps-link">
                             {row['Distance']}km Route
                        </a>
                        """, unsafe_allow_html=True)
                        st.write(f"📎 {row['Receipts']} Receipt(s)")
                    
                    with col4:
                        patient_data = df[df['patient_id'] == row['Patient ID']].iloc[0]
                        if st.button(f" Invoice", key=f"banking_invoice_{row['Patient ID']}"):
                            pdf_buffer = generate_invoice_pdf(patient_data)
                            st.download_button(
                                label=" Download",
                                data=pdf_buffer.getvalue(),
                                file_name=f"invoice_{row['Patient ID']}.pdf",
                                mime="application/pdf",
                                key=f"banking_download_{row['Patient ID']}"
                            )
                    
                    st.divider()
            
            # Payment summary
            total_payments = banking_df['Amount'].sum()
            st.markdown(f"""
            <div class="highlight-card">
                <h3> Payment Summary</h3>
                <p><strong>Total Pending Payments:</strong> ${total_payments:.2f}</p>
                <p><strong>Number of Accounts:</strong> {len(banking_df)}</p>
                <p><strong>Average Payment:</strong> ${total_payments/len(banking_df):.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.info("No banking details available for current patients.")

# Main application
def main():
    if st.session_state.current_user is None:
        show_login()
    else:
        # Load patient data
        df = load_patient_data()
        
        # Sidebar
        with st.sidebar:
            st.markdown(f"### Welcome, {st.session_state.current_user.title()}")
            st.markdown(f"**Role:** {st.session_state.current_user.replace('_', ' ').title()}")
            
            if st.button("Logout", use_container_width=True):
                st.session_state.current_user = None
                st.session_state.show_new_patient_form = False
                st.rerun()
            
            st.divider()
            
            # System stats
            st.markdown("###  System Overview")
            st.metric("Total Patients", len(df))
            st.metric("Active Studies", df['study_name'].nunique())
            st.metric("Upcoming Visits", len(df[df['status'] == 'upcoming']))
            
            # Recent activity
            st.markdown("###  Recent Activity")
            st.write("• New patient registered")
            st.write("• Claim approved")
            st.write("• Payment processed")
        
        # Route to appropriate dashboard
        if st.session_state.current_user == 'participant':
            show_participant_dashboard(df)
        elif st.session_state.current_user == 'coordinator':
            show_coordinator_dashboard(df)
        elif st.session_state.current_user == 'admin':
            show_admin_dashboard(df)

if __name__ == "__main__":
    main()