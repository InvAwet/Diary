from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from typing import List, Dict, Optional
from utils.data_models import DailyDiaryData

class PDFGenerator:
    """Class for generating Daily Diary PDF documents"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 20 * mm
        self.setup_styles()
    
    def setup_styles(self):
        """Setup text styles for the PDF"""
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=12,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica'
        )
        
        self.small_style = ParagraphStyle(
            'CustomSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Helvetica'
        )
    
    def generate_daily_diary_pdf(self, data: DailyDiaryData) -> bytes:
        """
        Generate Daily Diary PDF from structured data
        
        Args:
            data: DailyDiaryData object with all required information
            
        Returns:
            bytes: PDF document as bytes
        """
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create PDF document with custom page template
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Build PDF content
            story = []
            
            # Add header section
            story.extend(self._create_header_section(data))
            
            # Add project information section
            story.extend(self._create_project_info_section(data))
            
            # Add date and weather section
            story.extend(self._create_date_weather_section(data))
            
            # Add activities section
            story.extend(self._create_activities_section(data))
            
            # Add equipment section
            story.extend(self._create_equipment_section(data))
            
            # Add personnel section
            story.extend(self._create_personnel_section(data))
            
            # Add unsafe acts section
            story.extend(self._create_unsafe_acts_section(data))
            
            # Add additional information sections
            story.extend(self._create_additional_info_section(data))
            
            # Add signatures section
            story.extend(self._create_signatures_section(data))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            raise Exception(f"Error generating PDF: {str(e)}")
    
    def _create_header_section(self, data: DailyDiaryData) -> List:
        """Create header section with company info"""
        elements = []
        
        # Company header table
        header_data = [
            ['NICHOLAS O\'DWYER', 'Company Name:', '', 'in Jv with'],
            ['', 'Unit E4, Nutgrove Office Park,', '', ''],
            ['', 'Nutgrove Avenue, Dublin 14', '', ''],
            ['', 'T +353 1 296 9000', '', ''],
            ['', 'F +353 1 296 9001', '', ''],
            ['', 'E dublin@nodwyer.com', '', ''],
            ['', 'W www.nodwyer.com', '', 'MS Consultancy']
        ]
        
        header_table = Table(header_data, colWidths=[40*mm, 60*mm, 40*mm, 40*mm])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 10))
        
        # Title and document info
        title_data = [
            ['Title: Daily Diary', 'Document No:', 'Page No. of']
        ]
        
        title_table = Table(title_data, colWidths=[60*mm, 60*mm, 60*mm])
        title_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        elements.append(title_table)
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_project_info_section(self, data: DailyDiaryData) -> List:
        """Create project information section"""
        elements = []
        
        # Project info headers
        header_data = [
            ['PROJECT', 'EMPLOYER', 'CONSULTANT', 'CONTRACTOR']
        ]
        
        header_table = Table(header_data, colWidths=[45*mm, 45*mm, 45*mm, 45*mm])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        
        elements.append(header_table)
        
        # Project info data
        info_data = [
            [data.project or '', data.employer or '', data.consultant or '', data.contractor or '']
        ]
        
        info_table = Table(info_data, colWidths=[45*mm, 45*mm, 45*mm, 45*mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_date_weather_section(self, data: DailyDiaryData) -> List:
        """Create date and weather information section"""
        elements = []
        
        # Date section
        morning_check = '✓' if data.time_morning else ''
        afternoon_check = '✓' if data.time_afternoon else ''
        
        date_data = [
            [f'1. Date: {data.date or ""}', f'Time: Morning {morning_check}', f'Afternoon {afternoon_check}']
        ]
        
        date_table = Table(date_data, colWidths=[60*mm, 60*mm, 60*mm])
        date_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        elements.append(date_table)
        
        # Weather section
        weather_data = [
            [f'2. Weather condition: {data.weather_condition or ""}']
        ]
        
        weather_table = Table(weather_data, colWidths=[180*mm])
        weather_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        elements.append(weather_table)
        elements.append(Spacer(1, 5))
        
        return elements
    
    def _create_activities_section(self, data: DailyDiaryData) -> List:
        """Create major activities section"""
        elements = []
        
        # Activities header
        activities_header = [
            ['3. Major Activities on progress, Chain age and Location']
        ]
        
        activities_header_table = Table(activities_header, colWidths=[180*mm])
        activities_header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        elements.append(activities_header_table)
        
        # Activities table header
        activities_table_header = [
            ['sn', 'Description/Topic - Contractor\'s work']
        ]
        
        activities_table_header_table = Table(activities_table_header, colWidths=[20*mm, 160*mm])
        activities_table_header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        
        elements.append(activities_table_header_table)
        
        # Activities data
        activities_data = []
        for i in range(6):  # Standard 6 rows
            if i < len(data.activities):
                activity = data.activities[i]
                activities_data.append([
                    str(activity.get('sn', i + 1)),
                    activity.get('description', '')
                ])
            else:
                activities_data.append([str(i + 1), ''])
        
        activities_table = Table(activities_data, colWidths=[20*mm, 160*mm])
        activities_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(activities_table)
        elements.append(Spacer(1, 5))
        
        return elements
    
    def _create_equipment_section(self, data: DailyDiaryData) -> List:
        """Create equipment section"""
        elements = []
        
        # Equipment header
        equipment_header = [
            ['4. Contractor\'s Equipment (dumper truck, excavator, water pump etc.)']
        ]
        
        equipment_header_table = Table(equipment_header, colWidths=[180*mm])
        equipment_header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        elements.append(equipment_header_table)
        
        # Equipment table header
        equipment_table_header = [
            ['sn', 'Equipment', 'NO', 'sn', 'Equipment', 'NO']
        ]
        
        equipment_table_header_table = Table(equipment_table_header, colWidths=[15*mm, 60*mm, 15*mm, 15*mm, 60*mm, 15*mm])
        equipment_table_header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        
        elements.append(equipment_table_header_table)
        
        # Equipment data (split into two columns)
        equipment_data = []
        for i in range(5):  # 5 rows as in original
            left_idx = i
            right_idx = i + 5
            
            left_sn = str(left_idx + 1)
            left_equipment = ''
            left_no = ''
            
            if left_idx < len(data.equipment):
                eq = data.equipment[left_idx]
                left_equipment = eq.get('equipment', '')
                left_no = eq.get('no', '')
            
            right_sn = str(right_idx + 1)
            right_equipment = ''
            right_no = ''
            
            if right_idx < len(data.equipment):
                eq = data.equipment[right_idx]
                right_equipment = eq.get('equipment', '')
                right_no = eq.get('no', '')
            
            equipment_data.append([
                left_sn, left_equipment, left_no,
                right_sn, right_equipment, right_no
            ])
        
        equipment_table = Table(equipment_data, colWidths=[15*mm, 60*mm, 15*mm, 15*mm, 60*mm, 15*mm])
        equipment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('ALIGN', (5, 0), (5, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (4, 0), (4, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(equipment_table)
        elements.append(Spacer(1, 5))
        
        return elements
    
    def _create_personnel_section(self, data: DailyDiaryData) -> List:
        """Create personnel section"""
        elements = []
        
        # Personnel header
        personnel_header = [
            ['5. Contractor\'s Personnel (Foreman, laborer, driver etc.)']
        ]
        
        personnel_header_table = Table(personnel_header, colWidths=[180*mm])
        personnel_header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        elements.append(personnel_header_table)
        
        # Personnel table header
        personnel_table_header = [
            ['sn', 'Personnel', 'No.', 'sn', 'Personnel', 'No.']
        ]
        
        personnel_table_header_table = Table(personnel_table_header, colWidths=[15*mm, 60*mm, 15*mm, 15*mm, 60*mm, 15*mm])
        personnel_table_header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        
        elements.append(personnel_table_header_table)
        
        # Personnel data (split into two columns, 14 rows each side)
        personnel_data = []
        for i in range(14):  # 14 rows as in original
            left_idx = i
            right_idx = i + 14
            
            left_sn = str(left_idx + 1)
            left_personnel = ''
            left_no = ''
            
            if left_idx < len(data.personnel):
                person = data.personnel[left_idx]
                left_personnel = person.get('personnel', '')
                left_no = person.get('no', '')
            
            right_sn = str(right_idx + 1)
            right_personnel = ''
            right_no = ''
            
            if right_idx < len(data.personnel):
                person = data.personnel[right_idx]
                right_personnel = person.get('personnel', '')
                right_no = person.get('no', '')
            
            personnel_data.append([
                left_sn, left_personnel, left_no,
                right_sn, right_personnel, right_no
            ])
        
        personnel_table = Table(personnel_data, colWidths=[15*mm, 60*mm, 15*mm, 15*mm, 60*mm, 15*mm])
        personnel_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('ALIGN', (5, 0), (5, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (4, 0), (4, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(personnel_table)
        elements.append(Spacer(1, 5))
        
        return elements
    
    def _create_unsafe_acts_section(self, data: DailyDiaryData) -> List:
        """Create unsafe acts section"""
        elements = []
        
        # Unsafe acts header
        unsafe_header = [
            ['6. Unsafe Acts / Conditions Observed']
        ]
        
        unsafe_header_table = Table(unsafe_header, colWidths=[180*mm])
        unsafe_header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        elements.append(unsafe_header_table)
        
        # Unsafe acts table header
        unsafe_table_header = [
            ['sn', 'Description of Unsafe Acts']
        ]
        
        unsafe_table_header_table = Table(unsafe_table_header, colWidths=[20*mm, 160*mm])
        unsafe_table_header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        
        elements.append(unsafe_table_header_table)
        
        # Unsafe acts data
        unsafe_data = []
        for i in range(2):  # 2 rows as in original
            if i < len(data.unsafe_acts):
                unsafe_act = data.unsafe_acts[i]
                unsafe_data.append([
                    str(unsafe_act.get('sn', i + 1)),
                    unsafe_act.get('description', '')
                ])
            else:
                unsafe_data.append([str(i + 1), ''])
        
        unsafe_table = Table(unsafe_data, colWidths=[20*mm, 160*mm], rowHeights=[20*mm, 20*mm])
        unsafe_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(unsafe_table)
        elements.append(Spacer(1, 5))
        
        return elements
    
    def _create_additional_info_section(self, data: DailyDiaryData) -> List:
        """Create additional information sections"""
        elements = []
        
        # Near Miss/Accidents/Incidents
        near_miss_data = [
            ['7. Near Miss/Accidents/Incidents:'],
            [data.near_miss or '']
        ]
        
        near_miss_table = Table(near_miss_data, colWidths=[180*mm], rowHeights=[10*mm, 20*mm])
        near_miss_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(near_miss_table)
        
        # Obstruction/Action Plans
        obstruction_data = [
            ['8. Obstruction/Action Plans:'],
            [data.obstruction or '']
        ]
        
        obstruction_table = Table(obstruction_data, colWidths=[180*mm], rowHeights=[10*mm, 20*mm])
        obstruction_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(obstruction_table)
        
        # Engineer's Note
        engineers_note_data = [
            ['9. Engineer\'s Note:'],
            [data.engineers_note or '']
        ]
        
        engineers_note_table = Table(engineers_note_data, colWidths=[180*mm], rowHeights=[10*mm, 25*mm])
        engineers_note_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(engineers_note_table)
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_signatures_section(self, data: DailyDiaryData) -> List:
        """Create signatures section"""
        elements = []
        
        # Signatures table
        signatures_data = [
            ['Prepared by', 'Checked by', 'Approved by'],
            ['Construction Staff', 'Consultant Supervision Staff', 'Consultant Supervision Staff'],
            [f'Name: {data.prepared_by or ""}', f'Name: {data.checked_by or ""}', f'Name: {data.approved_by or ""}'],
            ['Sign:', 'Sign:', 'Sign:']
        ]
        
        signatures_table = Table(signatures_data, colWidths=[60*mm, 60*mm, 60*mm], rowHeights=[10*mm, 10*mm, 15*mm, 15*mm])
        signatures_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ]))
        
        elements.append(signatures_table)
        
        return elements
