import streamlit as st

# ---------------- AI PROMPT START ----------------
AI_GENERATION_PROMPT = '''
You are an expert software engineer and Streamlit developer. Write a complete, production-ready Streamlit app that:

1. **Replicates the exact layout** of a provided daily diary PDF template with 100% fidelity, including fonts, margins, table structure, and placeholders for user input.
2. **Parses input PDFs** (daily site report) to extract fields (e.g., date, tasks, site status) and populates the diary template automatically.
3. Uses **PyMuPDF**, **pdfminer.six**, and **ReportLab** for PDF parsing and generation. Show imports and dependency versions.
4. Organizes code into modules: `app.py`, `pdf_parser.py`, `pdf_generator.py`, `data_models.py`, and a configuration file (`config.toml`).
5. Provides a **`requirements.txt`** listing exact package versions compatible with Python 3.10.
6. Includes **unit tests** for parsing functions using `pytest`, covering edge cases (missing fields, multi-page PDFs).
7. Presents a **UI** with:
   - A file uploader for the site-report PDF.
   - A preview of extracted fields in a form layout matching the diary.
   - A download button for the generated diary PDF.
8. Follows best practices: proper exception handling, logging, type hints, and modular design.

# AI Generation Prompt
'''
# ---------------- AI PROMPT END ----------------

import pandas as pd
from datetime import datetime, date
import io
import base64
import os
from typing import Optional, Dict, List
import traceback

# Import utilities
from utils.pdf_parser import PDFParser
from utils.gemini_processor import GeminiProcessor
from utils.enhanced_pdf_generator import EnhancedPDFGenerator
from utils.data_models import DailyDiaryData, SiteReportData

# Page configuration
st.set_page_config(
    page_title="Daily Site Report to Diary Converter",
    page_icon="📋",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = None
    if 'generated_pdf' not in st.session_state:
        st.session_state.generated_pdf = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False

def main():
    initialize_session_state()
    
    st.title("🏗️ Daily Site Report to Diary Converter")
    st.markdown("Convert detailed site reports into standardized Daily Diary PDF format using AI")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    # Logo management section
    with st.sidebar.expander("📷 Logo Management"):
        st.markdown("**Upload Company Logos**")
        
        nicholas_logo = st.file_uploader(
            "Nicholas O'Dwyer Logo",
            type=['png', 'jpg', 'jpeg'],
            key="nicholas_logo"
        )
        
        ms_logo = st.file_uploader(
            "MS Consultancy Logo", 
            type=['png', 'jpg', 'jpeg'],
            key="ms_logo"
        )
        
        if nicholas_logo:
            # Save to attached_assets
            os.makedirs("attached_assets", exist_ok=True)
            with open(f"attached_assets/nicholas_odwyer_logo.{nicholas_logo.name.split('.')[-1]}", "wb") as f:
                f.write(nicholas_logo.getbuffer())
            st.success("✅ Nicholas O'Dwyer logo uploaded")
        
        if ms_logo:
            # Save to attached_assets
            os.makedirs("attached_assets", exist_ok=True)
            with open(f"attached_assets/ms_consultancy_logo.{ms_logo.name.split('.')[-1]}", "wb") as f:
                f.write(ms_logo.getbuffer())
            st.success("✅ MS Consultancy logo uploaded")
    
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Upload & Process", "Review & Edit", "Generate PDF", "History"]
    )
    
    if page == "Upload & Process":
        upload_and_process_page()
    elif page == "Review & Edit":
        review_and_edit_page()
    elif page == "Generate PDF":
        generate_pdf_page()
    elif page == "History":
        history_page()

def upload_and_process_page():
    """Page for uploading and processing site reports"""
    st.header("📤 Upload Site Report")
    
    # Check for Gemini API key
    import os
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_api_key:
        st.error("⚠️ Gemini API key not found. Please add GEMINI_API_KEY to your environment variables.")
        st.stop()
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Upload PDF", "Manual Entry"],
        horizontal=True
    )
    
    if input_method == "Upload PDF":
        handle_pdf_upload()
    else:
        handle_manual_entry()

def handle_pdf_upload():
    """Handle PDF file upload and processing"""
    uploaded_file = st.file_uploader(
        "Upload site report PDF",
        type=['pdf'],
        help="Upload a daily site report PDF to extract information automatically"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        if st.button("🤖 Process with AI", type="primary"):
            process_uploaded_pdf(uploaded_file)

def process_uploaded_pdf(uploaded_file):
    """Process the uploaded PDF file"""
    try:
        with st.spinner("🔍 Extracting text from PDF..."):
            # Parse PDF
            parser = PDFParser()
            raw_text = parser.extract_text_from_pdf(uploaded_file)
            
            if not raw_text.strip():
                st.error("❌ No text could be extracted from the PDF. Please try a different file or use manual entry.")
                return
            
            st.success("✅ Text extracted successfully")
            
            # Show extracted text in expandable section with language detection
            with st.expander("📄 Extracted Text (Click to view)"):
                st.text_area("Raw extracted text:", raw_text, height=200, disabled=True)
                
                # Show text statistics
                word_count = len(raw_text.split())
                char_count = len(raw_text)
                line_count = len(raw_text.split('\n'))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words", word_count)
                with col2:
                    st.metric("Characters", char_count)
                with col3:
                    st.metric("Lines", line_count)
                
                # Detect potential multilingual content
                if any(ord(char) > 127 for char in raw_text):
                    st.info("🌍 Multilingual content detected - preserving original text formatting")
                
                # Show OCR confidence if available
                if hasattr(st.session_state, 'ocr_confidence'):
                    st.metric("OCR Confidence", f"{st.session_state.ocr_confidence:.1f}%")
        
        with st.spinner("🧠 Processing with Gemini AI..."):
            # Process with Gemini
            import os
            gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
            processor = GeminiProcessor(gemini_api_key)
            
            extracted_data = processor.extract_site_report_data(raw_text)
            
            if extracted_data:
                st.session_state.extracted_data = extracted_data
                st.session_state.processing_complete = True
                st.success("✅ Data extracted successfully! Navigate to 'Review & Edit' to continue.")
                
                # Show summary of extracted data
                show_extraction_summary(extracted_data)
            else:
                st.error("❌ Failed to extract structured data from the report.")
                
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        st.error("Please try again or use manual entry method.")
        with st.expander("🐛 Error Details"):
            st.code(traceback.format_exc())

def handle_manual_entry():
    """Handle manual data entry"""
    st.subheader("✏️ Manual Data Entry")
    
    with st.form("manual_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Project Information")
            project_name = st.text_input("Project Name", placeholder="Enter project name")
            employer = st.text_input("Employer", placeholder="Enter employer name")
            consultant = st.text_input("Consultant", placeholder="Enter consultant name")
            contractor = st.text_input("Contractor", placeholder="Enter contractor name")
            
            report_date = st.date_input("Date", value=date.today())
            time_period = st.selectbox("Time Period", ["Morning", "Afternoon", "Full Day"])
            weather = st.selectbox("Weather Condition", ["Sunny/Dry", "Rainy/Wet", "Cloudy", "Other"])
            location = st.text_input("Location", placeholder="Enter site location")
        
        with col2:
            st.subheader("Activities")
            activities_text = st.text_area(
                "Major Activities (one per line)",
                placeholder="Enter activities, one per line:\n- Excavation work\n- Pipe laying\n- Concrete work",
                height=150
            )
            
            st.subheader("Equipment & Personnel")
            equipment_text = st.text_area(
                "Equipment Used (format: Equipment Type, Quantity, Hours)",
                placeholder="Enter equipment details:\nExcavator, 2, 8\nDumper Truck, 1, 6",
                height=100
            )
            
            personnel_text = st.text_area(
                "Personnel (format: Role, Number)",
                placeholder="Enter personnel details:\nForeman, 1\nLaborer, 5\nDriver, 2",
                height=100
            )
        
        submitted = st.form_submit_button("📝 Create Daily Diary Entry", type="primary")
        
        if submitted:
            if not all([project_name, employer, contractor, report_date]):
                st.error("❌ Please fill in all required fields (Project Name, Employer, Contractor, Date)")
                return
            
            # Create structured data from manual input
            manual_data = create_manual_data_structure(
                project_name, employer, consultant, contractor,
                report_date, time_period, weather, location,
                activities_text, equipment_text, personnel_text
            )
            
            st.session_state.extracted_data = manual_data
            st.session_state.processing_complete = True
            st.success("✅ Manual entry completed! Navigate to 'Review & Edit' to continue.")

def create_manual_data_structure(project_name, employer, consultant, contractor,
                                report_date, time_period, weather, location,
                                activities_text, equipment_text, personnel_text):
    """Create structured data from manual input"""
    
    # Parse activities
    activities = []
    if activities_text.strip():
        for i, activity in enumerate(activities_text.strip().split('\n'), 1):
            if activity.strip():
                activities.append({
                    'sn': i,
                    'description': activity.strip().lstrip('- ')
                })
    
    # Parse equipment
    equipment = []
    if equipment_text.strip():
        for i, eq_line in enumerate(equipment_text.strip().split('\n'), 1):
            if eq_line.strip():
                parts = [p.strip() for p in eq_line.split(',')]
                equipment.append({
                    'sn': i,
                    'equipment': parts[0] if len(parts) > 0 else '',
                    'no': parts[1] if len(parts) > 1 else '1'
                })
    
    # Parse personnel
    personnel = []
    if personnel_text.strip():
        for i, person_line in enumerate(personnel_text.strip().split('\n'), 1):
            if person_line.strip():
                parts = [p.strip() for p in person_line.split(',')]
                personnel.append({
                    'sn': i,
                    'personnel': parts[0] if len(parts) > 0 else '',
                    'no': parts[1] if len(parts) > 1 else '1'
                })
    
    return DailyDiaryData(
        project=project_name,
        employer=employer,
        consultant=consultant,
        contractor=contractor,
        date=report_date.strftime("%d-%m-%Y"),
        time_morning=time_period in ["Morning", "Full Day"],
        time_afternoon=time_period in ["Afternoon", "Full Day"],
        weather_condition=weather,
        location=location,
        activities=activities,
        equipment=equipment,
        personnel=personnel,
        unsafe_acts=[],
        near_miss="",
        obstruction="",
        engineers_note="",
        prepared_by="",
        checked_by="",
        approved_by=""
    )

def show_extraction_summary(data: DailyDiaryData):
    """Show summary of extracted data"""
    st.subheader("📊 Extraction Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Activities", len(data.activities))
    with col2:
        st.metric("Equipment Items", len(data.equipment))
    with col3:
        st.metric("Personnel Types", len(data.personnel))
    with col4:
        st.metric("Date", data.date)
    
    # Show key information
    with st.expander("🔍 Key Information Extracted"):
        st.write(f"**Project:** {data.project}")
        st.write(f"**Location:** {data.location}")
        st.write(f"**Contractor:** {data.contractor}")
        st.write(f"**Weather:** {data.weather_condition}")

def review_and_edit_page():
    """Page for reviewing and editing extracted data"""
    st.header("📝 Review & Edit Extracted Data")
    
    if not st.session_state.processing_complete or not st.session_state.extracted_data:
        st.warning("⚠️ No data to review. Please process a report first in the 'Upload & Process' page.")
        return
    
    data = st.session_state.extracted_data
    
    # Project Information Section
    st.subheader("🏗️ Project Information")
    col1, col2 = st.columns(2)
    
    with col1:
        data.project = st.text_input("Project", value=data.project or "")
        data.employer = st.text_input("Employer", value=data.employer or "")
        data.date = st.text_input("Date", value=data.date or "")
        data.location = st.text_input("Location", value=data.location or "")
    
    with col2:
        data.consultant = st.text_input("Consultant", value=data.consultant or "")
        data.contractor = st.text_input("Contractor", value=data.contractor or "")
        
        # Time period checkboxes
        st.write("**Time Period:**")
        data.time_morning = st.checkbox("Morning", value=data.time_morning)
        data.time_afternoon = st.checkbox("Afternoon", value=data.time_afternoon)
        
        data.weather_condition = st.selectbox(
            "Weather Condition",
            ["Sunny/Dry", "Rainy/Wet", "Cloudy", "Other"],
            index=0 if not data.weather_condition else 
                  ["Sunny/Dry", "Rainy/Wet", "Cloudy", "Other"].index(data.weather_condition) 
                  if data.weather_condition in ["Sunny/Dry", "Rainy/Wet", "Cloudy", "Other"] else 0
        )
    
    # Activities Section
    st.subheader("🔨 Major Activities")
    activities_df = pd.DataFrame(data.activities) if data.activities else pd.DataFrame(columns=['sn', 'description'])
    
    if activities_df.empty:
        activities_df = pd.DataFrame({
            'sn': [1, 2, 3, 4, 5, 6],
            'description': [''] * 6
        })
    
    edited_activities = st.data_editor(
        activities_df,
        num_rows="dynamic",
        use_container_width=True,
        key="activities_editor"
    )
    
    # Equipment Section
    st.subheader("🚜 Equipment")
    equipment_df = pd.DataFrame(data.equipment) if data.equipment else pd.DataFrame(columns=['sn', 'equipment', 'no'])
    
    if equipment_df.empty:
        equipment_df = pd.DataFrame({
            'sn': list(range(1, 11)),
            'equipment': [''] * 10,
            'no': [''] * 10
        })
    
    edited_equipment = st.data_editor(
        equipment_df,
        num_rows="dynamic",
        use_container_width=True,
        key="equipment_editor"
    )
    
    # Personnel Section
    st.subheader("👷 Personnel")
    personnel_df = pd.DataFrame(data.personnel) if data.personnel else pd.DataFrame(columns=['sn', 'personnel', 'no'])
    
    if personnel_df.empty:
        personnel_df = pd.DataFrame({
            'sn': list(range(1, 29)),
            'personnel': [''] * 28,
            'no': [''] * 28
        })
    
    edited_personnel = st.data_editor(
        personnel_df,
        num_rows="dynamic",
        use_container_width=True,
        key="personnel_editor"
    )
    
    # Additional Information
    st.subheader("📋 Additional Information")
    col1, col2 = st.columns(2)
    
    with col1:
        unsafe_acts_text = st.text_area(
            "Unsafe Acts/Conditions Observed",
            value="\n".join([act.get('description', '') for act in data.unsafe_acts]) if data.unsafe_acts else "",
            height=100
        )
        
        data.near_miss = st.text_area(
            "Near Miss/Accidents/Incidents",
            value=data.near_miss or "",
            height=100
        )
    
    with col2:
        data.obstruction = st.text_area(
            "Obstruction/Action Plans",
            value=data.obstruction or "",
            height=100
        )
        
        data.engineers_note = st.text_area(
            "Engineer's Note",
            value=data.engineers_note or "",
            height=100
        )
    
    # Signatures
    st.subheader("✍️ Signatures")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Prepared by (Construction Staff)**")
        data.prepared_by = st.text_input("Name", value=data.prepared_by or "", key="prepared_by")
    
    with col2:
        st.write("**Checked by (Consultant Supervision Staff)**")
        data.checked_by = st.text_input("Name", value=data.checked_by or "", key="checked_by")
    
    with col3:
        st.write("**Approved by (Consultant Supervision Staff)**")
        data.approved_by = st.text_input("Name", value=data.approved_by or "", key="approved_by")
    
    # Update data in session state
    if st.button("💾 Save Changes", type="primary"):
        # Update activities
        data.activities = edited_activities.to_dict('records')
        
        # Update equipment
        data.equipment = edited_equipment.to_dict('records')
        
        # Update personnel
        data.personnel = edited_personnel.to_dict('records')
        
        # Update unsafe acts
        if unsafe_acts_text.strip():
            data.unsafe_acts = [{'sn': i+1, 'description': act.strip()} 
                               for i, act in enumerate(unsafe_acts_text.strip().split('\n')) 
                               if act.strip()]
        else:
            data.unsafe_acts = []
        
        st.session_state.extracted_data = data
        st.success("✅ Changes saved successfully! Navigate to 'Generate PDF' to create the Daily Diary.")

def generate_pdf_page():
    """Page for generating the final PDF"""
    st.header("📄 Generate Daily Diary PDF")
    
    if not st.session_state.processing_complete or not st.session_state.extracted_data:
        st.warning("⚠️ No data available. Please process and review a report first.")
        return
    
    data = st.session_state.extracted_data
    
    # Show final data summary with validation
    st.subheader("📊 Final Data Summary")
    
    # Validate data before showing summary
    validation_errors = data.validate()
    if validation_errors:
        st.warning("⚠️ Data validation warnings:")
        for error in validation_errors[:3]:  # Show first 3 errors
            st.warning(f"• {error}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Project:** {data.project or 'Not specified'}")
        st.info(f"**Date:** {data.date or 'Not specified'}")
    with col2:
        st.info(f"**Location:** {data.location or 'Not specified'}")
        st.info(f"**Contractor:** {data.contractor or 'Not specified'}")
    with col3:
        activities_count = len([a for a in data.activities if a.get('description', '') and str(a.get('description', '')).strip()])
        equipment_count = len([e for e in data.equipment if e.get('equipment', '') and str(e.get('equipment', '')).strip()])
        st.info(f"**Activities:** {activities_count}")
        st.info(f"**Equipment:** {equipment_count}")
    
    # Generate PDF button
    if st.button("🔄 Generate Daily Diary PDF", type="primary"):
        try:
            with st.spinner("📄 Generating PDF..."):
                generator = EnhancedPDFGenerator()
                pdf_buffer = generator.generate_daily_diary_pdf(data)
                
                if pdf_buffer:
                    st.session_state.generated_pdf = pdf_buffer
                    st.success("✅ PDF generated successfully!")
                    
                    # Provide download button
                    st.download_button(
                        label="📥 Download Daily Diary PDF",
                        data=pdf_buffer,
                        file_name=f"daily_diary_{data.date.replace('-', '_')}.pdf",
                        mime="application/pdf"
                    )
                    
                    # Show PDF preview info
                    st.info("📋 PDF has been generated with all the extracted and edited information formatted according to the Daily Diary template.")
                    
                else:
                    st.error("❌ Failed to generate PDF. Please try again.")
                    
        except Exception as e:
            st.error(f"❌ Error generating PDF: {str(e)}")
            with st.expander("🐛 Error Details"):
                st.code(traceback.format_exc())

def history_page():
    """Page for viewing processing history"""
    st.header("📚 Processing History")
    st.info("📝 History functionality will be implemented in future versions.")
    st.write("This page will show:")
    st.write("- Previously processed reports")
    st.write("- Generated PDFs")
    st.write("- Processing statistics")
    st.write("- Export/import functionality")

if __name__ == "__main__":
    main()
